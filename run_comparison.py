"""
run_comparison.py
=================
Generate the artificial dataset (27 states x 5 sectors x 10 years),
run every shift-share variant, and score each against the DGP ground truth.

Metrics (region-level, for the competitive component unless noted):
  pearson   correlation between estimated and true component
  spearman  rank correlation (does the model rank regions correctly?)
  nrmse     RMSE / std(truth)  -- < 1 means better than guessing the mean
  sign_acc  share of regions whose estimated sign matches the true sign

For the inferential models (Berzeg ANOVA, full-analogue regression, Knudsen
MDI) we also report significance diagnostics: among regions whose TRUE
competitive rate |c_bar| is in the top/bottom tercile, how often is the effect
flagged significant (power proxy), and how often are near-zero regions flagged
(false-positive proxy).

Outputs (written next to this script):
  results_single_run.csv     component estimates + truth, seed 42
  results_recovery.csv       recovery metrics, single run
  results_montecarlo.csv     metrics averaged over N_SIM seeds
  recovery_chart.png         visual summary
"""

import re

import numpy as np
import pandas as pd
from scipy import stats

import ssa_models as M
from ssa_dgp import generate_dataset


# ----------------------------------------------------------------------
def score(est, truth, est_col="competitive", true_col="true_comp"):
    x = est.set_index("region")[est_col].reindex(truth["region"]).values
    y = truth[true_col].values
    return {
        "pearson": stats.pearsonr(x, y)[0],
        "spearman": stats.spearmanr(x, y)[0],
        "nrmse": np.sqrt(np.mean((x - y) ** 2)) / np.std(y),
        "sign_acc": np.mean(np.sign(x) == np.sign(y)),
    }


def run_all_models(data):
    E, regs, secs, W = data["E"], data["regions"], data["sectors"], data["W"]
    out = {}
    out["Classic Dunn (base wts)"] = M.classic_dunn(E, regs, "base")
    out["Classic Dunn (terminal wts)"] = M.classic_dunn(E, regs, "terminal")
    out["Classic Dunn (avg wts, Fuchs)"] = M.classic_dunn(E, regs, "average")
    out["Esteban-Marquillas (static)"] = M.esteban_marquillas(E, regs)
    out["Arcelus I (static)"] = M.arcelus(E, regs)
    out["Dynamic (Barff-Knight)"] = M.dynamic_shift_share(E, regs)
    out["Dynamic Esteban-Marquillas"] = M.dynamic_em(E, regs)
    out["Berzeg ANOVA (stochastic)"] = M.berzeg_anova(E, regs)
    far, _ = M.full_analogue_regression(E, regs, secs)
    out["Full-analogue regression"] = far
    out["Nazara-Hewings spatial (static)"] = M.nazara_hewings(E, regs, W)
    out["Nazara-Hewings spatial (dynamic)"] = M.dynamic_nazara_hewings(E, regs, W)
    kn_static, _ = M.knudsen_mdi(E, regs, secs, dynamic=False)
    out["Knudsen MDI (static)"] = kn_static
    kn_dynamic, _ = M.knudsen_mdi(E, regs, secs, dynamic=True)
    out["Knudsen MDI (dynamic)"] = kn_dynamic
    return out


def recovery_table(models, truth):
    rows = []
    for name, est in models.items():
        # which truth does this model's "competitive" target?
        homothetic = ("Esteban" in name) or ("Arcelus" in name)
        tc = "true_comp_homothetic" if homothetic else "true_comp"
        rec = {"model": name, "target": tc, **score(est, truth, "competitive", tc)}
        # mix recovery where available
        if "mix" in est.columns:
            rec.update(
                {f"mix_{k}": v for k, v in score(est, truth, "mix", "true_mix").items()}
            )
        # allocation recovery where available
        if "allocation" in est.columns:
            rec.update(
                {
                    f"alloc_{k}": v
                    for k, v in score(est, truth, "allocation", "true_alloc").items()
                }
            )
        # spatial split recovery (Nazara-Hewings models)
        if "neighborhood" in est.columns:
            rec.update(
                {
                    f"neigh_{k}": v
                    for k, v in score(est, truth, "neighborhood", "true_neigh").items()
                }
            )
            rec.update(
                {
                    f"own_{k}": v
                    for k, v in score(est, truth, "own_net", "true_own_net").items()
                }
            )
        rows.append(rec)
    return pd.DataFrame(rows)


def moran_table(models, data, n_perm=999):
    """Moran's I of the true regional rates and of each model's estimated
    competitive RATE: can the models *detect* the spatial structure?

    Note: the test must run on rates, not employment-unit levels -- levels
    are dominated by state size (a big state with a modest advantage shows
    a huge absolute competitive effect), which drowns the spatial signal.
    Each model's implied rate = competitive component / employment-years.
    """
    from brazil_geo import morans_i

    W = data["W"]
    truth = data["truth"]
    T = data["n_years"]
    w_r = data["E"][:, :, :T].sum(axis=(1, 2))  # employment-years per state
    rows = [
        {
            "series": "TRUE c_bar (regional rate)",
            **dict(zip(("morans_I", "p_value"), morans_i(data["c_bar"], W, n_perm))),
        }
    ]
    for name, est in models.items():
        lvl = est.set_index("region")["competitive"].reindex(truth["region"]).values
        I, p = morans_i(lvl / w_r, W, n_perm)
        rows.append({"series": name + " [rate]", "morans_I": I, "p_value": p})
    return pd.DataFrame(rows)


def significance_diagnostics(models, data):
    """Power / false-positive proxies for the inferential models."""
    truth = data["truth"]
    c = np.abs(truth["c_bar"].values)
    strong = c >= np.quantile(c, 2 / 3)  # top tercile of |true rate|
    weak = c <= np.quantile(c, 1 / 3)  # bottom tercile
    rows = []
    for name, est in models.items():
        if "significant_5pct" not in est.columns:
            continue
        sig = (
            est.set_index("region")["significant_5pct"]
            .reindex(truth["region"])
            .values.astype(bool)
        )
        rows.append(
            {
                "model": name,
                "power_strong_regions": sig[strong].mean(),
                "flag_rate_weak_regions": sig[weak].mean(),
                "share_flagged_overall": sig.mean(),
            }
        )
    return pd.DataFrame(rows)


SCENARIOS = {
    # benign: smooth growth, mild noise, spatially correlated advantages
    "benign": {"rho_space": 0.5},
    # stress: volatile national cycle, strong yearly industry swings, more
    # idiosyncratic noise -- the setting where the literature says the
    # static endpoint models break down (Barff-Knight 1988)
    "stress": {
        "rho_space": 0.5,
        "sd_national": 0.035,
        "sd_mix": 0.035,
        "sd_mix_wobble": 0.020,
        "sd_eps": 0.015,
    },
    # no_space: rho = 0 falsification -- the Nazara-Hewings neighborhood
    # effect should collapse toward noise when no spatial structure exists
    "no_space": {"rho_space": 0.0},
}


def monte_carlo(n_sim=50, base_seed=1000, scenario="benign"):
    all_rows = []
    for s in range(n_sim):
        data = generate_dataset(seed=base_seed + s, **SCENARIOS[scenario])
        models = run_all_models(data)
        rt = recovery_table(models, data["truth"])
        rt["seed"] = base_seed + s
        all_rows.append(rt)
    mc = pd.concat(all_rows, ignore_index=True)
    metric_cols = [c for c in mc.columns if c not in ("model", "target", "seed")]
    summary = mc.groupby("model")[metric_cols].agg(["mean", "std"])
    summary.columns = ["_".join(c) for c in summary.columns]
    return summary.reset_index(), mc


def make_chart(mc_summary, path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    df = mc_summary.sort_values("pearson_mean")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5), sharey=True)
    axes[0].barh(
        df["model"], df["pearson_mean"], xerr=df["pearson_std"], color="#4878cf"
    )
    axes[0].set_title(
        "Competitive effect: correlation with truth\n(mean ± sd over 50 simulations)"
    )
    axes[0].set_xlabel("Pearson r")
    axes[0].set_xlim(0, 1.05)
    axes[1].barh(df["model"], df["nrmse_mean"], xerr=df["nrmse_std"], color="#d1615d")
    axes[1].set_title("Competitive effect: normalized RMSE\n(lower is better)")
    axes[1].set_xlabel("RMSE / sd(truth)")
    for ax in axes:
        ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ----------------------------------------------------------------------
if __name__ == "__main__":
    # ---- single detailed run (with spatial structure) ----
    data = generate_dataset(seed=42, rho_space=0.5)
    truth = data["truth"]
    models = run_all_models(data)

    # save estimates side by side with truth
    wide = truth.copy()
    for name, est in models.items():
        tag = re.sub(r"\W+", "_", name).strip("_")
        wide[f"comp__{tag}"] = (
            est.set_index("region")["competitive"].reindex(truth["region"]).values
        )
    wide.to_csv("results_single_run.csv", index=False)

    rt = recovery_table(models, truth)
    rt.to_csv("results_recovery.csv", index=False)
    print("=== Recovery of the COMPETITIVE effect (single run, seed 42) ===")
    print(
        rt[["model", "pearson", "spearman", "nrmse", "sign_acc"]]
        .round(3)
        .to_string(index=False)
    )

    sig = significance_diagnostics(models, data)
    print("\n=== Significance diagnostics (inferential models) ===")
    print(sig.round(3).to_string(index=False))

    # spatial diagnostics
    nh_cols = ["model", "neigh_pearson", "neigh_nrmse", "own_pearson", "own_nrmse"]
    nh = rt[rt["model"].str.contains("Nazara")]
    print("\n=== Nazara-Hewings spatial split recovery (rho_space = 0.5) ===")
    print(nh[nh_cols].round(3).to_string(index=False))

    mt = moran_table(models, data)
    mt.to_csv("results_morans_i.csv", index=False)
    print("\n=== Moran's I of competitive-effect estimates (999 permutations) ===")
    print(mt.round(3).to_string(index=False))

    # allocation effect check by design group
    em = models["Esteban-Marquillas (static)"].set_index("region")
    grp = truth.set_index("region")["group"]
    print("\n=== Mean allocation effect by DGP group (E-M static) ===")
    print(
        pd.DataFrame(
            {
                "estimated_AE": em["allocation"],
                "true_AE": truth.set_index("region")["true_alloc"],
                "group": grp,
            }
        )
        .groupby("group")
        .mean()
        .round(1)
    )

    # ---- Monte Carlo: benign and stress scenarios ----
    cols = [
        "model",
        "pearson_mean",
        "pearson_std",
        "nrmse_mean",
        "nrmse_std",
        "sign_acc_mean",
    ]
    summaries = {}
    for scen in SCENARIOS:
        print(f"\nRunning Monte Carlo (50 seeds, scenario: {scen})...")
        mc_summary, _ = monte_carlo(n_sim=50, scenario=scen)
        mc_summary["scenario"] = scen
        summaries[scen] = mc_summary
        print(f"\n=== Monte Carlo ({scen}): competitive-effect recovery ===")
        print(
            mc_summary[cols].sort_values("nrmse_mean").round(3).to_string(index=False)
        )
        nh_cols = [
            "model",
            "neigh_pearson_mean",
            "neigh_nrmse_mean",
            "own_pearson_mean",
            "own_nrmse_mean",
        ]
        if "neigh_pearson_mean" in mc_summary.columns:
            nh = mc_summary[mc_summary["model"].str.contains("Nazara")]
            print(f"--- Nazara-Hewings spatial split ({scen}) ---")
            print(nh[nh_cols].round(3).to_string(index=False))
    pd.concat(summaries.values()).to_csv("results_montecarlo.csv", index=False)

    make_chart(summaries["stress"], "recovery_chart.png")
    print(
        "\nSaved: results_single_run.csv, results_recovery.csv, "
        "results_montecarlo.csv, recovery_chart.png"
    )
