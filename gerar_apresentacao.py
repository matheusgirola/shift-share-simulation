"""
gerar_apresentacao.py
=====================
Build the slide presentation (in Portuguese) that walks through the
methodological note and puts, for every shift-share variant, the TRUE
component from the DGP side by side with the model's estimate, state by
state (seed 42), followed by the Monte Carlo, Moran's I and significance
summaries.

The estimates come from re-running seed 42 (same call as run_comparison.py);
the recovery metrics, Monte Carlo summary and Moran's I are read from the
results_*.csv files, so run run_comparison.py first if the models changed.

Outputs (written next to this script):
  apresentacao_shift_share.html   standalone deck: arrow keys / click to
                                  navigate, N toggles speaker notes
  --pdf                           also write apresentacao_shift_share.pdf
                                  (one page per slide, needs Chrome)
  --deck DIR                     also write the Slides-artifact files
                                  (DIR/project/deck.json, DIR/project/slides/)

Run with: uv run python gerar_apresentacao.py [--pdf] [--deck DIR]
"""

import argparse
import json
import math
import os
import re
import shutil
import subprocess
from datetime import UTC, datetime

import pandas as pd

import run_comparison as RC
from ssa_dgp import generate_dataset

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#1C2733"
BG = "#F6F4EE"
CARD = "#FDFCF8"
SOFT = "#4A5563"
MUTED = "#5E6773"
RULE = "#DAD6CC"
BLUE = "#2B63A6"
ORANGE = "#C9681A"
SERIF = "'Source Serif 4', Georgia, serif"
SANS = "'IBM Plex Sans', Arial, sans-serif"
MONO = "'IBM Plex Mono', 'Courier New', monospace"
SYS = "-apple-system, 'Helvetica Neue', Arial, sans-serif"

TITLE = "Evolução do Shift-Share: verdade vs. estimativa"
FACES = {
    "source-serif-4": {
        "family": "Source Serif 4",
        "href": "https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400..700&display=swap",
    },
    "ibm-plex-sans": {
        "family": "IBM Plex Sans",
        "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&display=swap",
    },
    "ibm-plex-mono": {
        "family": "IBM Plex Mono",
        "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400&display=swap",
    },
}

NAMES = {
    "Classic Dunn (base wts)": "Dunn, pesos-base",
    "Classic Dunn (terminal wts)": "Dunn, pesos terminais",
    "Classic Dunn (avg wts, Fuchs)": "Dunn, média (Fuchs)",
    "Esteban-Marquillas (static)": "Esteban-Marquillas",
    "Arcelus I (static)": "Arcelus I",
    "Arcelus II (static)": "Arcelus II",
    "Dynamic (Barff-Knight)": "Barff-Knight",
    "Dynamic Esteban-Marquillas": "E-M dinâmico",
    "Berzeg ANOVA (stochastic)": "Berzeg ANOVA",
    "Full-analogue regression": "Full-analogue",
    "Knudsen MDI (static)": "Knudsen estático",
    "Knudsen MDI (dynamic)": "Knudsen dinâmico",
    "Nazara-Hewings spatial (static)": "Nazara-Hewings est.",
    "Nazara-Hewings spatial (dynamic)": "Nazara-Hewings din.",
}


# ----------------------------------------------------------------------
# data
# ----------------------------------------------------------------------
def collect_rais():
    """Everything the real-data slides need, recomputed from rais_uf_secao.csv.

    Mirrors run_rais.main() but keeps the tables in memory, so the deck and
    the CSVs can never drift apart.
    """
    import warnings

    from statsmodels.tools.sm_exceptions import SingularMatrixWarning

    import rais_data as RD
    import run_rais as RR
    import ssa_models as M

    panel = RD.load_panel(years=RR.YEARS, level="secao")
    E, regs = panel["E"], panel["regions"]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SingularMatrixWarning)
        models = RR.run_all_models(panel)

    # the series break: the same model with and without administração pública
    with_o = RD.load_panel(years=RR.YEARS, level="secao", drop=("T", "U"))
    bk_sem = M.dynamic_shift_share(E, regs)["competitive"].to_numpy()
    bk_com = M.dynamic_shift_share(with_o["E"], regs)["competitive"].to_numpy()
    all_sec = RD.load_panel(years=RR.YEARS, level="secao", drop=())
    Ea = all_sec["E"]
    g_o = (
        Ea[:, all_sec["sectors"].index("O"), -1]
        / Ea[:, all_sec["sectors"].index("O"), 0]
        - 1.0
    )

    tot = E.sum(axis=(0, 1))
    bk = models[RR.REFERENCE].set_index("region").reindex(regs)
    spread = RR.spread_table(models, regs).set_index("region").reindex(regs)
    return {
        "regions": regs,
        "years": list(RR.YEARS),
        "n_sectors": E.shape[1],
        "totals": [float(v) for v in tot],
        "growth": float(tot[-1] / tot[0] - 1),
        "competitive": {
            name: est.set_index("region").reindex(regs)["competitive"].tolist()
            for name, est in models.items()
        },
        "mix": bk["mix"].tolist(),
        "national": bk["national"].tolist(),
        "sig": {
            name: est.set_index("region")
            .reindex(regs)["significant_5pct"]
            .astype(bool)
            .tolist()
            for name, est in models.items()
            if "significant_5pct" in est.columns
        },
        "break_sem": bk_sem.tolist(),
        "break_com": bk_com.tolist(),
        "break_o_growth": {r: float(v) for r, v in zip(regs, g_o)},
        "spread": {
            k: spread[k].tolist()
            for k in ("min_jobs", "max_jobs", "median_jobs", "sign_flips")
        },
        "agreement": RR.agreement_table(models, regs).to_dict("records"),
        "sensitivity": RR.sensitivity_table(regs).to_dict("records"),
        "significance": RR.significance_table(models, regs)
        .set_index("model")
        .to_dict("index"),
        "moran": RR.moran_table(models, panel).to_dict("records"),
    }


def collect():
    """Seed-42 truth and estimates per state, plus the saved result tables."""
    data = generate_dataset(seed=42, rho_space=0.5)
    models = RC.run_all_models(data)
    truth = data["truth"].set_index("region")
    regs = list(truth.index)
    est = {}
    for name, df in models.items():
        e = df.set_index("region").reindex(regs)
        est[name] = {
            col: e[col].tolist()
            for col in (
                "competitive",
                "allocation",
                "neighborhood",
                "own_net",
                "regional_shift",
                "differential_shift",
            )
            if col in e.columns
        }
        if "significant_5pct" in e.columns:
            est[name]["sig"] = e["significant_5pct"].astype(bool).tolist()
    mc = pd.read_csv(os.path.join(HERE, "results_montecarlo.csv"))
    return {
        "rais": collect_rais(),
        "regions": regs,
        "group": truth["group"].tolist(),
        "truth": {c: truth[c].tolist() for c in truth.columns if c != "group"},
        "est": est,
        "rec": pd.read_csv(os.path.join(HERE, "results_recovery.csv"))
        .set_index("model")
        .to_dict("index"),
        "mc": mc.set_index(["scenario", "model"]).to_dict("index"),
        "moran": pd.read_csv(os.path.join(HERE, "results_morans_i.csv")).to_dict(
            "records"
        ),
        "sigdiag": RC.significance_diagnostics(models, data)
        .set_index("model")
        .to_dict("index"),
    }


# ----------------------------------------------------------------------
# formatting and charts
# ----------------------------------------------------------------------
def br(x, nd=3):
    s = f"{x:.{nd}f}".replace(".", ",")
    return s.replace("-", "−")


def pct(x):
    return f"{round(100 * x)}%"


def nice_step(span, target=6):
    raw = span / target
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if m * mag >= raw:
            return m * mag
    return 10 * mag


def panel_svg(x0, y0, w, h, title, labels, truth, est, sig=None):
    """Grouped bars true vs estimated, sorted by the truth (thousand jobs)."""
    order = sorted(range(len(labels)), key=lambda i: -truth[i])
    t = [truth[i] / 1000 for i in order]
    e = [est[i] / 1000 for i in order]
    lab = [labels[i] for i in order]
    sg = [sig[i] for i in order] if sig else None
    lo = min(0, min(t), min(e))
    hi = max(0, max(t), max(e))
    step = nice_step(hi - lo)
    lo = math.floor(lo / step) * step
    hi = math.ceil(hi / step) * step
    left, top, bottom = 96, 52, 70
    pw, ph = w - left - 8, h - top - bottom
    px0, py0 = x0 + left, y0 + top

    def Y(v):
        return py0 + ph * (hi - v) / (hi - lo)

    out = [
        f'<text x="{x0}" y="{y0 + 30}" font-size="26" font-weight="600" fill="{INK}">{title}</text>'
    ]
    v = lo
    while v <= hi + 1e-9:
        yy = Y(v)
        col = "#8A8F96" if abs(v) < 1e-9 else RULE
        sw = 2 if abs(v) < 1e-9 else 1
        out.append(
            f'<line x1="{px0}" x2="{px0 + pw}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>'
        )
        lbl = f"{v:,.0f}".replace(",", ".").replace("-", "−")
        out.append(
            f'<text x="{px0 - 10}" y="{yy + 8:.1f}" font-size="24" text-anchor="end" fill="{MUTED}">{lbl}</text>'
        )
        v += step
    n = len(lab)
    gw = pw / n
    bw = gw * 0.38
    for k in range(n):
        gx = px0 + k * gw
        for j, (val, colr) in enumerate(((t[k], BLUE), (e[k], ORANGE))):
            bx = gx + gw * 0.1 + j * bw
            ya, yb = Y(max(val, 0)), Y(min(val, 0))
            hgt = max(yb - ya, 1)
            if j == 1 and sg is not None and not sg[k]:
                out.append(
                    f'<rect x="{bx + 1:.1f}" y="{ya:.1f}" width="{bw - 2:.1f}" height="{hgt:.1f}" fill="{BG}" stroke="{ORANGE}" stroke-width="2"/>'
                )
            else:
                out.append(
                    f'<rect x="{bx:.1f}" y="{ya:.1f}" width="{bw:.1f}" height="{hgt:.1f}" fill="{colr}"/>'
                )
        # two staggered rows of state labels so neighbouring codes don't touch
        ly = y0 + h - (34 if k % 2 == 0 else 6)
        out.append(
            f'<text x="{gx + gw / 2:.1f}" y="{ly}" font-size="23" text-anchor="middle" fill="{INK}">{lab[k]}</text>'
        )
    return "".join(out)


def legend_svg(y, sig=False, items=None):
    """items: (colour, text, hollow) triples; the default pair is the
    simulation's truth-vs-estimate reading."""
    if items is None:
        items = [
            (BLUE, "Verdadeiro (DGP)", False),
            (ORANGE, "Estimado pelo modelo", False),
        ]
        if sig:
            items.append((ORANGE, "Estimado, não signif. a 5%", True))
    out, x = [], 96
    for colr, txt, hollow in items:
        if hollow:
            out.append(
                f'<rect x="{x + 1}" y="{y - 19}" width="22" height="22" fill="{BG}" stroke="{colr}" stroke-width="2"/>'
            )
        else:
            out.append(
                f'<rect x="{x}" y="{y - 20}" width="24" height="24" fill="{colr}"/>'
            )
        out.append(
            f'<text x="{x + 34}" y="{y}" font-size="24" fill="{INK}">{txt}</text>'
        )
        x += 34 + int(len(txt) * 13.2) + 40
    return "".join(out)


def embed(svg_body, w, h, left, top):
    """A pinned live embed holding a static SVG (the Slides format draws
    charts this way; the standalone HTML unwraps it into a plain div)."""
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'font-family="{SYS}">{svg_body}</svg>'
    )
    page = f'<meta charset="utf-8"><body style="margin:0;background:{BG}">{svg}</body>'
    assert len(page.encode()) < 16000, len(page.encode())
    return f'<x-embed style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px">{page}</x-embed>'


CH_W, CH_H, CH_L, CH_T = 1056, 800, 736, 104


def single_chart(title, labels, truth, est, sig=None, legend=None):
    body = legend_svg(30, sig is not None, legend) + panel_svg(
        0, 56, CH_W, CH_H - 56, title, labels, truth, est, sig
    )
    return embed(body, CH_W, CH_H, CH_L, CH_T)


def double_chart(p1, p2):
    hh = (CH_H - 56) // 2
    body = (
        legend_svg(30)
        + panel_svg(0, 56, CH_W, hh - 8, *p1)
        + panel_svg(0, 56 + hh + 8, CH_W, hh - 8, *p2)
    )
    return embed(body, CH_W, CH_H, CH_L, CH_T)


def hbar_chart(rows, w, h, left, top, xmax, ticks, fmt, legend, ref=None):
    """rows: (label, [(value, color)]) -> grouped horizontal bars."""
    lab_w, top_m, bot = 470, 56, 40
    pw = w - lab_w - 70
    rh = (h - top_m - bot) / len(rows)
    out = []
    x = lab_w
    for colr, txt in legend:
        out.append(f'<rect x="{x}" y="10" width="24" height="24" fill="{colr}"/>')
        out.append(
            f'<text x="{x + 34}" y="30" font-size="24" fill="{INK}">{txt}</text>'
        )
        x += 34 + int(len(txt) * 13.2) + 40

    def X(v):
        return lab_w + pw * v / xmax

    for tv in ticks:
        out.append(
            f'<line x1="{X(tv):.1f}" x2="{X(tv):.1f}" y1="{top_m}" y2="{h - bot}" stroke="{RULE}"/>'
        )
        out.append(
            f'<text x="{X(tv):.1f}" y="{h - 8}" font-size="24" text-anchor="middle" fill="{MUTED}">{fmt(tv)}</text>'
        )
    if ref is not None:
        out.append(
            f'<line x1="{X(ref):.1f}" x2="{X(ref):.1f}" y1="{top_m - 6}" y2="{h - bot}" stroke="{BLUE}" stroke-width="3" stroke-dasharray="8 6"/>'
        )
    for k, (name, bars) in enumerate(rows):
        y = top_m + k * rh
        out.append(
            f'<text x="{lab_w - 14}" y="{y + rh / 2 + 8:.1f}" font-size="24" text-anchor="end" fill="{INK}">{name}</text>'
        )
        bh = (rh * 0.72) / len(bars)
        for j, (val, colr) in enumerate(bars):
            by = y + rh * 0.14 + j * bh
            out.append(
                f'<rect x="{lab_w}" y="{by:.1f}" width="{max(X(val) - lab_w, 1):.1f}" height="{bh - 2:.1f}" fill="{colr}"/>'
            )
            out.append(
                f'<text x="{X(val) + 8:.1f}" y="{by + bh / 2 + 7:.1f}" font-size="22" fill="{INK}">{fmt(val)}</text>'
            )
    return embed("".join(out), w, h, left, top)


# ----------------------------------------------------------------------
# slide templates
# ----------------------------------------------------------------------
def footer(n, source=None):
    src = source or (
        "Simulação semente 42 · 27 UFs × 5 setores × 10 anos · valores em mil empregos"
    )
    return (
        f'<p style="position:absolute;left:128px;bottom:56px;width:1300px;font-size:24px;color:{MUTED}">'
        f"{src}</p>"
        f'<p style="position:absolute;right:128px;bottom:56px;width:120px;font-size:24px;color:{MUTED};text-align:right">{n}</p>'
    )


RAIS_SOURCE = (
    "RAIS 2022–2025 (MTE/PDET) · 27 UFs × 18 seções CNAE · "
    "valores em mil vínculos ativos"
)


def footer_rais(n):
    return footer(n, RAIS_SOURCE)


def stat(value, label):
    return (
        f'<div style="flex:1;display:flex;flex-direction:column;gap:4px">'
        f'<p style="font-family:{SERIF};font-size:52px;font-weight:600;line-height:1.05;color:{INK}">{value}</p>'
        f'<p style="font-size:24px;line-height:1.25;color:{MUTED}">{label}</p></div>'
    )


def model_slide(
    sid, n, eyebrow, title, desc, formula, stats, extra, chart, notes, source=None
):
    st = "".join(stat(v, lab) for v, lab in stats)
    ex = "".join(
        e
        if e.startswith("<table")
        else f'<p style="font-size:24px;line-height:1.35;color:{SOFT}">{e}</p>'
        for e in extra
    )
    return f"""<section id="{sid}" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:24px">
<div style="width:560px;display:flex;flex-direction:column;gap:22px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">{eyebrow}</p>
<h2 style="font-family:{SERIF};font-size:54px;font-weight:600;line-height:1.08;color:{INK}">{title}</h2>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">{desc}</p>
<p style="font-family:{MONO};font-size:24px;line-height:1.45;color:{INK};background:{CARD};border:1px solid {RULE};border-radius:12px;padding:18px 22px">{formula}</p>
<div style="display:flex;gap:20px;border-top:2px solid {INK};padding:18px 0px 0px 0px">{st}</div>
{ex}
</div>
{chart}
{footer(n, source)}
<aside>{notes}</aside>
</section>"""


# ----------------------------------------------------------------------
# wave dividers (the three waves of reformulation plus the spatial one)
# ----------------------------------------------------------------------
DARK_CARD = "#24313F"
DARK_RULE = "#3A4757"
GOLD = "#E9A867"
PALE = "#C3CBD4"
FAINT = "#8A94A0"


def footer_dark(n, source=None):
    src = source or (
        "Simulação semente 42 · 27 UFs × 5 setores × 10 anos · valores em mil empregos"
    )
    return (
        f'<p style="position:absolute;left:128px;bottom:56px;width:1300px;font-size:24px;color:{FAINT}">'
        f"{src}</p>"
        f'<p style="position:absolute;right:128px;bottom:56px;width:120px;font-size:24px;color:{FAINT};text-align:right">{n}</p>'
    )


def dark_cards(cards):
    return "".join(
        f'<div style="flex:1;display:flex;flex-direction:column;gap:14px;'
        f'background:{DARK_CARD};border-radius:16px;padding:32px">'
        f'<p style="font-size:22px;font-weight:600;letter-spacing:2px;'
        f'text-transform:uppercase;color:{GOLD}">{a}</p>'
        f'<p style="font-size:27px;line-height:1.4;color:{PALE}">{b}</p></div>'
        for a, b in cards
    )


def wave_slide(sid, section, n, eyebrow, title, lead, cards, ahead, notes):
    """Dark divider opening one wave: problem, structural change, remaining limit."""
    return f"""<section id="{sid}" data-transition="fade" data-section="{section}" style="background:{INK};color:{BG};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:32px">
<p style="font-size:26px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:{GOLD}">{eyebrow}</p>
<h2 style="font-family:{SERIF};font-size:68px;font-weight:600;line-height:1.08;color:{BG};width:1520px">{title}</h2>
<p style="font-size:30px;line-height:1.45;color:{PALE};width:1560px">{lead}</p>
<div style="display:flex;gap:24px">{dark_cards(cards)}</div>
<p style="font-size:26px;line-height:1.4;color:{FAINT};border-top:1px solid {DARK_RULE};padding:22px 0px 0px 0px">{ahead}</p>
{footer_dark(n)}
<aside>{notes}</aside>
</section>"""


# ----------------------------------------------------------------------
# real-data slides (RAIS 2022-2025)
# ----------------------------------------------------------------------
def card_grid(cards, columns=3, dark=False):
    bgc = "#24313F" if dark else CARD
    border = "none" if dark else f"1px solid {RULE}"
    h3c, pc = ("#E9A867", "#D5DBE2") if dark else (INK, SOFT)
    inner = "".join(
        f'<div style="display:flex;flex-direction:column;gap:12px;background:{bgc};'
        f'border:{border};border-radius:16px;padding:32px">'
        f'<h3 style="font-size:32px;font-weight:600;color:{h3c}">{a}</h3>'
        f'<p style="font-size:26px;line-height:1.4;color:{pc}">{b}</p></div>'
        for a, b in cards
    )
    return (
        f'<div style="display:grid;grid-template-columns:{"1fr " * columns};'
        f'gap:24px">{inner}</div>'
    )


def table_html(headers, rows, size=30):
    th = "".join(
        f'<th style="width:{w};text-align:{al}">{t}</th>' for t, w, al in headers
    )
    tr = "".join(
        "<tr>"
        + "".join(
            f'<td style="text-align:{al};{"font-weight:600" if k == 0 else ""}">{c}</td>'
            for k, (c, (_, _, al)) in enumerate(zip(r, headers))
        )
        + "</tr>"
        for r in rows
    )
    return (
        f'<table style="font-size:{size}px;color:{INK};padding:14px 18px">'
        f"<tr>{th}</tr>{tr}</table>"
    )


def build_rais_slides(R, n, true_moran):
    """Eight slides: the real panel, the series break, the decomposition, how
    far the variants fall apart, and what survives inference and geography."""
    REGS = R["regions"]
    COMP = R["competitive"]
    AGR = {r["model"]: r for r in R["agreement"]}
    SENS = {(r["test"].split(" (")[0], r["variant"]): r for r in R["sensitivity"]}
    slides = []

    def pp(x, nd=1):
        return br(100 * x, nd) + "%"

    # 1. section opener
    y0, y1 = R["years"][0], R["years"][-1]
    cards = [
        (
            "Concordam?",
            "Sem verdade, resta medir a distância entre as variantes nos mesmos números.",
        ),
        (
            "Do que depende?",
            "Ano de ponderação, nível de agregação setorial, integridade da série.",
        ),
        (
            "Há efeito?",
            "Os modelos inferenciais conseguem distinguir alguma UF de zero?",
        ),
    ]
    slides.append(
        f"""<section id="rais-intro" data-transition="fade" data-section="RAIS 2022–2025" style="background:{BG};color:{INK};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:36px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">Do laboratório ao campo</p>
<h2 style="font-family:{SERIF};font-size:64px;font-weight:600;line-height:1.1">As mesmas treze variantes, agora sem gabarito</h2>
<p style="font-size:30px;line-height:1.4;color:{SOFT};width:1500px">Emprego formal das 27 UFs por seção CNAE 2.0, vínculos ativos em 31/12, microdados de estabelecimentos da RAIS. De <b>{br(R["totals"][0] / 1e6, 1)} milhões</b> de vínculos em {y0} para <b>{br(R["totals"][-1] / 1e6, 1)} milhões</b> em {y1} ({pp(R["growth"], 1)}).</p>
<p style="font-family:{MONO};font-size:30px;color:{INK};background:{CARD};border:1px solid {RULE};border-radius:16px;padding:24px 32px">ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/&lt;ano&gt;/RAIS_ESTAB_PUB.7z → rais_uf_secao.csv</p>
<p style="font-size:28px;line-height:1.45;color:{SOFT}">As três perguntas da simulação (correlação com a verdade, nRMSE, acerto de sinal) deixam de existir. Sobram as perguntas da literatura aplicada:</p>
{card_grid(cards)}
{footer_rais(n)}
<aside>Seção 13 do notebook. O painel usa 18 das 21 seções CNAE: ficam de fora administração pública (quebra de série, slide seguinte), serviços domésticos e organismos internacionais (pequenos demais para carregar uma taxa). O total fica cerca de 1% abaixo dos números oficiais porque a contagem vem do arquivo de estabelecimentos, não do de vínculos.</aside>
</section>"""
    )
    n += 1

    # 2. the series break
    g_o = R["break_o_growth"]
    worst = sorted(g_o, key=lambda r: -g_o[r])[:3]
    sem, com = R["break_sem"], R["break_com"]
    i_sp, i_df = REGS.index("SP"), REGS.index("DF")
    quebra = SENS[("quebra de série", "com administração pública · Barff-Knight")]
    slides.append(
        model_slide(
            "rais-quebra",
            n,
            "RAIS · antes de decompor",
            "A quebra de série vira efeito competitivo",
            "Desde 2023 a RAIS vem do eSocial, e os vínculos públicos foram reclassificados: estatutários −907.224, contratos por lei municipal +927.463. É a mesma pessoa em outra caixa.",
            "A identidade não distingue "
            "<b>ficou competitivo</b> de <b>passou a declarar</b>",
            [
                (br(quebra["spearman"], 2), "Spearman entre as duas versões"),
                (br(quebra["nrmse_vs_baseline"], 2), "nRMSE da inclusão"),
                (
                    br(abs(com[i_sp] - sem[i_sp]) / 1000, 0),
                    "mil vínculos a menos em SP",
                ),
            ],
            [
                "Crescimento da seção O, 2022–2025: "
                + ", ".join(f"{r} {pp(g_o[r], 0)}" for r in worst)
                + f", SP {pp(g_o['SP'], 0)}.",
            ],
            single_chart(
                "Efeito competitivo por UF, Barff-Knight (mil vínculos)",
                REGS,
                sem,
                com,
                legend=[
                    (BLUE, "Sem administração pública", False),
                    (ORANGE, "Com administração pública", False),
                ],
            ),
            f"O DF sai de {br(sem[i_df] / 1000, 0)} para {br(com[i_df] / 1000, 0)} mil "
            "vínculos de “vantagem competitiva”. "
            "O efeito competitivo é um resíduo, e um resíduo absorve o que aparecer — inclusive erro de medida. Nenhuma das treze variantes se defende disso, e as inferenciais tampouco: a quebra é sistemática, não é ruído, e os erros-padrão medem ruído. A triagem que detecta o problema está na seção 13.1 do notebook: dispersão dos crescimentos entre UFs, seção por seção.",
            RAIS_SOURCE,
        )
    )
    n += 1

    # 3. the decomposition as an analyst would read it
    bk = COMP["Dynamic (Barff-Knight)"]
    top = sorted(range(len(REGS)), key=lambda i: -bk[i])[:3]
    bot = sorted(range(len(REGS)), key=lambda i: bk[i])[:3]
    slides.append(
        model_slide(
            "rais-decomp",
            n,
            "RAIS · a decomposição",
            "O efeito nacional domina; o estrutural é pequeno",
            "Barff-Knight anual sobre 2022–2025, a variante mais defensável no Monte Carlo. Em nenhuma UF a composição chega a um quarto do efeito nacional.",
            "ΔE = nacional + estrutural + competitivo",
            [
                (
                    br(R["national"][REGS.index("SP")] / 1e6, 2),
                    "milhões de efeito nacional em SP",
                ),
                (br(bk[REGS.index("SP")] / 1000, 1), "mil de competitivo em SP"),
                (
                    br(max(abs(m) for m in R["mix"]) / 1000, 0),
                    "maior estrutural (mil, RJ)",
                ),
            ],
            [
                "Ganham: "
                + ", ".join(f"{REGS[i]} {br(bk[i] / 1000, 0)}" for i in top)
                + " mil vínculos.",
                "Perdem: "
                + ", ".join(f"{REGS[i]} {br(bk[i] / 1000, 0)}" for i in bot)
                + " mil vínculos.",
            ],
            single_chart(
                "Competitivo e estrutural por UF (mil vínculos)",
                REGS,
                bk,
                R["mix"],
                legend=[
                    (BLUE, "Efeito competitivo", False),
                    (ORANGE, "Efeito estrutural", False),
                ],
            ),
            "A composição setorial das UFs brasileiras é parecida o bastante para que a estrutura explique pouco, apesar de 36 pontos percentuais separarem o setor mais rápido (educação, +39%) do mais lento (agropecuária, +3,4%). É um argumento a favor de desagregar mais, não menos. O competitivo separa Sul e Sudeste consolidado (RS, RJ, PR negativos) do Norte-Nordeste em formalização acelerada.",
            RAIS_SOURCE,
        )
    )
    n += 1

    # 4. how far the variants fall apart
    order = sorted(AGR, key=lambda m: AGR[m]["nrmse_vs_ref"])
    rows = [
        (
            NAMES[m],
            [(min(AGR[m]["nrmse_vs_ref"], 1.5), ORANGE)],
        )
        for m in order
    ]
    term = AGR["Classic Dunn (terminal wts)"]
    slides.append(
        f"""<section id="rais-acordo" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:24px">
<div style="width:440px;display:flex;flex-direction:column;gap:24px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">RAIS · concordância</p>
<h2 style="font-family:{SERIF};font-size:54px;font-weight:600;line-height:1.08">Ordenam igual, mas discordam na magnitude</h2>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">Cada variante contra a decomposição anual de Barff-Knight: RMSE da diferença dividido pelo desvio-padrão da própria referência.</p>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">Pearson entre {br(min(a["pearson_vs_ref"] for a in AGR.values()), 2)} e 1,00 — o <i>ranking</i> das UFs quase não muda. Mas os pesos terminais discordam em {br(term["nrmse_vs_ref"], 2)} desvios-padrão e deslocam uma UF em até {int(term["max_rank_shift"])} posições de 27.</p>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">Berzeg e Nazara-Hewings dinâmico dão o mesmo competitivo total, como a aditividade exige.</p>
</div>
{hbar_chart(rows, 1180, 800, 612, 104, 1.5, [0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5], lambda v: br(v, 2), [(ORANGE, "nRMSE contra Barff-Knight")])}
{footer_rais(n)}
<aside>results_rais_agreement.csv. Esteban-Marquillas, Arcelus I e E-M dinâmico estimam o competitivo homotético, que é outro objeto — a distância deles até a referência não é erro, é definição. A barra dos pesos terminais está truncada em 1,50; o valor é {br(term["nrmse_vs_ref"], 2)}.</aside>
</section>"""
    )
    n += 1

    # 5. the spread, state by state
    SPR = R["spread"]
    flips = [REGS[i] for i, f in enumerate(SPR["sign_flips"]) if f]
    i_sp = REGS.index("SP")
    slides.append(
        model_slide(
            "rais-amplitude",
            n,
            "RAIS · amplitude",
            "Em três UFs, o sinal é escolha do analista",
            "Por UF, a menor e a maior estimativa do efeito competitivo entre as variantes de efeito completo. Onde o efeito é grande, a conclusão de sinal é robusta; onde é próximo de zero, não é.",
            "São Paulo: mediana "
            f"{br(SPR['median_jobs'][i_sp] / 1000, 1)} mil · "
            f"de {br(SPR['min_jobs'][i_sp] / 1000, 1)} a "
            f"{br(SPR['max_jobs'][i_sp] / 1000, 1)} mil",
            [
                (
                    f"{len(flips)} de 27",
                    "UFs em que o sinal muda: " + ", ".join(flips),
                ),
                (
                    br(
                        (SPR["max_jobs"][i_sp] - SPR["min_jobs"][i_sp]) / 1000,
                        0,
                    ),
                    "mil vínculos de amplitude em SP",
                ),
            ],
            [
                (
                    "“São Paulo ganhou ou perdeu competitividade entre 2022 e 2025?” não tem "
                    "resposta nestes dados: a resposta é a variante escolhida."
                ),
                (
                    "MG fica entre "
                    f"{br(SPR['min_jobs'][REGS.index('MG')] / 1000, 0)} e "
                    f"{br(SPR['max_jobs'][REGS.index('MG')] / 1000, 0)} mil, sempre positivo; "
                    "RS, sempre bem negativo."
                ),
            ],
            single_chart(
                "Menor e maior estimativa do competitivo por UF (mil vínculos)",
                REGS,
                SPR["max_jobs"],
                SPR["min_jobs"],
                legend=[
                    (BLUE, "Maior estimativa entre as variantes", False),
                    (ORANGE, "Menor estimativa entre as variantes", False),
                ],
            ),
            "results_rais_spread.csv. São sete estimadores distintos: as variantes homotéticas (Esteban-Marquillas, Arcelus I) ficam fora porque estimam outro objeto, e as quatro que duplicam outra exatamente — Arcelus II e Nazara-Hewings estático reproduzem Dunn pesos-base; Berzeg e Nazara-Hewings dinâmico reproduzem Barff-Knight — são contadas uma vez só, para que a mediana não dependa de quantas vezes a literatura reformula o mesmo estimador. A amplitude de São Paulo vem sobretudo dos pesos terminais, que reponderam a identidade pelo emprego de 2025 — e São Paulo é grande justamente nos setores que cresceram menos.",
            RAIS_SOURCE,
        )
    )
    n += 1

    # 6. inference
    SIG = R["significance"]
    srows = [
        (
            NAMES[m],
            f"{SIG[m]['n_significant']} de 27",
            SIG[m]["significant_states"] or "—",
        )
        for m in (
            "Berzeg ANOVA (stochastic)",
            "Full-analogue regression",
            "Knudsen MDI (static)",
            "Knudsen MDI (dynamic)",
        )
    ]
    pi_vals = [COMP[m][REGS.index("PI")] / 1000 for m in COMP]
    slides.append(
        f"""<section id="rais-infer" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:20px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">RAIS · inferência</p>
<h2 style="font-family:{SERIF};font-size:64px;font-weight:600;line-height:1.1">Quase nenhuma UF se distingue de zero</h2>
{table_html([("Modelo", "34%", "left"), ("UFs signif. 5%", "22%", "right"), ("Quais", "44%", "right")], srows)}
<p style="font-size:28px;line-height:1.45;color:{SOFT}">Na simulação, estes três modelos sinalizavam 100% das UFs de vantagem forte. Nos dados reais, três anos e 18 seções deixam variação intra-UF grande o bastante para que quase todas as diferenças regionais caibam no erro-padrão.</p>
<div style="display:flex;gap:20px;border-top:2px solid {INK};padding:18px 0px 0px 0px">
{stat(br(min(pi_vals), 1) + " a " + br(max(pi_vals), 1), "mil vínculos: o competitivo do PI pelas treze variantes")}
{stat("2,19 a 2,41", "t de Berzeg e das duas formas de Knudsen para o PI")}
{stat("0,98", "t da regressão análoga completa para o PI")}
</div>
<p style="font-size:26px;line-height:1.45;color:{SOFT}">Mesmo no caso mais favorável, os métodos inferenciais não fecham entre si. Sem erro-padrão, os 27 números das variantes determinísticas parecem precisos, e não há como saber que a maioria não se distingue de zero.</p>
{footer_rais(n)}
<aside>results_rais_significance.csv. É o argumento de Berzeg (1978) e de Knudsen (2000) com o sinal invertido em relação à simulação: lá a inferência confirmava o que havia; aqui ela desmente o que parecia haver. O diagnóstico qualitativo do slide da decomposição é, em grande parte, ruído com aparência de resultado.</aside>
</section>"""
    )
    n += 1

    # 7. Moran's I: is competitiveness clustered in Brazil?
    mrows, pmax, pmin = [], 0.0, 1.0
    for row in R["moran"]:
        s = row["series"]
        if s.endswith(" [rate]"):
            lab = NAMES[s[: -len(" [rate]")]]
            pmax, pmin = max(pmax, row["p_value"]), min(pmin, row["p_value"])
        elif s.endswith(" [nível]"):
            lab = "Barff-Knight, em nível"
        else:
            lab = "Crescimento total observado"
        mrows.append(
            (f"{lab} · p = {br(row['p_value'], 2)}", [(row["morans_I"], ORANGE)])
        )
    rates = [r["morans_I"] for r in R["moran"] if r["series"].endswith(" [rate]")]
    slides.append(
        f"""<section id="rais-moran" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:24px">
<div style="width:440px;display:flex;flex-direction:column;gap:24px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">RAIS · espaço</p>
<h2 style="font-family:{SERIF};font-size:54px;font-weight:600;line-height:1.08">Nazara-Hewings não se paga neste recorte</h2>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">I de Moran das taxas competitivas entre {br(min(rates), 2)} e {br(max(rates), 2)}, com p entre {br(pmin, 2)} e {br(pmax, 2)} — nenhum significativo a 10%. A linha tracejada marca o valor verdadeiro da simulação, {br(true_moran, 2)}.</p>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">A competitividade do emprego formal brasileiro não é contagiosa entre vizinhos: MG cresce bem cercado de UFs que não crescem.</p>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">A decomposição espacial continua correta — seu competitivo total é idêntico ao de Dunn — mas o componente de vizinhança não informa nada aqui.</p>
</div>
{hbar_chart(mrows, 1180, 800, 612, 104, 0.7, [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], lambda v: br(v, 2), [(ORANGE, "I de Moran, dados reais")], ref=true_moran)}
{footer_rais(n)}
<aside>results_rais_morans_i.csv, 999 permutações, contiguidade real das UFs. É o cenário no_space da simulação, agora em dados reais: a maquinaria espacial mede corretamente um componente que não carrega informação sobre a vantagem da própria UF. Em recorte municipal, ou com outra matriz W, a resposta pode mudar — a própria advertência de sensibilidade à matriz de pesos. Calculado sobre o competitivo em nível, o I cai ainda mais, porque o tamanho de São Paulo domina.</aside>
</section>"""
    )
    n += 1

    # 8. the hierarchy of fragilities
    agg = SENS[("agregação", "5 setores vs. 18 seções · Dunn pesos-base")]
    wts = SENS[("pesos", "pesos terminal")]
    frows = [
        (
            "Quebra de série (adm. pública)",
            [(min(quebra["nrmse_vs_baseline"], 4.0), ORANGE)],
        ),
        ("Escolha da variante (pior caso)", [(term["nrmse_vs_ref"], ORANGE)]),
        ("Pesos: base → terminal", [(wts["nrmse_vs_baseline"], ORANGE)]),
        ("Agregação: 18 → 5 setores", [(agg["nrmse_vs_baseline"], ORANGE)]),
    ]
    slides.append(
        f"""<section id="rais-fecho" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:24px">
<div style="width:460px;display:flex;flex-direction:column;gap:24px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">RAIS · síntese</p>
<h2 style="font-family:{SERIF};font-size:54px;font-weight:600;line-height:1.08">A decisão mais consequente é a menos discutida</h2>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">Cada barra é o nRMSE que uma escolha do analista produz no efeito competitivo, nos mesmos dados.</p>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">A integridade da série vale uma ordem de grandeza mais do que qualquer refinamento de método — e é a única das quatro que a literatura shift-share quase não discute. Não existe variante que a corrija.</p>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">Depois dela, pesos e variante, na mesma ordem de grandeza que o Monte Carlo indicava.</p>
</div>
{hbar_chart(frows, 1180, 700, 612, 150, 4.0, [0, 1, 2, 3, 4], lambda v: br(v, 2), [(ORANGE, "nRMSE no efeito competitivo")])}
{footer_rais(n)}
<aside>results_rais_sensitivity.csv e results_rais_agreement.csv. A concordância entre variantes não é evidência de acerto: todas podem estar erradas juntas, e no caso da administração pública estavam. O laboratório mostra que os métodos funcionam quando há verdade; a RAIS mostra onde o resultado é frágil quando não há.</aside>
</section>"""
    )
    n += 1
    return slides, n


# ----------------------------------------------------------------------
# slides
# ----------------------------------------------------------------------
def build_slides(D):
    REGS = D["regions"]
    REC, MC, SIG, EST = D["rec"], D["mc"], D["sigdiag"], D["est"]
    T = D["truth"]
    TC, TH = T["true_comp"], T["true_comp_homothetic"]
    TRS = T["true_reg_shift"]
    CT = "Efeito competitivo por UF, ordenado pelo verdadeiro (mil empregos)"
    CTH = "Efeito competitivo homotético por UF (mil empregos)"

    def metrics(model, prefix=""):
        r = REC[model]
        return [
            (br(r[prefix + "pearson"]), "correlação (r)"),
            (br(r[prefix + "nrmse"], 2), "nRMSE"),
            (pct(r[prefix + "sign_acc"]), "sinal correto"),
        ]

    def mc_line(model):
        b = MC[("benign", model)]["nrmse_mean"]
        s = MC[("stress", model)]["nrmse_mean"]
        return (
            f"Monte Carlo, 50 sementes · nRMSE médio <b>{br(b, 2)}</b> no cenário benigno "
            f"e <b>{br(s, 2)}</b> no de estresse."
        )

    def comp(model):
        return EST[model]["competitive"]

    def sig(model):
        return EST[model].get("sig")

    def sig_line(model):
        s = SIG[model]
        k = sum(EST[model]["sig"])
        return (
            f"Teste a 5%: <b>{k} de 27</b> UFs significativas; detecta {pct(s['power_strong_regions'])} "
            f"das UFs de vantagem forte e marca {pct(s['flag_rate_weak_regions'])} das de vantagem fraca."
        )

    def chart(title, truth, est, sg=None):
        return single_chart(title, REGS, truth, est, sg)

    slides = []

    # 1 cover
    slides.append(
        f"""<section id="cover" data-transition="fade" style="background:{INK};color:{BG};font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:space-between">
<p style="font-size:26px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:#E9A867">Nota metodológica · simulação</p>
<div style="display:flex;flex-direction:column;gap:36px">
<h1 style="font-family:{SERIF};font-size:96px;font-weight:600;line-height:1.05;color:{BG};width:1664px">A evolução da análise shift-share</h1>
<p style="font-size:36px;line-height:1.4;color:#C3CBD4;width:1400px">De Dunn (1960) a Nazara-Hewings (2004): o que cada modelo recupera de uma economia artificial cujos efeitos verdadeiros são conhecidos</p>
</div>
<div style="display:flex;gap:48px;border-top:2px solid #3A4757;padding:28px 0px 0px 0px">
<p style="font-size:26px;color:#C3CBD4">13 variantes</p>
<p style="font-size:26px;color:#C3CBD4">27 UFs × 5 setores × 10 anos</p>
<p style="font-size:26px;color:#C3CBD4">Verdadeiro vs. estimado, UF a UF</p>
<p style="font-size:26px;color:#C3CBD4">e o mesmo teste na RAIS 2022–2025</p>
</div>
<aside>Apresentação baseada na nota metodológica (nota_metodologica_shift_share_PT-BR.md) e nos resultados de run_comparison.py. A nota explica cada artigo com um exemplo de cinco UFs do Nordeste; aqui cada modelo é confrontado com a verdade do processo gerador de dados.</aside>
</section>"""
    )

    # 2 the experiment
    cards = [
        ("n[t]", "Efeito nacional", "Taxa de crescimento do país em cada ano."),
        (
            "m[i,t]",
            "Composição setorial",
            "Desvio de cada setor; média ponderada nula.",
        ),
        (
            "c[r,i]",
            "Efeito competitivo",
            "Vantagem comum da UF mais interação UF × setor.",
        ),
        ("ε[r,i,t]", "Ruído", "Choque aleatório que nenhum modelo recupera."),
    ]
    cards_html = "".join(
        f'<div style="flex:1;display:flex;flex-direction:column;gap:12px;background:{CARD};border:1px solid {RULE};border-radius:16px;padding:32px">'
        f'<p style="font-family:{MONO};font-size:32px;color:{BLUE}">{a}</p>'
        f'<h3 style="font-size:32px;font-weight:600;color:{INK}">{b}</h3>'
        f'<p style="font-size:26px;line-height:1.4;color:{SOFT}">{c}</p></div>'
        for a, b, c in cards
    )
    slides.append(
        f"""<section id="lab" data-transition="fade" data-section="O experimento" style="background:{BG};color:{INK};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:40px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">O experimento</p>
<h2 style="font-family:{SERIF};font-size:64px;font-weight:600;line-height:1.1">Uma economia artificial com a resposta certa embutida</h2>
<p style="font-family:{MONO};font-size:44px;color:{INK};background:{CARD};border:1px solid {RULE};border-radius:16px;padding:28px 36px">g[r,i,t] = n[t] + m[i,t] + c[r,i] + ε[r,i,t]</p>
<div style="display:flex;gap:24px">{cards_html}</div>
<p style="font-size:26px;line-height:1.45;color:{SOFT}">O emprego evolui ano a ano, E[t+1] = E[t]·(1 + g), de modo que ΔE = nacional + composição + competitivo + ruído vale com precisão de máquina. Cada UF tem, portanto, um efeito competitivo <b>verdadeiro</b> contra o qual a estimativa de cada modelo é comparada.</p>
{footer(2)}
<aside>Os efeitos vivem no espaço das taxas de crescimento, exatamente onde todas as variantes de SSA supõem que eles estejam. Um terço das UFs começa com estrutura inclinada para os setores em que tem vantagem (bem alocadas), um terço para os setores em que tem desvantagem (mal alocadas) e um terço neutro. A vantagem regional comum segue um processo SAR com rho = 0,5 sobre a matriz de contiguidade real das UFs.</aside>
</section>"""
    )

    # 3 how to read
    mcards = [
        (
            "Correlação (r)",
            "O modelo acompanha e ordena as UFs como a verdade? 1 é perfeito.",
        ),
        (
            "nRMSE",
            "Erro quadrático médio dividido pelo desvio-padrão da verdade. Abaixo de 1 já supera chutar a média; quanto menor, melhor.",
        ),
        (
            "Sinal correto",
            "Parcela das 27 UFs em que o modelo acerta se a UF ganha ou perde competitividade.",
        ),
    ]
    mc_html = "".join(
        f'<div style="flex:1;display:flex;flex-direction:column;gap:14px;background:{CARD};border:1px solid {RULE};border-radius:16px;padding:36px">'
        f'<h3 style="font-size:36px;font-weight:600;color:{INK}">{a}</h3>'
        f'<p style="font-size:26px;line-height:1.45;color:{SOFT}">{b}</p></div>'
        for a, b in mcards
    )
    slides.append(
        f"""<section id="leitura" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:40px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">Como ler os slides de modelo</p>
<h2 style="font-family:{SERIF};font-size:64px;font-weight:600;line-height:1.1">Cada modelo, lado a lado com a verdade</h2>
<div style="display:flex;gap:40px;align-items:center">
<div style="display:flex;gap:16px;align-items:center"><div style="width:40px;height:40px;background:{BLUE}"></div><p style="font-size:30px">Verdadeiro (DGP)</p></div>
<div style="display:flex;gap:16px;align-items:center"><div style="width:40px;height:40px;background:{ORANGE}"></div><p style="font-size:30px">Estimado pelo modelo</p></div>
<div style="display:flex;gap:16px;align-items:center"><div style="width:40px;height:40px;background:{BG};border:3px solid {ORANGE}"></div><p style="font-size:30px">Estimado, não significativo a 5%</p></div>
</div>
<p style="font-size:28px;line-height:1.45;color:{SOFT}">Os gráficos mostram, para as 27 UFs ordenadas pelo valor verdadeiro, o par de barras verdadeiro × estimado. Ao lado, três medidas resumem a recuperação na semente 42, e uma linha traz a média de 50 simulações.</p>
<div style="display:flex;gap:24px">{mc_html}</div>
<p style="font-size:26px;line-height:1.45;color:{SOFT}">Cada modelo é avaliado contra o alvo que diz estimar: Esteban-Marquillas e Arcelus I contra o efeito competitivo <b>homotético</b> verdadeiro; os demais contra o efeito competitivo verdadeiro.</p>
{footer(3)}
<aside>As métricas vêm de results_recovery.csv (semente 42) e results_montecarlo.csv (50 sementes, cenários benigno e de estresse). O cenário de estresse aumenta a volatilidade do ciclo nacional, as oscilações setoriais anuais e o ruído.</aside>
</section>"""
    )

    # 4 the waves
    rows = [
        (
            "Dunn (1960)",
            "linha de base: identidade de 3 termos",
            "competitivo contaminado pela estrutura",
        ),
        (
            "Fuchs / Stilwell",
            "viés do ano de ponderação",
            "sensibilidade persiste na alocação",
        ),
        (
            "Esteban-Marquillas (1972)",
            "estrutura dentro do competitivo",
            "sinal de AE depende dos pesos",
        ),
        (
            "Arcelus (1984) · I",
            "homotetia só no competitivo",
            "DN e EM nulos por construção",
        ),
        (
            "Arcelus (1984) · II",
            "competitivo mistura UF e setor",
            "diferencial agregado é −IM por construção",
        ),
        ("Barff-Knight (1988)", "viés ponto a ponto", "ainda determinístico"),
        ("Berzeg (1978, 1984)", "nenhum teste estatístico", "supõe normalidade"),
        ("Knudsen (2000)", "ANOVA heterocedástica", "parâmetros em escala log"),
        (
            "Nazara-Hewings (2004)",
            "regiões tratadas como isoladas",
            "sensível à matriz W",
        ),
    ]
    trs = "".join(
        f'<tr><td style="font-weight:600">{a}</td><td>{b}</td><td>{c}</td></tr>'
        for a, b, c in rows
    )
    slides.append(
        f"""<section id="ondas" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:36px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">Três ondas e uma extensão espacial</p>
<h2 style="font-family:{SERIF};font-size:64px;font-weight:600;line-height:1.1">Cada variante corrige uma falha da anterior</h2>
<table style="font-size:28px;color:{INK};padding:12px 16px">
<tr><th style="width:30%">Variante</th><th style="width:36%">Problema que ataca</th><th style="width:34%">Limite que sobra</th></tr>
{trs}
</table>
{footer(4)}
<aside>Síntese do Quadro 1 da nota. A primeira onda (homotética) ataca a contaminação estrutural do efeito competitivo; a segunda (dinâmica) ataca o viés do ano de ponderação e a comparação ponto a ponto; a terceira (inferencial) ataca a impossibilidade de testar uma identidade determinística. Nazara-Hewings ataca o pressuposto de que regiões vizinhas não interagem.</aside>
</section>"""
    )

    # 5 the central defect of the identity
    defeito_cards = [
        ("Onda 1 · homotética", "Mede vantagem e especialização no mesmo número."),
        ("Onda 2 · temporal", "Só as duas pontas do período entram na conta."),
        ("Onda 3 · inferencial", "Identidade determinística não tem erro-padrão."),
        ("Extensão espacial", "Cada região é tratada como ilha, sem vizinhança."),
    ]
    slides.append(
        f"""<section id="defeito" data-transition="fade" data-section="Linha de base" style="background:{INK};color:{BG};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:30px">
<p style="font-size:26px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:{GOLD}">Linha de base · Dunn (1960)</p>
<h2 style="font-family:{SERIF};font-size:68px;font-weight:600;line-height:1.08;color:{BG};width:1520px">O resíduo competitivo nasce contaminado</h2>
<p style="font-family:{MONO};font-size:36px;color:{BG};background:{DARK_CARD};border-radius:16px;padding:26px 32px">ΔE = E₀·gₙ &#160;+&#160; E₀·(gₙᵢ − gₙ) &#160;+&#160; <span style="color:{GOLD}">E₀·(gᵣᵢ − gₙᵢ)</span></p>
<p style="font-size:30px;line-height:1.45;color:{PALE};width:1620px">Rosenfeld (1959) e Houston (1967) apontaram, e Esteban-Marquillas (1972) formalizou: o terceiro termo é ponderado pelo emprego <b>observado</b> da região no setor. Duas regiões com a mesma taxa diferencial recebem efeitos competitivos diferentes só porque uma tem mais emprego ali — o componente que deveria medir vantagem pura mede vantagem × estrutura.</p>
<div style="display:flex;gap:24px">{dark_cards(defeito_cards)}</div>
<p style="font-size:26px;line-height:1.4;color:{FAINT};border-top:1px solid {DARK_RULE};padding:22px 0px 0px 0px">Loveridge e Selting (1998): “SSA é apenas uma identidade contábil praticável: nunca pretendeu ser uma teoria.”</p>
{footer_dark(5)}
<aside>Seções 2.1 e 2.2 da nota. O defeito central já estava descrito em Rosenfeld (1959) e Houston (1967), mas é Esteban-Marquillas (1972) que o demonstra formalmente. Cada uma das quatro falhas listadas abre uma parte deste deck: onda 1 (homotética), onda 2 (temporal), onda 3 (inferencial) e a extensão espacial de Nazara-Hewings (2004), posterior às três.</aside>
</section>"""
    )

    n = 6
    M = "Classic Dunn (base wts)"
    slides.append(
        model_slide(
            "dunn",
            n,
            "Clássico · 1960",
            "Dunn: pesos do ano-base",
            "Identidade contábil que reparte ΔE em crescimento nacional, composição setorial e um resíduo competitivo, todos ponderados pelo emprego inicial.",
            "ΔE = E₀·gₙ + E₀·(gₙᵢ − gₙ)<br>&#160;&#160;&#160;+ E₀·(gᵣᵢ − gₙᵢ)",
            metrics(M),
            [
                mc_line(M),
                f"Composição setorial: r = {br(REC[M]['mix_pearson'])} com a verdade.",
            ],
            chart(CT, TC, comp(M)),
            "Seção 4 da nota. A identidade é algébrica e vale à precisão de máquina. Na simulação, o efeito competitivo de Dunn ordena muito bem as UFs (r alto e sinal sempre correto), mas a magnitude carrega o viés de comparar só os anos extremos de um período de dez anos.",
        )
    )
    n += 1
    slides.append(
        wave_slide(
            "onda1",
            "Onda 1 · homotética",
            n,
            "Onda 1 de 3 · 1972–1987",
            "Homotética: tirar a estrutura de dentro do resíduo",
            "A primeira onda aceita a identidade de Dunn e troca o <b>ponderador</b>. "
            "Em lugar do emprego observado entra o emprego homotético E*, a estrutura "
            "que a região teria se reproduzisse exatamente as participações setoriais "
            "do país — e a diferença entre os dois pesos passa a ser um componente "
            "próprio, o efeito alocação.",
            [
                (
                    "Problema",
                    (
                        "O efeito competitivo mistura vantagem com especialização: "
                        "vantagem × estrutura em um único número."
                    ),
                ),
                (
                    "Mudança",
                    (
                        "Peso contrafactual E* = E₀ᵣ·(E₀ᵢ/E₀); o competitivo se parte em "
                        "puro (CE*) e alocação (AE)."
                    ),
                ),
                (
                    "Limite que sobra",
                    (
                        "O sinal de AE depende do ano de ponderação (Herzog-Olsen, 1977) e "
                        "a homotetia se esgota no competitivo."
                    ),
                ),
            ],
            "Nos próximos quatro slides: Esteban-Marquillas (1972), o efeito alocação, "
            "Arcelus I e Arcelus II (1984). Autores da onda: Esteban-Marquillas (1972), "
            "Herzog-Olsen (1977), Arcelus (1984), Haynes-Machunda (1987).",
            "Seções 6 e 7 da nota. Esteban-Marquillas e Arcelus I são avaliados contra o "
            "efeito competitivo homotético verdadeiro do DGP, não contra o competitivo "
            "clássico — são alvos diferentes. Keil (1992), com dados de Indiana "
            "(1977–1986), concluiu que as extensões homotéticas lançam pouca luz sobre o "
            "crescimento regional total, o que a Seção 7.3 da nota explica por álgebra: "
            "dois dos quatro subcomponentes de Arcelus I são nulos por construção quando "
            "somados por região.",
        )
    )
    n += 1
    M = "Esteban-Marquillas (static)"
    slides.append(
        model_slide(
            "em",
            n,
            "Onda 1 · homotética · 1972",
            "Esteban-Marquillas",
            "Troca o peso observado pelo emprego homotético E*, a estrutura que a UF teria se reproduzisse as participações setoriais do país. Separa competitividade pura de alocação.",
            "E* = E₀ᵣ·(E₀ᵢ/E₀)<br>CE* = E*·(gᵣᵢ − gₙᵢ)",
            metrics(M),
            [mc_line(M)],
            chart(CTH, TH, comp(M)),
            "Seção 6 da nota. Aqui o alvo é o efeito competitivo homotético verdadeiro, calculado no DGP com o emprego homotético ao longo da trajetória. O componente puro acompanha a verdade de perto; o resto do efeito competitivo clássico vai para o efeito alocação, mostrado no próximo slide.",
        )
    )
    n += 1
    g = D["group"]
    al_t, al_e = T["true_alloc"], EST[M]["allocation"]
    grp_rows = ""
    for key, name in (
        ("well_allocated", "Bem alocadas"),
        ("neutral", "Neutras"),
        ("mis_allocated", "Mal alocadas"),
    ):
        idx = [i for i, x in enumerate(g) if x == key]
        mt = sum(al_t[i] for i in idx) / len(idx) / 1000
        me = sum(al_e[i] for i in idx) / len(idx) / 1000
        grp_rows += f'<tr><td>{name}</td><td style="text-align:right">{br(mt, 1)}</td><td style="text-align:right">{br(me, 1)}</td></tr>'
    table = (
        f'<table style="font-size:24px;color:{INK};padding:8px 12px"><tr><th style="width:44%">Grupo (média)</th>'
        f'<th style="width:28%;text-align:right">Verdadeiro</th><th style="width:28%;text-align:right">Estimado</th></tr>{grp_rows}</table>'
    )
    slides.append(
        model_slide(
            "em-aloc",
            n,
            "Onda 1 · homotética · 1972",
            "Efeito alocação",
            "Especialização vezes vantagem: positivo quando a UF se concentra nos setores em que é competitiva, negativo quando se concentra onde perde.",
            "AE = (E₀ − E*)·(gᵣᵢ − gₙᵢ)",
            metrics(M, "alloc_"),
            [table],
            chart(
                "Efeito alocação por UF, ordenado pelo verdadeiro (mil empregos)",
                al_t,
                al_e,
            ),
            "Seção 6.3 da nota. O DGP sorteia um terço das UFs bem alocadas, um terço mal alocadas e um terço neutras. As médias por grupo do efeito alocação estimado praticamente coincidem com as verdadeiras: o efeito funciona como anunciado.",
        )
    )
    n += 1
    M = "Arcelus I (static)"
    slides.append(
        model_slide(
            "arcelus",
            n,
            "Onda 1 · homotética · 1984",
            "Arcelus I: a partição homotética",
            "Estende a partição homotética aos efeitos nacional e de composição. Somados por UF, dois dos quatro novos termos se anulam identicamente.",
            "NE = E*·gₙ + (E₀−E*)·gₙ<br>IM = E*·(gₙᵢ−gₙ) + (E₀−E*)·(gₙᵢ−gₙ)",
            metrics(M),
            [
                mc_line(M),
                "Na simulação, |DN| e |EM| ficam abaixo de 10⁻⁹ em todas as UFs: o competitivo é o de Esteban-Marquillas.",
            ],
            chart(CTH, TH, comp(M)),
            "Não confundir com o Modelo II do mesmo autor, que parte a competitividade usando a taxa da própria UF como referência — é esse que Knudsen (2000) usa, dois slides adiante. Seção 7.2 da nota. A propriedade algébrica da Seção 7.3 aparece na simulação: o termo diferencial nacional e o termo esperado de composição somam zero por UF. Por isso Arcelus I e Esteban-Marquillas estático têm exatamente as mesmas estimativas e as mesmas métricas. O Modelo II (Seção 7.4) é outro objeto: reparte o competitivo de Dunn em deslocamento regional e diferencial, e tem slide próprio a seguir.",
        )
    )
    n += 1
    M = "Arcelus II (static)"
    slides.append(
        model_slide(
            "arcelus2",
            n,
            "Onda 1 · deslocamento regional · 1984",
            "Arcelus II: a partição do competitivo",
            "Troca a referência, não o ponderador: separa o quanto a UF inteira cresce "
            "acima do país do quanto um setor se destaca dentro dela.",
            "r = E₀·(g_UF − gₙ)<br>d = E₀·[(g_rᵢ − g_UF) − (gₙᵢ − gₙ)]",
            metrics(M, "regshift_"),
            [
                (
                    "O competitivo total é <b>idêntico</b> ao de Dunn com pesos-base: "
                    "r + d = E₀·(g_rᵢ − gₙᵢ) célula a célula. "
                    "O modelo acrescenta a partição, não o total."
                ),
                (
                    "Somado por UF, o diferencial é −IM por construção: r = "
                    f"{br(REC[M]['diffshift_pearson'])}, nRMSE = "
                    f"{br(REC[M]['diffshift_nrmse'], 2)}, sinal correto em "
                    f"{pct(REC[M]['diffshift_sign_acc'])}. Pior que chutar a média."
                ),
            ],
            chart(
                "Deslocamento regional por UF, ordenado pelo verdadeiro (mil empregos)",
                TRS,
                EST[M]["regional_shift"],
            ),
            "Seção 7.4 da nota. O gráfico mostra o deslocamento regional, não o "
            "competitivo — este seria cópia exata do slide de Dunn. O DGP constrói "
            "c_rᵢ = c̄_r + d_rᵢ, então a verdade do deslocamento regional é a parcela "
            "c̄_r e a do diferencial é d_rᵢ. O estimador recupera bem a primeira e "
            "nada da segunda: é a degenerescência algébrica da Seção 7.4 aparecendo na "
            "simulação, como os termos nulos de Arcelus I aparecem no slide anterior.",
        )
    )
    n += 1
    slides.append(
        wave_slide(
            "onda2",
            "Onda 2 · temporal",
            n,
            "Onda 2 de 3 · 1959–1988",
            "Temporal: a trajetória entre as duas pontas",
            "A segunda onda não discute o ponderador, mas <b>quando</b> ele é medido. "
            "Fuchs (1959) mostrou que o efeito de composição é sensível ao ano de "
            "ponderação; Stilwell (1969) propôs o extremo terminal e Ashby (1970) o "
            "criticou. Barff e Knight (1988), retomando Thirlwall (1967), foram além: "
            "partiram o intervalo em subperíodos e somaram as decomposições.",
            [
                (
                    "Problema",
                    (
                        "A comparação ponto a ponto ignora a trajetória e a escolha do ano "
                        "de ponderação não é neutra."
                    ),
                ),
                (
                    "Mudança",
                    (
                        "Pesos terminais, média cinquenta-cinquenta ou soma de K "
                        "decomposições subperiódicas."
                    ),
                ),
                (
                    "Limite que sobra",
                    (
                        "Continua determinística e exige dados de alta frequência para "
                        "montar os subperíodos."
                    ),
                ),
            ],
            "Nos próximos quatro slides: Dunn com pesos terminais, Dunn com a média de "
            "Fuchs, Barff-Knight (1988) e Esteban-Marquillas dinâmico, que soma as duas "
            "primeiras ondas. Autores da onda: Fuchs (1959), Stilwell (1969), "
            "Ashby (1970), Barff-Knight (1988).",
            "Seções 5 e 8 da nota. A controvérsia dos pesos aparece na nota antes de "
            "Esteban-Marquillas, por ser uma variação direta da mesma identidade, mas a "
            "taxonomia da Seção 2.2 a classifica nesta onda — é por isso que esses dois "
            "slides vêm aqui, e não junto ao de Dunn. Na simulação, a forma dinâmica é a "
            "que reproduz a construção do DGP, em que o emprego evolui ano a ano, e por "
            "isso supera as formas estáticas em magnitude.",
        )
    )
    n += 1
    M = "Classic Dunn (terminal wts)"
    slides.append(
        model_slide(
            "terminal",
            n,
            "Onda 2 · pesos terminais · 1969",
            "Dunn: pesos do ano terminal",
            "A mesma identidade, reponderada pelo emprego final com a taxa reversa. Stilwell (1969) propôs essa “composição reversa”; Ashby (1970) a criticou como excessiva.",
            "g′ = (E₀ − E₁)/E₁<br>CE = −E₁·(g′ᵣᵢ − g′ₙᵢ)",
            metrics(M),
            [
                mc_line(M),
                f"É a pior variante em magnitude na média de 50 simulações; a composição setorial cai para r = {br(REC[M]['mix_pearson'])}.",
            ],
            chart(CT, TC, comp(M)),
            "Seção 5 da nota. Na semente 42 o nRMSE dos pesos terminais é até baixo, mas o Monte Carlo mostra que, em média, é a variante que mais erra a magnitude, e o erro cresce no cenário volátil, como previa a crítica de Ashby e a advertência de Herzog-Olsen sobre sensibilidade aos pesos.",
        )
    )
    n += 1
    M = "Classic Dunn (avg wts, Fuchs)"
    slides.append(
        model_slide(
            "fuchs",
            n,
            "Onda 2 · média dos pesos · 1959",
            "Dunn: média dos pesos (Fuchs)",
            "Fuchs (1959) mostrou que o efeito de composição é sensível ao ano de ponderação e propôs a média entre pesos-base e pesos-terminais.",
            "CE = ½·(CE_base + CE_terminal)",
            metrics(M),
            [
                mc_line(M),
                "Fica entre as duas convenções: melhor que a terminal, pior que a base na média.",
            ],
            chart(CT, TC, comp(M)),
            "Seção 5 da nota. A convenção cinquenta-cinquenta suaviza, mas não elimina, o viés de ponto a ponto: a média das duas pontas continua ignorando a trajetória do emprego entre elas.",
        )
    )
    n += 1
    M = "Dynamic (Barff-Knight)"
    slides.append(
        model_slide(
            "bk",
            n,
            "Onda 2 · dinâmica · 1988",
            "Barff-Knight dinâmico",
            "Recalcula a identidade clássica ano a ano, com o emprego do início de cada ano como peso, e soma. Elimina o viés de comparar só as pontas.",
            "CE = Σₜ Eₜ₋₁·(gᵣᵢ⁽ᵗ⁾ − gₙᵢ⁽ᵗ⁾)",
            metrics(M),
            [mc_line(M), "No estresse, reduz o erro dos pesos-base de 0,29 para 0,25."],
            chart(CT, TC, comp(M)),
            "Seção 8 da nota. A forma dinâmica é a que reproduz a construção do DGP, em que o emprego evolui ano a ano. Por isso, em média, supera todas as formas estáticas de Dunn, e a vantagem aumenta quando o ciclo é volátil.",
        )
    )
    n += 1
    M = "Dynamic Esteban-Marquillas"
    slides.append(
        model_slide(
            "dem",
            n,
            "Ondas 1 + 2",
            "Esteban-Marquillas dinâmico",
            "Junta as duas correções: o emprego homotético é recalculado a cada ano e o efeito competitivo puro é somado ao longo da trajetória.",
            "CE* = Σₜ E*ₜ·(gᵣᵢ⁽ᵗ⁾ − gₙᵢ⁽ᵗ⁾)",
            metrics(M),
            [
                mc_line(M),
                f"Alocação: r = {br(REC[M]['alloc_pearson'])} com a verdade.",
            ],
            chart(CTH, TH, comp(M)),
            "Variante implementada no código e não descrita na nota. Na média de 50 simulações é a de menor erro de magnitude no cenário de estresse, empatada com a regressão full-analogue.",
        )
    )
    n += 1
    slides.append(
        wave_slide(
            "onda3",
            "Onda 3 · inferencial",
            n,
            "Onda 3 de 3 · 1976–2000",
            "Inferencial: um número sem erro-padrão não é resultado",
            "A terceira onda ataca o que as duas primeiras não podiam tocar. Como "
            "observam Selting e Loveridge (1992), uma identidade determinística não tem "
            "erro-padrão: não há como dizer se um efeito competitivo é vantagem ou "
            "ruído amostral. Berzeg (1978, 1984) recasta a identidade como ANOVA, em que "
            "o competitivo é o <b>resíduo</b> de uma regressão; Knudsen (2000) a deriva "
            "da teoria da informação.",
            [
                (
                    "Problema",
                    (
                        "Nenhum componente da SSA clássica admite teste de hipótese, "
                        "porque nenhum tem distribuição."
                    ),
                ),
                (
                    "Mudança",
                    (
                        "Regressão das taxas em dummies (ANOVA) e mínima informação "
                        "discriminante (GLM de Poisson log-linear)."
                    ),
                ),
                (
                    "Limite que sobra",
                    (
                        "Supõe normalidade; parâmetros em escala log; exige correção de "
                        "dispersão (quase-Poisson)."
                    ),
                ),
            ],
            "Nos próximos quatro slides: Berzeg ANOVA, regressão full-analogue, Knudsen "
            "estático e Knudsen dinâmico. Autores da onda: Buck-Atkins (1976), "
            "Berzeg (1978, 1984), Patterson (1991), Knudsen (2000).",
            "Seções 9 e 10 da nota. Na comparação empírica de Knudsen (2000), com emprego "
            "do BLS nas nove divisões censitárias dos EUA (1970 e 1980), a forma "
            "informacional ajustou melhor que a ANOVA correspondente: PNMD de 0,5163 e "
            "0,6601 contra R² de 0,1836 e 0,2284 nos modelos simples e com a extensão de "
            "Arcelus. Na forma dinâmica o ajuste foi fraco nos dois casos (0,0258 contra "
            "0,0111). O próprio autor conclui com cautela: os parâmetros informacionais "
            "são mais difíceis de interpretar e nem sempre ajustam melhor.",
        )
    )
    n += 1
    M = "Berzeg ANOVA (stochastic)"
    slides.append(
        model_slide(
            "berzeg",
            n,
            "Onda 3 · inferencial · 1978",
            "Berzeg: ANOVA",
            "Reescreve a identidade como regressão das taxas em dummies de setor. O efeito competitivo vira o resíduo médio da UF, com erro-padrão e teste t.",
            "gᵣᵢₜ = Σ βᵢDᵢ + uᵣᵢₜ (MQP)<br>t = ūᵣ / ep(ūᵣ)",
            metrics(M),
            [
                sig_line(M),
                "Estimativas pontuais idênticas às de Barff-Knight: a ANOVA só acrescenta os erros-padrão.",
            ],
            chart(CT, TC, comp(M), sig(M)),
            "Seção 9 da nota. Aqui a regressão é estimada por mínimos quadrados ponderados nas taxas anuais, que é a versão que reproduz a identidade (Seção 10.1). As estimativas coincidem com Barff-Knight, replicando Knudsen e Barff (1991). Barras vazadas: UFs cujo efeito não é significativo a 5%.",
        )
    )
    n += 1
    M = "Full-analogue regression"
    slides.append(
        model_slide(
            "far",
            n,
            "Onda 3 · inferencial",
            "Regressão full-analogue",
            "Buck-Atkins (1976) e Patterson (1991): taxas anuais em efeitos de ano, setor × ano e região, com restrições de soma zero ponderadas.",
            "gᵣᵢₜ = Yₜ + Iᵢₜ + Rᵣ + e (MQP)",
            metrics(M),
            [sig_line(M), mc_line(M)],
            chart(CT, TC, comp(M), sig(M)),
            "Variante implementada no código e não descrita na nota. O efeito de região estimado é a taxa competitiva, convertida em empregos. Junto com Esteban-Marquillas dinâmico, tem o menor erro médio de magnitude entre todos os modelos.",
        )
    )
    n += 1
    M = "Knudsen MDI (static)"
    slides.append(
        model_slide(
            "knud-s",
            n,
            "Onda 3 · teoria da informação · 2000",
            "Knudsen: forma estática",
            "Mínima informação discriminante com restrição de margens setoriais e regionais — a extensão de Arcelus II: modelo log-linear estimado como GLM de Poisson com offset ln E₀, uma única transição de dez anos.",
            "ln(E₁/E₀) = A + Oᵢ + Dᵣ<br>CE = (e^D̃ᵣ − 1)·Wᵣ",
            metrics(M),
            [sig_line(M), mc_line(M)],
            chart(CT, TC, comp(M), sig(M)),
            "Seção 10 da nota, equação 18 de Knudsen (2000) — a forma com a extensão de Arcelus, que é o Modelo II (deslocamento regional), não a homotética do slide de Arcelus I. Dᵣ é a contraparte log-linear do deslocamento regional. Erros-padrão quase-Poisson (dispersão de Pearson), recentragem ponderada de D e conversão em empregos são adaptações da implementação. Na semente 42 tem a maior correlação de todas, mas no Monte Carlo fica atrás de Dunn com pesos-base em magnitude.",
        )
    )
    n += 1
    M = "Knudsen MDI (dynamic)"
    slides.append(
        model_slide(
            "knud-d",
            n,
            "Onda 3 · teoria da informação · 2000",
            "Knudsen: forma dinâmica",
            "Acrescenta à tabela a dimensão do tempo, com um efeito Tₜ para cada par de anos adjacentes.",
            "ln(Eₜ/Eₜ₋₁) = A + Oᵢ + Dᵣ + Tₜ",
            metrics(M),
            [sig_line(M), mc_line(M)],
            chart(CT, TC, comp(M), sig(M)),
            "Equação 19 de Knudsen (2000), a extensão de Arcelus (Modelo II) com a dimensão do tempo. A forma dinâmica acompanha quase exatamente a regressão full-analogue: as taxas competitivas se correlacionam a 0,99999. A dispersão estimada é cerca de 5, por isso a correção quase-Poisson importa.",
        )
    )
    n += 1
    slides.append(
        wave_slide(
            "espacial",
            "Extensão espacial",
            n,
            "Extensão espacial · 2004",
            "Vizinhos que não eram para existir",
            "Nazara e Hewings (2004) atacam um pressuposto comum às três ondas: o de que "
            "regiões vizinhas não interagem. Com uma matriz de pesos espaciais W, o país "
            "deixa de ser a única referência — a vizinhança entra entre a região e a "
            "média nacional, e o competitivo se parte em quanto a vizinhança supera o "
            "país e quanto a região supera a vizinhança.",
            [
                (
                    "Problema",
                    (
                        "Cada região é tratada como isolada, embora partilhe mercados de "
                        "trabalho e transbordamentos com as vizinhas."
                    ),
                ),
                (
                    "Mudança",
                    (
                        "Matriz W de contiguidade; defasagem espacial (Wc)ᵣ e taxonomia de "
                        "vinte estruturas de decomposição."
                    ),
                ),
                (
                    "Limite que sobra",
                    (
                        "Sensível à especificação de W e exige N grande: com 5 regiões o I "
                        "de Moran não tem poder algum."
                    ),
                ),
            ],
            "Nos próximos dois slides: Nazara-Hewings estático e dinâmico. O I de Moran "
            "é calculado sobre a taxa competitiva cᵣ = CEᵣ/E₀ᵣ, nunca sobre o emprego em "
            "nível — em nível, o tamanho das UFs encobre inteiramente o padrão espacial.",
            "Seção 11 da nota. A nota ilustra o cálculo com cinco UFs do Nordeste e um I "
            "de Moran de −0,4852 contra E[I] = −0,25, explicitamente apresentado como "
            "demonstração de cálculo e não como evidência: com n = 5 o teste não tem "
            "poder. A simulação deste deck usa a matriz de contiguidade real das 27 UFs e "
            "um processo SAR com rho = 0,5, de modo que existe dependência espacial "
            "verdadeira a ser recuperada.",
        )
    )
    n += 1
    for sid, M, ttl, note in (
        (
            "nh-s",
            "Nazara-Hewings spatial (static)",
            "Nazara-Hewings estático",
            "Seção 11 da nota. O efeito competitivo total é idêntico ao de Dunn com pesos-base, como exige a aditividade; o ganho está na partição. No DGP, a vizinhança verdadeira usa W·c ao longo da trajetória.",
        ),
        (
            "nh-d",
            "Nazara-Hewings spatial (dynamic)",
            "Nazara-Hewings dinâmico",
            "Versão anual da partição espacial. O total coincide com Barff-Knight. Em 50 simulações, a parte própria é recuperada com erro menor que na versão estática.",
        ),
    ):
        est = EST[M]
        r = REC[M]
        slides.append(
            model_slide(
                sid,
                n,
                "Extensão espacial · 2004",
                ttl,
                "Troca o país pela vizinhança como referência: o efeito competitivo se divide em quanto a vizinhança supera o país e quanto a UF supera a vizinhança.",
                "g̃ᵣᵢ = Σₖ wᵣₖ·gₖᵢ<br>CE = E₀·(g̃ᵣᵢ−gₙᵢ) + E₀·(gᵣᵢ−g̃ᵣᵢ)",
                [
                    (br(r["neigh_pearson"]), "r vizinhança"),
                    (br(r["own_pearson"]), "r próprio"),
                    (br(r["own_nrmse"], 2), "nRMSE próprio"),
                ],
                [
                    f"Monte Carlo benigno · nRMSE vizinhança <b>{br(MC[('benign', M)]['neigh_nrmse_mean'], 2)}</b>, próprio <b>{br(MC[('benign', M)]['own_nrmse_mean'], 2)}</b>.",
                ],
                double_chart(
                    (
                        "Efeito vizinhança (mil empregos)",
                        REGS,
                        T["true_neigh"],
                        est["neighborhood"],
                    ),
                    (
                        "Efeito próprio líquido (mil empregos)",
                        REGS,
                        T["true_own_net"],
                        est["own_net"],
                    ),
                ),
                note,
            )
        )
        n += 1

    # Monte Carlo ranking
    order = sorted(NAMES, key=lambda m: MC[("stress", m)]["nrmse_mean"])
    rows = [
        (
            NAMES[m],
            [
                (MC[("benign", m)]["nrmse_mean"], BLUE),
                (MC[("stress", m)]["nrmse_mean"], ORANGE),
            ],
        )
        for m in order
    ]
    rank_chart = hbar_chart(
        rows,
        1180,
        800,
        612,
        104,
        0.6,
        [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
        lambda v: br(v, 2),
        [(BLUE, "Cenário benigno"), (ORANGE, "Cenário de estresse")],
    )
    slides.append(
        f"""<section id="ranking" data-transition="fade" data-section="Síntese" style="background:{BG};color:{INK};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:24px">
<div style="width:440px;display:flex;flex-direction:column;gap:24px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">Síntese · 50 simulações</p>
<h2 style="font-family:{SERIF};font-size:54px;font-weight:600;line-height:1.08">Todos ordenam bem; a magnitude separa</h2>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">Correlação com a verdade entre 0,95 e 0,99 em todos os modelos. O erro de magnitude (nRMSE, menor é melhor) favorece as formas dinâmicas, e a distância cresce no cenário volátil.</p>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">Pesos terminais quase dobram o erro das formas dinâmicas sob estresse.</p>
</div>
{rank_chart}
{footer(n)}
<aside>Monte Carlo de 50 sementes por cenário (results_montecarlo.csv), ordenado pelo nRMSE no cenário de estresse. Berzeg, Barff-Knight e Nazara-Hewings dinâmico têm o mesmo efeito competitivo total; Esteban-Marquillas e Arcelus I também coincidem.</aside>
</section>"""
    )
    n += 1

    # five states: truth against estimate, case by case
    COMP_TARGET = [m for m in NAMES if REC[m]["target"] == "true_comp"]
    GRP = {
        "well_allocated": "bem alocada",
        "mis_allocated": "mal alocada",
        "neutral": "neutra",
    }
    GRPS = D["group"]
    idx = {r: i for i, r in enumerate(REGS)}
    CBAR = T["c_bar"]

    def mil(v):
        """Employment-unit value in thousands of jobs."""
        return v / 1000.0

    def case_row(uf):
        i = idx[uf]
        vals = [comp(m)[i] for m in COMP_TARGET]
        lo, hi = min(vals), max(vals)
        errs = [abs(v - TC[i]) for v in vals]
        return {
            "uf": uf,
            "grp": GRP[GRPS[i]],
            "true": mil(TC[i]),
            "rate": 100 * CBAR[i],
            "alloc": mil(T["true_alloc"][i]),
            "base": mil(comp("Classic Dunn (base wts)")[i]),
            "term": mil(comp("Classic Dunn (terminal wts)")[i]),
            "bk": mil(comp("Dynamic (Barff-Knight)")[i]),
            "knud": mil(comp("Knudsen MDI (static)")[i]),
            "lo": mil(lo),
            "hi": mil(hi),
            "span": mil(hi - lo),
            "emin": mil(min(errs)),
            "emax": mil(max(errs)),
            "signs": sum(1 for v in vals if (v > 0) == (TC[i] > 0)),
            "nsig": sum(
                1
                for m in (
                    "Berzeg ANOVA (stochastic)",
                    "Full-analogue regression",
                    "Knudsen MDI (static)",
                    "Knudsen MDI (dynamic)",
                )
                if not sig(m)[i]
            ),
        }

    C = {uf: case_row(uf) for uf in ("AC", "ES", "GO", "MG", "AP")}
    nvar = len(COMP_TARGET)
    read = {
        "AC": (
            f"<b>Primeira colocada nas {nvar}</b> variantes \u2014 mas a faixa abre "
            f"{br(C['AC']['span'], 1)} mil empregos, "
            f"{pct(C['AC']['span'] / C['AC']['true'])} do valor verdadeiro."
        ),
        "ES": (
            f"Mal alocada, <b>sinal correto nas {nvar}</b>. Knudsen erra "
            f"{br(C['ES']['emin'], 1)} mil; Dunn com pesos-base, "
            f"{br(C['ES']['emax'], 1)} mil."
        ),
        "GO": (
            f"Aloca\u00e7\u00e3o de {br(C['GO']['alloc'], 1)} mil: <b>todas as {nvar}</b> "
            f"subestimam a vantagem, de {br(C['GO']['emin'], 1)} a "
            f"{br(C['GO']['emax'], 1)} mil."
        ),
        "MG": (
            f"Taxa de {br(C['MG']['rate'], 2)}% contra {br(C['AC']['rate'], 2)}% do "
            f"AC, e efeitos da mesma ordem em n\u00edvel: \u00e9 <b>escala</b>, n\u00e3o desempenho."
        ),
        "AP": (
            f"Vantagem nula ({br(C['AP']['rate'], 2)}%): "
            f"<b>{C['AP']['nsig']} dos 4</b> modelos inferenciais recusam "
            f"signific\u00e2ncia a 5%."
        ),
    }
    chead = [
        ("UF", "5%", "left"),
        ("Verdadeiro", "9%", "right"),
        ("Dunn-base", "9%", "right"),
        ("Terminal", "9%", "right"),
        ("Barff-Knight", "10%", "right"),
        ("Knudsen est.", "10%", "right"),
        (f"Faixa das {nvar}", "12%", "right"),
        ("O que o caso revela", "38%", "left"),
    ]
    crows = [
        (
            c["uf"],
            br(c["true"], 1),
            br(c["base"], 1),
            br(c["term"], 1),
            br(c["bk"], 1),
            br(c["knud"], 1),
            f"{br(c['lo'], 1)} a {br(c['hi'], 1)}",
            read[c["uf"]],
        )
        for c in C.values()
    ]
    slides.append(
        f"""<section id="casos" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:28px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">S\u00edntese \u00b7 cinco casos</p>
<h2 style="font-family:{SERIF};font-size:54px;font-weight:600;line-height:1.08">Cinco UFs, verdade e estimativa lado a lado</h2>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">Efeito competitivo em mil empregos, semente 42. A <i>faixa</i> \u00e9 o m\u00ednimo e o m\u00e1ximo entre as {nvar} variantes de alvo cl\u00e1ssico; Esteban-Marquillas, Arcelus I e E-M din\u00e2mico estimam outro alvo, o homot\u00e9tico.</p>
{table_html(chead, crows, 23)}
<p style="font-size:26px;line-height:1.4;color:{SOFT}"><b>Ordena\u00e7\u00e3o e sinal s\u00e3o consensuais; a magnitude n\u00e3o.</b> Onde a UF \u00e9 mal alocada (GO, ES) ou grande com taxa pequena (MG), o res\u00edduo absorve o que n\u00e3o deveria \u2014 e nenhuma variante de alvo cl\u00e1ssico corrige isso.</p>
{footer(n)}
<aside>Casos escolhidos entre as 27 UFs da semente 42 para cobrir os extremos e os defeitos conhecidos: AC (maior vantagem), ES (maior desvantagem), GO (m\u00e1 aloca\u00e7\u00e3o forte), MG (taxa pequena sobre base grande) e AP (vantagem praticamente nula). \u00c9 a mesma estrat\u00e9gia das Tabelas 4 a 7 da nota, que usam cinco UFs do Nordeste para exibir um caso de vantagem concentrada, um de desvantagem generalizada, um neutro e um de especializa\u00e7\u00e3o mal alocada \u2014 com a diferen\u00e7a de que aqui existe gabarito contra o qual comparar.</aside>
</section>"""
    )
    n += 1
    # what the approach delivers and where it fails
    fortes = [
        (
            "Ordena\u00e7\u00e3o sobrevive a tudo",
            (
                f"Na semente 42, correla\u00e7\u00e3o com a verdade entre "
                f"{br(min(REC[m]['pearson'] for m in COMP_TARGET), 2)} e "
                f"{br(max(REC[m]['pearson'] for m in COMP_TARGET), 2)} nas {nvar} variantes, "
                "e sinal correto em todas elas nos cinco casos do slide anterior."
            ),
        ),
        (
            "A identidade fecha",
            (
                "A soma dos componentes reproduz \u0394E \u00e0 precis\u00e3o de m\u00e1quina. Nada do "
                "resultado depende de converg\u00eancia, ajuste ou escolha de estimador."
            ),
        ),
        (
            "A aloca\u00e7\u00e3o faz o que promete",
            (
                "As m\u00e9dias do efeito aloca\u00e7\u00e3o por grupo do DGP \u2014 bem alocadas, neutras, "
                "mal alocadas \u2014 praticamente coincidem com as verdadeiras."
            ),
        ),
        (
            "A infer\u00eancia separa sinal de ru\u00eddo",
            (
                f"No AP, de vantagem verdadeira de {br(C['AP']['rate'], 2)}%, "
                f"{C['AP']['nsig']} dos 4 modelos inferenciais recusam signific\u00e2ncia a 5%."
            ),
        ),
        (
            "A forma din\u00e2mica compensa volatilidade",
            (
                "Somar decomposi\u00e7\u00f5es anuais reduz o erro de magnitude, e a vantagem "
                "sobre as formas est\u00e1ticas cresce no cen\u00e1rio de estresse."
            ),
        ),
    ]
    fracos = [
        (
            "Magnitude \u00e9 conven\u00e7\u00e3o",
            (
                f"Mudar s\u00f3 o ano de pondera\u00e7\u00e3o abre {br(C['AC']['span'], 1)} mil empregos "
                f"de faixa no AC, {pct(C['AC']['span'] / C['AC']['true'])} do valor verdadeiro."
            ),
        ),
        (
            "O res\u00edduo absorve a m\u00e1 aloca\u00e7\u00e3o",
            (
                f"No GO, com aloca\u00e7\u00e3o de {br(C['GO']['alloc'], 1)} mil, todas as {nvar} "
                f"variantes subestimam a vantagem em {br(C['GO']['emin'], 1)} a "
                f"{br(C['GO']['emax'], 1)} mil."
            ),
        ),
        (
            "O n\u00edvel premia tamanho",
            (
                f"MG tem taxa de {br(C['MG']['rate'], 2)}% e AC de {br(C['AC']['rate'], 2)}%; "
                "em empregos os dois efeitos ficam na mesma ordem. \u00c9 o defeito que E* corrige."
            ),
        ),
        (
            "Duas extens\u00f5es degeneram por \u00e1lgebra",
            (
                "Em Arcelus I, DN e EM s\u00e3o nulos por UF; em Arcelus II, o diferencial "
                f"somado \u00e9 \u2212IM, com sinal correto em s\u00f3 "
                f"{pct(REC['Arcelus II (static)']['diffshift_sign_acc'])} das UFs."
            ),
        ),
        (
            "Fora do laborat\u00f3rio, quase nada \u00e9 significativo",
            (
                "Na RAIS 2022\u20132025, de 27 UFs apenas 0 a 4 t\u00eam efeito competitivo "
                "distingu\u00edvel de zero a 5% \u2014 e uma quebra de s\u00e9rie desloca mais que a "
                "pior escolha de variante."
            ),
        ),
    ]

    def ledger(title, items, accent):
        rows = "".join(
            f'<p style="font-size:25px;line-height:1.4;color:{SOFT};'
            f'border-top:1px solid {RULE};padding:16px 0px 0px 0px">'
            f'<b style="color:{INK}">{a}</b> \u2014 {b}</p>'
            for a, b in items
        )
        return (
            f'<div style="flex:1;display:flex;flex-direction:column;gap:16px">'
            f'<h3 style="font-size:34px;font-weight:600;color:{accent}">{title}</h3>'
            f"{rows}</div>"
        )

    slides.append(
        f"""<section id="balanco" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:30px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">S\u00edntese \u00b7 balan\u00e7o</p>
<h2 style="font-family:{SERIF};font-size:54px;font-weight:600;line-height:1.08">Pontos fortes e pontos fracos da abordagem</h2>
<div style="display:flex;gap:56px">
{ledger("O que a abordagem entrega", fortes, BLUE)}
{ledger("Onde ela falha", fracos, ORANGE)}
</div>
{footer(n)}
<aside>Lado esquerdo: o que a simula\u00e7\u00e3o confirma, com gabarito. Lado direito: as limita\u00e7\u00f5es da Se\u00e7\u00e3o 14 da nota, aqui quantificadas nos cinco casos do slide anterior. A limita\u00e7\u00e3o de fundo permanece a da Se\u00e7\u00e3o 1: a SSA \u00e9 uma identidade cont\u00e1bil, n\u00e3o um modelo causal, e nenhum destes resultados a torna preditiva. A pr\u00f3pria simula\u00e7\u00e3o tem um teto: nela o efeito competitivo verdadeiro \u00e9 constante no tempo, o que favorece todos os modelos.</aside>
</section>"""
    )
    n += 1
    # Moran's I
    mor = D["moran"]
    true_I = mor[0]["morans_I"]
    mrows = [("Verdadeiro (DGP)", [(true_I, BLUE)])] + [
        (NAMES[r["series"].replace(" [rate]", "")], [(r["morans_I"], ORANGE)])
        for r in mor[1:]
    ]
    moran_chart = hbar_chart(
        mrows,
        1180,
        800,
        612,
        104,
        0.7,
        [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
        lambda v: br(v, 2),
        [(BLUE, "I de Moran verdadeiro"), (ORANGE, "Estimado")],
        ref=true_I,
    )
    est_I = [r["morans_I"] for r in mor[1:]]
    slides.append(
        f"""<section id="moran" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:24px">
<div style="width:440px;display:flex;flex-direction:column;gap:24px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">Dependência espacial</p>
<h2 style="font-family:{SERIF};font-size:54px;font-weight:600;line-height:1.08">Todos detectam o agrupamento espacial</h2>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">I de Moran das taxas competitivas: verdadeiro {br(true_I, 2)}; estimado entre {br(min(est_I), 2)} e {br(max(est_I), 2)}, todos com p = 0,001.</p>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">Calculado sobre o emprego em nível, o I cai para cerca de 0,12, não significativo: o tamanho das UFs encobre o padrão.</p>
</div>
{moran_chart}
{footer(n)}
<aside>results_morans_i.csv, 999 permutações, matriz de contiguidade real das 27 UFs. A linha tracejada marca o valor verdadeiro. A nota (Seção 11) já advertia: o I de Moran deve ser calculado sobre taxas competitivas, nunca sobre o emprego em nível.</aside>
</section>"""
    )
    n += 1

    # significance
    srows = ""
    for m in (
        "Berzeg ANOVA (stochastic)",
        "Full-analogue regression",
        "Knudsen MDI (static)",
        "Knudsen MDI (dynamic)",
    ):
        s = SIG[m]
        srows += (
            f'<tr><td style="font-weight:600">{NAMES[m]}</td><td style="text-align:right">{sum(EST[m]["sig"])} de 27</td>'
            f'<td style="text-align:right">{pct(s["power_strong_regions"])}</td><td style="text-align:right">{pct(s["flag_rate_weak_regions"])}</td></tr>'
        )
    slides.append(
        f"""<section id="signif" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:36px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">Inferência</p>
<h2 style="font-family:{SERIF};font-size:64px;font-weight:600;line-height:1.1">Só os modelos inferenciais dizem se o efeito é real</h2>
<table style="font-size:30px;color:{INK};padding:14px 18px">
<tr><th style="width:34%">Modelo</th><th style="width:22%;text-align:right">UFs signif. 5%</th><th style="width:22%;text-align:right">Vantagem forte</th><th style="width:22%;text-align:right">Vantagem fraca</th></tr>
{srows}
</table>
<p style="font-size:26px;line-height:1.45;color:{SOFT}">“Vantagem forte”: terço das UFs com maior |c̄| verdadeiro, parcela marcada como significativa (poder). “Vantagem fraca”: terço com menor |c̄|, parcela marcada mesmo assim. As variantes determinísticas produzem números sem nenhum meio de separar sinal de ruído.</p>
{footer(n)}
<aside>Diagnóstico de significância da semente 42 (significance_diagnostics em run_comparison.py). Os testes têm poder alto, mas também marcam boa parte das UFs de vantagem fraca, o que é esperado: vantagem fraca não é vantagem nula. Knudsen estático, com uma única transição, é o mais conservador.</aside>
</section>"""
    )
    n += 1

    # the real-data section
    rais_slides, n = build_rais_slides(D["rais"], n, true_I)
    slides.extend(rais_slides)

    # conclusions
    concl = [
        (
            "Ordenação robusta",
            "Todas as variantes ordenam as UFs quase igual, na simulação (r de 0,95 a 0,99) e na RAIS (r de 0,72 a 1,00), como Knudsen e Barff (1991) previam.",
        ),
        (
            "Magnitude depende da forma",
            "Formas dinâmicas e regressões ponderadas erram menos; pesos terminais erram mais, sobretudo sob volatilidade.",
        ),
        (
            "Alocação funciona",
            "O efeito alocação de Esteban-Marquillas separa UFs bem e mal alocadas com médias próximas das verdadeiras.",
        ),
        (
            "A série vem antes do método",
            "Na RAIS, uma quebra de série desloca o competitivo quatro vezes mais do que a pior escolha de variante — e nenhuma variante corrige isso.",
        ),
        (
            "Sem erro-padrão, sem resultado",
            "Nos dados reais, de 27 UFs apenas 0 a 4 têm efeito competitivo distinguível de zero a 5%.",
        ),
        (
            "Limite do laboratório",
            "A verdade da simulação é constante no tempo; na prática o efeito competitivo oscila, então aqueles resultados são um teto.",
        ),
    ]
    ch = "".join(
        f'<div style="display:flex;flex-direction:column;gap:12px;background:#24313F;border-radius:16px;padding:36px">'
        f'<h3 style="font-size:36px;font-weight:600;color:#E9A867">{a}</h3>'
        f'<p style="font-size:27px;line-height:1.45;color:#D5DBE2">{b}</p></div>'
        for a, b in concl
    )
    slides.append(
        f"""<section id="conclusoes" data-transition="fade" style="background:{INK};color:{BG};font-family:{SANS};padding:104px 128px 128px;display:flex;flex-direction:column;gap:40px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#E9A867">Conclusões</p>
<h2 style="font-family:{SERIF};font-size:64px;font-weight:600;line-height:1.1;color:{BG}">O que o laboratório e o campo dizem juntos</h2>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:28px">{ch}</div>
<aside>Nenhum destes resultados valida a SSA como ferramenta de previsão ou causal: ela continua sendo uma identidade contábil. A simulação mostra que os métodos funcionam quando existe verdade; a RAIS mostra onde o resultado é frágil quando não existe. A nota sugere, como próximos passos, testar outras matrizes W, vantagens específicas por setor com estrutura espacial e um passo de econometria espacial.</aside>
</section>"""
    )
    n += 1

    # annex: the note's parameters beside this deck's
    phead = [
        ("Par\u00e2metro", "26%", "left"),
        ("Nota metodol\u00f3gica (exemplo did\u00e1tico)", "36%", "left"),
        ("Simula\u00e7\u00e3o deste deck", "38%", "left"),
    ]
    prows = [
        ("Regi\u00f5es", "5: PI, CE, MA, BA, PE", "27 unidades federativas"),
        (
            "Setores",
            "3: agropecu\u00e1ria, ind\u00fastria, servi\u00e7os",
            "5 setores agregados",
        ),
        (
            "Per\u00edodos",
            "t\u2080 \u2192 t\u2081, dois pontos",
            "10 anos, 9 transi\u00e7\u00f5es anuais",
        ),
        (
            "Natureza dos dados",
            "sint\u00e9ticos ilustrativos, sem verdade conhecida",
            "sint\u00e9ticos com verdade embutida, semente 42",
        ),
        ("Repeti\u00e7\u00f5es", "nenhuma", "50 sementes \u00d7 2 cen\u00e1rios"),
        (
            "Subper\u00edodos din\u00e2micos",
            "2, trajet\u00f3ria hipot\u00e9tica",
            "9 subper\u00edodos anuais",
        ),
        (
            "Regress\u00e3o de Berzeg",
            "MQO, dummies de setor, sem pondera\u00e7\u00e3o",
            "MQP nas taxas anuais, a vers\u00e3o que reproduz a identidade",
        ),
        (
            "Modelo de Knudsen",
            "GLM Poisson, offset ln E\u2080, refer\u00eancias BA e AGR",
            "idem, com erros quase-Poisson (dispers\u00e3o \u2248 5 na forma din\u00e2mica)",
        ),
        (
            "Vizinhan\u00e7a e I de Moran",
            "contiguidade entre as 5 UFs, I sobre a taxa competitiva",
            "contiguidade real das 27 UFs, rho = 0,5 no DGP, 999 permuta\u00e7\u00f5es",
        ),
    ]
    slides.append(
        f"""<section id="parametros" data-transition="fade" data-section="Anexo" style="background:{BG};color:{INK};font-family:{SANS};padding:104px 128px 160px;display:flex;flex-direction:column;gap:28px">
<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">Anexo</p>
<h2 style="font-family:{SERIF};font-size:54px;font-weight:600;line-height:1.08">Quadro de par\u00e2metros consolidados</h2>
<p style="font-size:26px;line-height:1.4;color:{SOFT}">A nota mostra <i>como</i> cada f\u00f3rmula se deriva da anterior, com um exemplo pequeno o suficiente para conferir \u00e0 m\u00e3o; a simula\u00e7\u00e3o mede <i>quanto</i> cada f\u00f3rmula recupera, com um painel grande o suficiente para ter poder. Signific\u00e2ncia de 5% em ambas.</p>
{table_html(phead, prows, 22)}
{footer(n, "Se\u00e7\u00e3o 13 da nota metodol\u00f3gica \u00b7 ssa_dgp.py e run_comparison.py para a simula\u00e7\u00e3o")}
<aside>Se\u00e7\u00e3o 13 da nota, com a coluna da simula\u00e7\u00e3o acrescentada. Duas diferen\u00e7as merecem aten\u00e7\u00e3o. A regress\u00e3o de Berzeg da nota \u00e9 estimada por MQO sem pondera\u00e7\u00e3o, que n\u00e3o reproduz a identidade cont\u00e1bil: segundo Knudsen (2000), as estimativas s\u00f3 coincidem sob MQP com pesos w = E\u2080/\u03a3E\u2080, que \u00e9 o que a simula\u00e7\u00e3o usa. E a nota, com 5 regi\u00f5es, n\u00e3o tem poder para o I de Moran nem para os testes t, limita\u00e7\u00e3o que ela pr\u00f3pria declara na Se\u00e7\u00e3o 14.</aside>
</section>"""
    )
    n += 1
    return slides


def slide_id(s):
    return s.split('id="', 1)[1].split('"', 1)[0]


# ----------------------------------------------------------------------
# outputs
# ----------------------------------------------------------------------
STANDALONE_CSS = """
html, body { margin: 0; height: 100%; background: #0F151C; overflow: hidden; }
section { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px;
  box-sizing: border-box; transform-origin: 0 0; overflow: hidden; visibility: hidden; }
section.on { visibility: visible; }
section * { margin: 0; box-sizing: border-box; }
section aside { display: none; }
table { border-collapse: collapse; width: 100%; padding: 0 !important; }
th, td { padding: 0.45em 0.6em; text-align: left; border-bottom: 1px solid #DAD6CC; }
th { font-weight: 600; border-bottom: 2px solid #1C2733; }
#counter { position: fixed; right: 16px; bottom: 12px; font: 14px -apple-system, Arial, sans-serif;
  color: #8A94A0; user-select: none; }
#notes { position: fixed; left: 0; right: 0; bottom: 0; max-height: 40%; overflow: auto;
  background: rgba(15, 21, 28, 0.94); color: #E6EAEE; font: 18px/1.5 -apple-system, Arial, sans-serif;
  padding: 20px 28px; display: none; }
#notes.on { display: block; }
@media print {
  @page { size: 1920px 1080px; margin: 0; }
  html, body { height: auto; overflow: visible; background: none; }
  section { position: relative; visibility: visible; transform: none !important;
    break-after: page; print-color-adjust: exact; -webkit-print-color-adjust: exact; }
  #counter, #notes { display: none; }
}
"""

STANDALONE_JS = """
const S = [...document.querySelectorAll('section')];
const counter = document.getElementById('counter');
const notes = document.getElementById('notes');
let cur = 0;
function fit() {
  const s = Math.min(innerWidth / 1920, innerHeight / 1080);
  const x = (innerWidth - 1920 * s) / 2, y = (innerHeight - 1080 * s) / 2;
  S.forEach(e => { e.style.transform = `translate(${x}px, ${y}px) scale(${s})`; });
}
function go(k) {
  cur = Math.max(0, Math.min(S.length - 1, k));
  S.forEach((e, j) => e.classList.toggle('on', j === cur));
  counter.textContent = `${cur + 1} / ${S.length}  ·  ← → navegar  ·  N notas`;
  const a = S[cur].querySelector('aside');
  notes.textContent = a ? a.textContent : '';
  history.replaceState(null, '', '#' + (cur + 1));
}
addEventListener('resize', fit);
addEventListener('keydown', e => {
  if (['ArrowRight', 'PageDown', ' '].includes(e.key)) go(cur + 1);
  else if (['ArrowLeft', 'PageUp'].includes(e.key)) go(cur - 1);
  else if (e.key === 'Home') go(0);
  else if (e.key === 'End') go(S.length - 1);
  else if (e.key === 'n' || e.key === 'N') notes.classList.toggle('on');
  else return;
  e.preventDefault();
});
addEventListener('click', e => {
  if (notes.contains(e.target)) return;
  go(e.clientX < innerWidth / 3 ? cur - 1 : cur + 1);
});
fit();
go((parseInt(location.hash.slice(1), 10) || 1) - 1);
"""


def write_standalone(slides, path):
    """Single HTML file: x-embeds become plain divs holding the SVG."""
    unwrap = re.compile(
        r'<x-embed style="([^"]*)"><meta charset="utf-8"><body style="[^"]*">(.*?)</body></x-embed>',
        re.DOTALL,
    )
    body = "\n".join(unwrap.sub(r'<div style="\1">\2</div>', s) for s in slides)
    families = "&".join(
        f["href"].split("?", 1)[1].replace("&display=swap", "") for f in FACES.values()
    )
    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{families}&display=swap">
<style>{STANDALONE_CSS}</style>
</head>
<body>
{body}
<div id="counter"></div>
<div id="notes"></div>
<script>{STANDALONE_JS}</script>
</body>
</html>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
]


def write_pdf(html_path, pdf_path):
    """Print the standalone deck with headless Chrome, one 1920x1080 page per
    slide (the @media print rules in STANDALONE_CSS do the layout)."""
    chrome = next(
        (c for c in CHROME_CANDIDATES if os.path.exists(c) or shutil.which(c)), None
    )
    if chrome is None:
        raise SystemExit("--pdf needs Google Chrome or Chromium installed")
    subprocess.run(
        [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--virtual-time-budget=15000",  # let the Google Fonts load
            f"--print-to-pdf={pdf_path}",
            "file://" + os.path.abspath(html_path),
        ],
        check=True,
        capture_output=True,
    )


def write_deck(slides, root):
    """Files for the Slides artifact: project/deck.json + project/slides/<id>.html."""
    sdir = os.path.join(root, "project", "slides")
    os.makedirs(sdir, exist_ok=True)
    for s in slides:
        with open(
            os.path.join(sdir, f"{slide_id(s)}.html"), "w", encoding="utf-8"
        ) as f:
            f.write(s)
    deck = {
        "v": 4,
        "createdOnFiles": {
            "v": 1,
            "at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "lists": "css",
        "title": TITLE,
        "order": [slide_id(s) for s in slides],
        "sections": {
            "intro": {
                "description": "O experimento e como ler os resultados",
                "start": "cover",
            },
            "base": {
                "description": "Linha de base: a identidade de Dunn e seu defeito central",
                "start": "defeito",
            },
            "onda1": {
                "description": "Onda 1, homotética: Esteban-Marquillas, efeito alocação "
                "e os dois modelos de Arcelus",
                "start": "onda1",
            },
            "onda2": {
                "description": "Onda 2, temporal: a controvérsia dos pesos e o "
                "shift-share dinâmico",
                "start": "onda2",
            },
            "onda3": {
                "description": "Onda 3, inferencial: Berzeg, full-analogue e Knudsen",
                "start": "onda3",
            },
            "espacial": {
                "description": "Extensão espacial de Nazara-Hewings",
                "start": "espacial",
            },
            "sintese": {
                "description": "Monte Carlo, cinco casos de UF e o balanço da abordagem",
                "start": "ranking",
            },
            "rais": {
                "description": "As mesmas variantes na RAIS 2022–2025, sem gabarito",
                "start": "rais-intro",
            },
            "anexo": {
                "description": "Quadro de parâmetros consolidados",
                "start": "parametros",
            },
        },
        "faces": FACES,
        "designSystems": [],
    }
    with open(os.path.join(root, "project", "deck.json"), "w", encoding="utf-8") as f:
        json.dump(deck, f, ensure_ascii=False, indent=1)


# ----------------------------------------------------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    ap.add_argument("--deck", help="also write the Slides-artifact files to DIR")
    ap.add_argument(
        "--pdf", action="store_true", help="also print the deck to PDF via Chrome"
    )
    args = ap.parse_args()

    slides = build_slides(collect())
    out = os.path.join(HERE, "apresentacao_shift_share.html")
    write_standalone(slides, out)
    print(f"Saved: {out} ({len(slides)} slides)")
    if args.pdf:
        pdf = os.path.splitext(out)[0] + ".pdf"
        write_pdf(out, pdf)
        print(f"Saved: {pdf}")
    if args.deck:
        write_deck(slides, args.deck)
        print(f"Saved Slides-artifact files under {args.deck}/project/")
