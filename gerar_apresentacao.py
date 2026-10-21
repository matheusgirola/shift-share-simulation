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
  --deck DIR                      also write the Slides-artifact files
                                  (DIR/project/deck.json, DIR/project/slides/)

Run with: uv run python gerar_apresentacao.py [--deck DIR]
"""

import argparse
import json
import math
import os
import re
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
            for col in ("competitive", "allocation", "neighborhood", "own_net")
            if col in e.columns
        }
        if "significant_5pct" in e.columns:
            est[name]["sig"] = e["significant_5pct"].astype(bool).tolist()
    mc = pd.read_csv(os.path.join(HERE, "results_montecarlo.csv"))
    return {
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


def legend_svg(y, sig=False):
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


def single_chart(title, labels, truth, est, sig=None):
    body = legend_svg(30, sig is not None) + panel_svg(
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
def footer(n):
    return (
        f'<p style="position:absolute;left:128px;bottom:56px;width:1300px;font-size:24px;color:{MUTED}">'
        f"Simulação semente 42 · 27 UFs × 5 setores × 10 anos · valores em mil empregos</p>"
        f'<p style="position:absolute;right:128px;bottom:56px;width:120px;font-size:24px;color:{MUTED};text-align:right">{n}</p>'
    )


def stat(value, label):
    return (
        f'<div style="flex:1;display:flex;flex-direction:column;gap:4px">'
        f'<p style="font-family:{SERIF};font-size:52px;font-weight:600;line-height:1.05;color:{INK}">{value}</p>'
        f'<p style="font-size:24px;line-height:1.25;color:{MUTED}">{label}</p></div>'
    )


def model_slide(sid, n, eyebrow, title, desc, formula, stats, extra, chart, notes):
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
{footer(n)}
<aside>{notes}</aside>
</section>"""


# ----------------------------------------------------------------------
# slides
# ----------------------------------------------------------------------
def build_slides(D):
    REGS = D["regions"]
    REC, MC, SIG, EST = D["rec"], D["mc"], D["sigdiag"], D["est"]
    T = D["truth"]
    TC, TH = T["true_comp"], T["true_comp_homothetic"]
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
<p style="font-size:26px;line-height:1.45;color:{SOFT}">Cada modelo é avaliado contra o alvo que diz estimar: Esteban-Marquillas e Arcelus contra o efeito competitivo <b>homotético</b> verdadeiro; os demais contra o efeito competitivo verdadeiro.</p>
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
            "Arcelus (1984)",
            "homotetia só no competitivo",
            "DN e EM nulos por construção",
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

    n = 5
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
    M = "Classic Dunn (terminal wts)"
    slides.append(
        model_slide(
            "terminal",
            n,
            "Controvérsia dos pesos · Stilwell",
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
            "Controvérsia dos pesos · Fuchs",
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
            "Arcelus I",
            "Estende a partição homotética aos efeitos nacional e de composição. Somados por UF, dois dos quatro novos termos se anulam identicamente.",
            "NE = E*·gₙ + (E₀−E*)·gₙ<br>IM = E*·(gₙᵢ−gₙ) + (E₀−E*)·(gₙᵢ−gₙ)",
            metrics(M),
            [
                mc_line(M),
                "Na simulação, |DN| e |EM| ficam abaixo de 10⁻⁹ em todas as UFs: o efeito competitivo é o mesmo de Esteban-Marquillas.",
            ],
            chart(CTH, TH, comp(M)),
            "Seção 7 da nota. A propriedade algébrica da Seção 7.3 aparece na simulação: o termo diferencial nacional e o termo esperado de composição somam zero por UF. Por isso Arcelus I e Esteban-Marquillas estático têm exatamente as mesmas estimativas e as mesmas métricas.",
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
            "Mínima informação discriminante: modelo log-linear estimado como GLM de Poisson com offset ln E₀, uma única transição de dez anos.",
            "ln(E₁/E₀) = A + Oᵢ + Dᵣ<br>CE = (e^D̃ᵣ − 1)·Wᵣ",
            metrics(M),
            [sig_line(M), mc_line(M)],
            chart(CT, TC, comp(M), sig(M)),
            "Seção 10 da nota, equação 18 de Knudsen (2000). Erros-padrão quase-Poisson (dispersão de Pearson), recentragem ponderada de D e conversão em empregos são adaptações da implementação. Na semente 42 tem a maior correlação de todas, mas no Monte Carlo fica atrás de Dunn com pesos-base em magnitude.",
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
            "Equação 19 de Knudsen (2000). A forma dinâmica acompanha quase exatamente a regressão full-analogue: as taxas competitivas se correlacionam a 0,99999. A dispersão estimada é cerca de 5, por isso a correção quase-Poisson importa.",
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
<aside>Monte Carlo de 50 sementes por cenário (results_montecarlo.csv), ordenado pelo nRMSE no cenário de estresse. Berzeg, Barff-Knight e Nazara-Hewings dinâmico têm o mesmo efeito competitivo total; Esteban-Marquillas e Arcelus também coincidem.</aside>
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

    # conclusions
    concl = [
        (
            "Ordenação robusta",
            "Todas as variantes ordenam as UFs quase igual (r de 0,95 a 0,99), como Knudsen e Barff (1991) previam.",
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
            "Limite do laboratório",
            "A verdade aqui é constante no tempo; na prática o efeito competitivo oscila, então estes resultados são um teto.",
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
<h2 style="font-family:{SERIF};font-size:64px;font-weight:600;line-height:1.1;color:{BG}">O que a simulação confirma da literatura</h2>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:28px">{ch}</div>
<aside>Nenhum destes resultados valida a SSA como ferramenta de previsão ou causal: ela continua sendo uma identidade contábil. A nota sugere, como próximos passos, testar outras matrizes W, vantagens específicas por setor com estrutura espacial e um passo de econometria espacial.</aside>
</section>"""
    )
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
    with open(path, "w") as f:
        f.write(html)


def write_deck(slides, root):
    """Files for the Slides artifact: project/deck.json + project/slides/<id>.html."""
    sdir = os.path.join(root, "project", "slides")
    os.makedirs(sdir, exist_ok=True)
    for s in slides:
        with open(os.path.join(sdir, f"{slide_id(s)}.html"), "w") as f:
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
            "classico": {
                "description": "Decomposição clássica e a controvérsia dos pesos",
                "start": "dunn",
            },
            "homotetica": {
                "description": "Reformulação homotética: Esteban-Marquillas e Arcelus",
                "start": "em",
            },
            "dinamica": {"description": "Shift-share dinâmico", "start": "bk"},
            "inferencial": {
                "description": "Formas inferenciais: Berzeg, full-analogue e Knudsen",
                "start": "berzeg",
            },
            "espacial": {
                "description": "Extensão espacial de Nazara-Hewings",
                "start": "nh-s",
            },
            "sintese": {
                "description": "Síntese do Monte Carlo e conclusões",
                "start": "ranking",
            },
        },
        "faces": FACES,
        "designSystems": [],
    }
    with open(os.path.join(root, "project", "deck.json"), "w") as f:
        json.dump(deck, f, ensure_ascii=False, indent=1)


# ----------------------------------------------------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    ap.add_argument("--deck", help="also write the Slides-artifact files to DIR")
    args = ap.parse_args()

    slides = build_slides(collect())
    out = os.path.join(HERE, "apresentacao_shift_share.html")
    write_standalone(slides, out)
    print(f"Saved: {out} ({len(slides)} slides)")
    if args.deck:
        write_deck(slides, args.deck)
        print(f"Saved Slides-artifact files under {args.deck}/project/")
