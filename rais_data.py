"""
rais_data.py
============
Real-data counterpart to the artificial economy: formal employment by state
and economic activity, from the RAIS (Relação Anual de Informações Sociais,
Ministério do Trabalho e Emprego), 2022-2025.

The simulation knows the true effects by construction; RAIS does not. What
the real panel adds is the applied situation every paper in the review was
actually written about: 27 states, a sector breakdown, a handful of years,
and no ground truth — so the variants can only be compared with *each other*.

Source
------
Establishment-level public microdata, one record per establishment with its
state, CNAE 2.0 class and count of links active on 31 December:

    ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/<year>/RAIS_ESTAB_PUB.7z

`build()` downloads those archives (~0.5 GB for the four years), streams
them, and writes the small aggregate actually used by the analysis,
`rais_uf_secao.csv` (27 states x 21 CNAE sections x 4 years). That file is
committed, so nothing here needs re-running unless the aggregation changes.

Public API
----------
    build(years, cache_dir)     download + aggregate -> rais_uf_secao.csv
    load_panel(years, level)    -> dict with E (R, I, T+1), regions, sectors, W

`level="secao"` gives the 21 CNAE 2.0 sections; `level="grande"` collapses
them into the five conventional broad sectors (agropecuária, indústria,
construção, comércio, serviços), which is what makes the aggregation-
sensitivity test of Houston (1967) runnable on real numbers.
"""

import os
import urllib.request

import pandas as pd

from brazil_geo import UFS, contiguity_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL_CSV = os.path.join(HERE, "rais_uf_secao.csv")
FTP = "ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/{year}/RAIS_ESTAB_PUB.7z"
YEARS = (2022, 2023, 2024, 2025)

# IBGE two-digit state code -> state abbreviation
UF_BY_CODE = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP",
    "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB",
    "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES",
    "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS",
    "51": "MT", "52": "GO", "53": "DF",
}  # fmt: skip

# CNAE 2.0 sections: letter -> (short label, first division, last division)
SECOES = {
    "A": ("Agropecuária", 1, 3),
    "B": ("Extrativa", 5, 9),
    "C": ("Transformação", 10, 33),
    "D": ("Eletricidade e gás", 35, 35),
    "E": ("Água e resíduos", 36, 39),
    "F": ("Construção", 41, 43),
    "G": ("Comércio", 45, 47),
    "H": ("Transporte", 49, 53),
    "I": ("Alojamento e alimentação", 55, 56),
    "J": ("Informação e comunicação", 58, 63),
    "K": ("Financeiro e seguros", 64, 66),
    "L": ("Imobiliárias", 68, 68),
    "M": ("Profissionais e técnicas", 69, 75),
    "N": ("Administrativas", 77, 82),
    "O": ("Administração pública", 84, 84),
    "P": ("Educação", 85, 85),
    "Q": ("Saúde e serviços sociais", 86, 88),
    "R": ("Artes e recreação", 90, 93),
    "S": ("Outros serviços", 94, 96),
    "T": ("Serviços domésticos", 97, 97),
    "U": ("Organismos internacionais", 99, 99),
}

# the five conventional broad sectors used in RAIS/CAGED releases
GRANDES = {
    "Agropecuária": ["A"],
    "Indústria": ["B", "C", "D", "E"],
    "Construção": ["F"],
    "Comércio": ["G"],
    "Serviços": ["H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U"],
}

# Sections excluded from the headline panel.
#
# O (administração pública) is a series break, not an economy: from base year
# 2023 the whole RAIS is collected through eSocial, and the technical note for
# RAIS 2023 records the re-labelling of public employment types that followed
# (statutory links -907,224 / -15.4%; links under municipal-law contracts
# +927,463 / +260.7%). State-level growth in section O between 2022 and 2025 is
# correspondingly impossible as economics: +176% in DF, +110% in RR, -9% in SP.
# Shift-share cannot tell a coverage break from a competitive gain -- it is an
# identity, so whatever happened lands in the competitive residual. The default
# panel therefore leaves section O out, and `run_rais.py` runs the comparison
# again with it in, to show exactly how much of the residual it manufactures.
#
# T (serviços domésticos: 1,283 links nationally) and U (organismos
# internacionais: 2,319) are too small to carry a growth rate and are empty in
# 14 and 44 state-year cells respectively.
DROP_DEFAULT = ("O", "T", "U")

_DIV_TO_SECAO = {
    f"{d:02d}": letter
    for letter, (_, lo, hi) in SECOES.items()
    for d in range(lo, hi + 1)
}


# ----------------------------------------------------------------------
# building the aggregate (only needed to refresh rais_uf_secao.csv)
# ----------------------------------------------------------------------
def _download(year, cache_dir):
    dest = os.path.join(cache_dir, str(year), "RAIS_ESTAB_PUB.7z")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if not os.path.exists(dest):
        urllib.request.urlretrieve(FTP.format(year=year), dest)
    return dest


def _extract(archive, cache_dir, year):
    import py7zr

    out = os.path.join(cache_dir, f"x{year}")
    os.makedirs(out, exist_ok=True)
    existing = [f for f in os.listdir(out) if f.lower().endswith((".txt", ".comt"))]
    if not existing:
        with py7zr.SevenZipFile(archive, "r") as z:
            z.extractall(path=out)
        existing = [f for f in os.listdir(out) if f.lower().endswith((".txt", ".comt"))]
    return os.path.join(out, existing[0])


def _dialect(txt_path):
    """Two layouts ship under the same name on the FTP: up to RAIS 2022 a
    semicolon-separated file whose CNAE column holds the 5-digit class, from
    RAIS 2023 a quoted comma-separated one whose columns carry a
    "- Código" suffix and whose CNAE column holds the 7-digit subclass. Both
    are latin-1 and both have `UF` and `Qtd Vínculos Ativos`.
    """
    with open(txt_path, "rb") as f:
        header = f.readline().decode("latin-1")
    sep = "," if header.lstrip().startswith('"') else ";"
    names = [c.strip().strip('"') for c in header.rstrip("\r\n").split(sep)]
    uf = next(c for c in names if c.split(" - ")[0] == "UF")
    cnae = next(c for c in names if c.split(" - ")[0] == "CNAE 2.0 Classe")
    width = 7 if " - " in cnae else 5  # subclass vs. class
    return sep, uf, cnae, width


def aggregate(txt_path, year, chunksize=2_000_000):
    """Stream the establishment file and sum active links by state x section.

    One row per establishment; `Qtd Vínculos Ativos` counts links active on
    31 December. Establishments with an unusable state code or CNAE (a few
    thousand links out of ~53 million, from malformed records) are dropped
    and reported.
    """
    sep, c_uf, c_cnae, width = _dialect(txt_path)
    keep = (c_uf, c_cnae, "Qtd Vínculos Ativos")
    parts, n_rows, n_links = [], 0, 0.0
    reader = pd.read_csv(
        txt_path,
        sep=sep,
        encoding="latin-1",
        chunksize=chunksize,
        usecols=lambda c: c.strip() in keep,
        dtype=str,
        on_bad_lines="warn",
    )
    for ch in reader:
        ch.columns = [c.strip() for c in ch.columns]
        n_rows += len(ch)
        v = pd.to_numeric(ch["Qtd Vínculos Ativos"], errors="coerce").fillna(0.0)
        n_links += float(v.sum())
        uf = ch[c_uf].str.strip().map(UF_BY_CODE)
        div = ch[c_cnae].str.strip().str.zfill(width).str[:2]
        part = pd.DataFrame(
            {"uf": uf, "secao": div.map(_DIV_TO_SECAO), "vinculos": v}
        ).dropna()
        parts.append(part.groupby(["uf", "secao"], as_index=False)["vinculos"].sum())

    g = pd.concat(parts).groupby(["uf", "secao"], as_index=False)["vinculos"].sum()
    g["ano"] = year
    lost = n_links - g["vinculos"].sum()
    print(
        f"RAIS {year}: {n_rows:,} estabelecimentos, "
        f"{int(g['vinculos'].sum()):,} vínculos ativos "
        f"({lost:,.0f} descartados, {lost / n_links:.5%})"
    )
    return g[["ano", "uf", "secao", "vinculos"]]


def build(years=YEARS, cache_dir=None, out=PANEL_CSV):
    """Download, extract and aggregate the RAIS establishment files.

    cache_dir holds the ~0.5 GB of archives and the ~2 GB per-year text
    files; it is not part of the repository. Defaults to ./_rais_cache.
    """
    cache_dir = cache_dir or os.path.join(HERE, "_rais_cache")
    frames = []
    for year in years:
        txt = _extract(_download(year, cache_dir), cache_dir, year)
        frames.append(aggregate(txt, year))
    panel = pd.concat(frames, ignore_index=True)
    # every state x section x year cell present, zeros made explicit
    full = pd.MultiIndex.from_product(
        [sorted(panel["ano"].unique()), UFS, sorted(SECOES)],
        names=["ano", "uf", "secao"],
    )
    panel = (
        panel.set_index(["ano", "uf", "secao"])
        .reindex(full, fill_value=0.0)
        .reset_index()
    )
    panel["vinculos"] = panel["vinculos"].astype("int64")
    panel.to_csv(out, index=False)
    print(f"Saved: {out} ({len(panel)} linhas)")
    return panel


# ----------------------------------------------------------------------
# loading the aggregate for the shift-share models
# ----------------------------------------------------------------------
def load_panel(
    years=(2022, 2025), level="secao", drop=DROP_DEFAULT, min_cell=0, path=PANEL_CSV
):
    """Build the (R, I, T+1) employment array the models in ssa_models expect.

    years    the years to stack, in order; (2022, 2025) is the two-point
             comparison, (2022, 2023, 2024, 2025) the annual panel the
             dynamic and inferential variants need.
    level    "secao" (CNAE 2.0 sections) or "grande" (broad sectors).
    drop     CNAE sections to exclude before aggregating; defaults to
             DROP_DEFAULT ("O", "T", "U") for the reason documented there.
             Pass () to keep all 21.
    min_cell drop sectors whose smallest state-year cell is below this
             (e.g. 1 keeps only sectors present everywhere, which the
             Poisson/MDI model needs because its offset is ln E0).

    Returns a dict shaped like ssa_dgp.generate_dataset's, minus `truth`.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} not found - run `uv run python rais_data.py build` first."
        )
    df = pd.read_csv(path, dtype={"uf": str, "secao": str})
    df = df[df["ano"].isin(years)]
    missing = set(years) - set(df["ano"].unique())
    if missing:
        raise ValueError(f"years not in {os.path.basename(path)}: {sorted(missing)}")
    drop = tuple(drop or ())
    if drop:
        df = df[~df["secao"].isin(drop)]

    if level == "grande":
        to_grande = {s: g for g, ss in GRANDES.items() for s in ss if s not in drop}
        df["setor"] = df["secao"].map(to_grande)
        labels = [g for g in GRANDES if any(s not in drop for s in GRANDES[g])]
    elif level == "secao":
        df["setor"] = df["secao"]
        labels = [s for s in sorted(SECOES) if s not in drop]
    else:
        raise ValueError(level)

    wide = (
        df.groupby(["ano", "uf", "setor"], as_index=False)["vinculos"]
        .sum()
        .pivot(index=["uf", "setor"], columns="ano", values="vinculos")
        .reindex(
            pd.MultiIndex.from_product([UFS, labels], names=["uf", "setor"]),
            fill_value=0.0,
        )
    )
    E = wide[list(years)].to_numpy(dtype=float).reshape(len(UFS), len(labels), -1)

    if min_cell > 0:
        keep = E.min(axis=(0, 2)) >= min_cell
        dropped = [s for s, k in zip(labels, keep) if not k]
        if dropped:
            print(f"Setores descartados (célula < {min_cell}): {dropped}")
        E, labels = E[:, keep, :], [s for s, k in zip(labels, keep) if k]

    return {
        "E": E,
        "regions": list(UFS),
        "sectors": labels,
        "sector_labels": {k: SECOES[k][0] for k in labels} if level == "secao" else {},
        "W": contiguity_matrix(row_standardize=True),
        "years": list(years),
        "n_years": len(years) - 1,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "build":
        build()
    else:
        d = load_panel(years=YEARS)
        E = d["E"]
        print(f"Painel: {E.shape[0]} UFs x {E.shape[1]} seções x {E.shape[2]} anos")
        for k, y in enumerate(d["years"]):
            print(f"  {y}: {E[:, :, k].sum():,.0f} vínculos ativos")
