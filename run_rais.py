"""
run_rais.py
===========
The same shift-share variants, applied to real data: formal employment in the
27 Brazilian states by CNAE 2.0 section, RAIS 2022-2025.

The simulation in `run_comparison.py` scores every variant against a known
truth. Real data has none, so the questions change. What can still be asked --
and what the applied literature actually argues about -- is how far the
variants disagree *with each other* on the same numbers:

  agreement   each model's competitive effect against a reference (the
              Barff-Knight annual decomposition), by correlation, by RMSE
              relative to the reference's own dispersion, and by how far the
              state-level rankings move;
  weights     base vs. terminal vs. average weights on the same endpoints
              (Fuchs 1959; Stilwell 1969; Ashby 1970; Herzog-Olsen 1977);
  aggregation 18 CNAE sections vs. 5 broad sectors (Houston 1967);
  break       with and without section O, administração pública, whose
              2022-2025 numbers are an artifact of the eSocial transition
              (see rais_data.DROP_DEFAULT) -- the applied demonstration that
              the competitive effect is a residual that absorbs anything;
  inference   which states the three inferential models (Berzeg, the
              full-analogue regression, Knudsen MDI) call significant;
  space       Moran's I of the estimated competitive rates, i.e. whether
              Brazilian formal-employment competitiveness is in fact
              spatially clustered -- the question Nazara-Hewings (2004)
              raise, here with no planted answer.

Outputs (written next to this script):
  results_rais_components.csv    per model x state: components in jobs
  results_rais_agreement.csv     cross-model agreement metrics
  results_rais_spread.csv        per state: the range across the variants
  results_rais_sensitivity.csv   weights, aggregation and series-break tests
  results_rais_significance.csv  which states each inferential model flags
  results_rais_morans_i.csv      spatial autocorrelation of the estimates

Run with: uv run python run_rais.py
"""

import os

import numpy as np
import pandas as pd
from scipy import stats

import rais_data as RD
import ssa_models as M
from brazil_geo import morans_i
from run_comparison import run_all_models

HERE = os.path.dirname(os.path.abspath(__file__))
YEARS = (2022, 2023, 2024, 2025)
REFERENCE = "Dynamic (Barff-Knight)"

# models whose competitive effect is the structure-free (homothetic) one and
# so is not directly comparable with the rest
HOMOTHETIC = ("Esteban", "Arcelus")


# ----------------------------------------------------------------------
def components_table(models, regions):
    rows = []
    for name, est in models.items():
        e = est.set_index("region").reindex(regions)
        for col in (
            "national",
            "mix",
            "competitive",
            "allocation",
            "neighborhood",
            "own_net",
        ):
            if col in e.columns:
                for r in regions:
                    rows.append(
                        {
                            "model": name,
                            "region": r,
                            "component": col,
                            "jobs": e.loc[r, col],
                        }
                    )
    return pd.DataFrame(rows)


def agreement_table(models, regions, reference=REFERENCE):
    """How far does each variant land from the reference decomposition?

    With no ground truth, `nrmse_vs_ref` is the root mean squared difference
    from the reference divided by the reference's own standard deviation: a
    value of 0.3 means the typical disagreement is a third of the spread the
    reference reports across states. `max_rank_shift` is the largest number
    of positions any single state moves between the two rankings.
    """
    ref = models[reference].set_index("region")["competitive"].reindex(regions).values
    rows = []
    for name, est in models.items():
        x = est.set_index("region")["competitive"].reindex(regions).values
        rk_a = pd.Series(ref, index=regions).rank(ascending=False)
        rk_b = pd.Series(x, index=regions).rank(ascending=False)
        rows.append(
            {
                "model": name,
                "target": "homothetic"
                if any(h in name for h in HOMOTHETIC)
                else "full",
                "pearson_vs_ref": stats.pearsonr(x, ref)[0],
                "spearman_vs_ref": stats.spearmanr(x, ref)[0],
                "nrmse_vs_ref": np.sqrt(np.mean((x - ref) ** 2)) / np.std(ref),
                "max_rank_shift": float((rk_a - rk_b).abs().max()),
                "sign_agree": float(np.mean(np.sign(x) == np.sign(ref))),
                "sd_jobs": float(np.std(x)),
            }
        )
    return pd.DataFrame(rows).sort_values("nrmse_vs_ref").reset_index(drop=True)


def spread_table(models, regions):
    """Per state, the range of competitive effects across the full-effect
    variants: the applied size of the choice-of-variant problem."""
    full = {
        n: e.set_index("region")["competitive"].reindex(regions)
        for n, e in models.items()
        if not any(h in n for h in HOMOTHETIC)
    }
    df = pd.DataFrame(full)
    out = pd.DataFrame(
        {
            "region": regions,
            "min_jobs": df.min(axis=1).values,
            "max_jobs": df.max(axis=1).values,
            "median_jobs": df.median(axis=1).values,
            "argmin": df.idxmin(axis=1).values,
            "argmax": df.idxmax(axis=1).values,
        }
    )
    out["range_jobs"] = out["max_jobs"] - out["min_jobs"]
    # a flip = some variant calls the state a winner and another a loser
    out["sign_flips"] = (out["min_jobs"] < 0) & (out["max_jobs"] > 0)
    return out.sort_values("range_jobs", ascending=False).reset_index(drop=True)


# ----------------------------------------------------------------------
def sensitivity_table(regions):
    """Weight choice, sector aggregation and the administração pública break,
    each measured as a departure from a stated baseline."""
    base = RD.load_panel(years=YEARS, level="secao")
    E, secs, W = base["E"], base["sectors"], base["W"]
    rows = []

    def cmp(label, family, a, b):
        rows.append(
            {
                "test": family,
                "variant": label,
                "pearson": stats.pearsonr(a, b)[0],
                "spearman": stats.spearmanr(a, b)[0],
                "nrmse_vs_baseline": np.sqrt(np.mean((a - b) ** 2)) / np.std(b),
                "max_abs_diff_jobs": float(np.abs(a - b).max()),
                "state_max_diff": regions[int(np.argmax(np.abs(a - b)))],
            }
        )

    # --- weights: Fuchs (1959) / Stilwell (1969) / Ashby (1970) -----------
    d_base = M.classic_dunn(E, regions, "base")["competitive"].values
    for w in ("terminal", "average"):
        cmp(
            f"pesos {w}",
            "pesos (base = Dunn pesos-base)",
            M.classic_dunn(E, regions, w)["competitive"].values,
            d_base,
        )

    # --- aggregation: Houston (1967) -------------------------------------
    coarse = RD.load_panel(years=YEARS, level="grande")
    for label, fn in (
        ("Dunn pesos-base", lambda e, s: M.classic_dunn(e, regions, "base")),
        ("Barff-Knight", lambda e, s: M.dynamic_shift_share(e, regions)),
    ):
        cmp(
            f"5 setores vs. 18 seções · {label}",
            "agregação (base = 18 seções)",
            fn(coarse["E"], coarse["sectors"])["competitive"].values,
            fn(E, secs)["competitive"].values,
        )

    # --- the series break: section O -------------------------------------
    withO = RD.load_panel(years=YEARS, level="secao", drop=("T", "U"))
    for label, fn in (
        ("Dunn pesos-base", lambda e, s: M.classic_dunn(e, regions, "base")),
        ("Barff-Knight", lambda e, s: M.dynamic_shift_share(e, regions)),
        ("Nazara-Hewings", lambda e, s: M.nazara_hewings(e, regions, W)),
    ):
        cmp(
            f"com administração pública · {label}",
            "quebra de série (base = sem seção O)",
            fn(withO["E"], withO["sectors"])["competitive"].values,
            fn(E, secs)["competitive"].values,
        )
    return pd.DataFrame(rows)


def moran_table(models, data, n_perm=999):
    """Moran's I of each model's implied competitive RATE.

    As in the simulation, the test has to run on rates: employment-unit
    levels are dominated by state size, so São Paulo's residual swamps the
    geography. Rate = competitive jobs / employment-years.
    """
    regions, W = data["regions"], data["W"]
    T = data["n_years"]
    w_r = data["E"][:, :, :T].sum(axis=(1, 2))
    rows = []
    # observed total growth rate, for reference: is the raw geography clustered?
    g_obs = data["E"][:, :, -1].sum(1) / data["E"][:, :, 0].sum(1) - 1.0
    I, p = morans_i(g_obs, W, n_perm)
    rows.append({"series": "crescimento total observado", "morans_I": I, "p_value": p})
    for name, est in models.items():
        lvl = est.set_index("region")["competitive"].reindex(regions).values
        I, p = morans_i(lvl / w_r, W, n_perm)
        rows.append({"series": name + " [rate]", "morans_I": I, "p_value": p})
    # the warning from the simulation, reproduced on real data
    lvl = models[REFERENCE].set_index("region")["competitive"].reindex(regions).values
    I, p = morans_i(lvl, W, n_perm)
    rows.append({"series": f"{REFERENCE} [nível]", "morans_I": I, "p_value": p})
    return pd.DataFrame(rows)


def significance_table(models, regions):
    """Which states each inferential model calls significant at 5%."""
    rows = []
    for name, est in models.items():
        if "significant_5pct" not in est.columns:
            continue
        e = est.set_index("region").reindex(regions)
        sig = e["significant_5pct"].astype(bool)
        rows.append(
            {
                "model": name,
                "n_significant": int(sig.sum()),
                "share_significant": float(sig.mean()),
                "significant_states": " ".join(sorted(np.array(regions)[sig.values])),
            }
        )
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------
def main():
    data = RD.load_panel(years=YEARS, level="secao")
    E, regions = data["E"], data["regions"]
    tot = E.sum(axis=(0, 1))
    print(
        f"RAIS {YEARS[0]}-{YEARS[-1]}: {E.shape[0]} UFs x {E.shape[1]} seções CNAE, "
        f"{tot[0]:,.0f} -> {tot[-1]:,.0f} vínculos ativos "
        f"({tot[-1] / tot[0] - 1:+.1%})"
    )

    models = run_all_models(data)

    comp = components_table(models, regions)
    comp.to_csv(os.path.join(HERE, "results_rais_components.csv"), index=False)

    agree = agreement_table(models, regions)
    agree.to_csv(os.path.join(HERE, "results_rais_agreement.csv"), index=False)
    print("\n--- concordância com", REFERENCE, "---")
    print(
        agree[["model", "pearson_vs_ref", "nrmse_vs_ref", "max_rank_shift"]].to_string(
            index=False
        )
    )

    spread = spread_table(models, regions)
    spread.to_csv(os.path.join(HERE, "results_rais_spread.csv"), index=False)
    print("\n--- amplitude entre variantes (5 maiores) ---")
    print(
        spread.head(5)[["region", "median_jobs", "range_jobs", "argmin", "argmax"]]
        .round(0)
        .to_string(index=False)
    )

    sens = sensitivity_table(regions)
    sens.to_csv(os.path.join(HERE, "results_rais_sensitivity.csv"), index=False)
    print("\n--- sensibilidade ---")
    print(
        sens[
            ["test", "variant", "spearman", "nrmse_vs_baseline", "state_max_diff"]
        ].to_string(index=False)
    )

    sig = significance_table(models, regions)
    sig.to_csv(os.path.join(HERE, "results_rais_significance.csv"), index=False)
    print("\n--- inferência ---")
    print(sig[["model", "n_significant", "share_significant"]].to_string(index=False))

    mor = moran_table(models, data)
    mor.to_csv(os.path.join(HERE, "results_rais_morans_i.csv"), index=False)
    print("\n--- I de Moran ---")
    print(mor.to_string(index=False))


if __name__ == "__main__":
    main()
