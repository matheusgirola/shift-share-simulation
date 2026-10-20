"""
ssa_models.py
=============
Implementations of the shift-share variants covered in the literature review.

All models take the employment array E with shape (R, I, T+1) and return a
per-region DataFrame with component estimates in EMPLOYMENT UNITS, so they
can be compared directly with the DGP ground truth.

Implemented variants
--------------------
1. classic_dunn          Dunn (1960) static identity; weight options:
                         'base' (classic), 'terminal' (Stilwell-flavoured),
                         'average' (Fuchs 1959).
2. esteban_marquillas    E-M (1972): homothetic employment, structure-free
                         competitive effect + allocation effect (static).
3. arcelus               Arcelus (1984, Model I): homothetic split of the
                         national and mix components (expected/differential).
4. dynamic_shift_share   Barff & Knight (1988): classic identity computed
                         annually and summed.
5. dynamic_em            Dynamic version of Esteban-Marquillas (annual
                         homothetic employment, summed).
6. berzeg_anova          Berzeg (1978, 1984) stochastic/ANOVA formulation:
                         WLS on annual growth rates; competitive rate = the
                         (weighted) region-mean residual, with a std. error.
7. full_analogue_regression
                         Buck-Atkins (1976) / Patterson (1991) style
                         "full-analogue" model: WLS of annual growth rates on
                         year, industry-year and region effects with
                         employment-weighted sum-to-zero constraints;
                         delivers t-statistics for the regional effect.

Not implemented (noted for reference): spatial shift-share (Nazara-Hewings
2004) needs a spatial weight matrix, i.e., a geography for the artificial
states; multifactor partitioning (Ray) and the Bartik IV serve different
questions (aggregation bias / causal identification).
"""

import numpy as np
import pandas as pd


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------
def _rates(E0, E1):
    """Safe growth rates between two cross-sections (R, I)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        g = np.where(E0 > 0, E1 / E0 - 1.0, 0.0)
    return g


def _homothetic(E_slice):
    """Homothetic employment for a cross-section (R, I):
    region total x national industry share."""
    reg_tot = E_slice.sum(axis=1, keepdims=True)  # (R,1)
    nat_share = E_slice.sum(axis=0) / E_slice.sum()  # (I,)
    return reg_tot * nat_share[None, :]


# ----------------------------------------------------------------------
# 1. Classic Dunn (static), with the three weighting schemes
# ----------------------------------------------------------------------
def classic_dunn(E, regions, weights="base"):
    """Static shift-share between year 0 and year T.

    weights: 'base'     -> classic Dunn, weights = E[.,.,0]
             'terminal' -> weights = E[.,.,T] deflated to base scale
             'average'  -> Fuchs: mean of base and terminal employment
    """
    T = E.shape[2] - 1
    E0, ET = E[:, :, 0], E[:, :, T]
    g_ri = _rates(E0, ET)  # regional-industry rates
    g_ni = ET.sum(0) / E0.sum(0) - 1.0  # national industry rates
    g_n = ET.sum() / E0.sum() - 1.0  # national all-industry rate

    if weights == "base":
        W = E0
    elif weights == "terminal":
        # deflate terminal employment back to base scale so components
        # still sum (approximately) to the observed change
        W = ET / (1.0 + g_n)
    elif weights == "average":
        W = 0.5 * (E0 + ET / (1.0 + g_n))
    else:
        raise ValueError(weights)

    NE = (W * g_n).sum(axis=1)
    IM = (W * (g_ni - g_n)[None, :]).sum(axis=1)
    CE = (W * (g_ri - g_ni[None, :])).sum(axis=1)
    out = pd.DataFrame(
        {"region": regions, "national": NE, "mix": IM, "competitive": CE}
    )
    out["total_explained"] = out[["national", "mix", "competitive"]].sum(axis=1)
    return out


# ----------------------------------------------------------------------
# 2. Esteban-Marquillas (1972), static
# ----------------------------------------------------------------------
def esteban_marquillas(E, regions):
    T = E.shape[2] - 1
    E0, ET = E[:, :, 0], E[:, :, T]
    g_ri = _rates(E0, ET)
    g_ni = ET.sum(0) / E0.sum(0) - 1.0
    g_n = ET.sum() / E0.sum() - 1.0
    E_star = _homothetic(E0)  # homothetic base employment

    NE = (E0 * g_n).sum(axis=1)
    IM = (E0 * (g_ni - g_n)[None, :]).sum(axis=1)
    CE_star = (E_star * (g_ri - g_ni[None, :])).sum(
        axis=1
    )  # structure-free competitive
    AE = ((E0 - E_star) * (g_ri - g_ni[None, :])).sum(axis=1)  # allocation effect
    out = pd.DataFrame(
        {
            "region": regions,
            "national": NE,
            "mix": IM,
            "competitive": CE_star,
            "allocation": AE,
        }
    )
    out["total_explained"] = out[["national", "mix", "competitive", "allocation"]].sum(
        axis=1
    )
    return out


# ----------------------------------------------------------------------
# 3. Arcelus (1984), Model I: homothetic split of every component
# ----------------------------------------------------------------------
def arcelus(E, regions):
    T = E.shape[2] - 1
    E0, ET = E[:, :, 0], E[:, :, T]
    g_ri = _rates(E0, ET)
    g_ni = ET.sum(0) / E0.sum(0) - 1.0
    g_n = ET.sum() / E0.sum() - 1.0
    E_star = _homothetic(E0)
    dE = E0 - E_star

    EN = (E_star * g_n).sum(1)  # expected national growth
    DN = (dE * g_n).sum(1)  # differential national growth
    EM = (E_star * (g_ni - g_n)[None, :]).sum(1)  # expected industry mix
    DM = (dE * (g_ni - g_n)[None, :]).sum(1)  # differential industry mix
    CE = (E_star * (g_ri - g_ni[None, :])).sum(1)  # competitive (as in E-M)
    AE = (dE * (g_ri - g_ni[None, :])).sum(1)  # allocation (as in E-M)
    out = pd.DataFrame(
        {
            "region": regions,
            "national": EN + DN,
            "expected_national": EN,
            "differential_national": DN,
            "mix": EM + DM,
            "expected_mix": EM,
            "differential_mix": DM,
            "competitive": CE,
            "allocation": AE,
        }
    )
    out["total_explained"] = out[["national", "mix", "competitive", "allocation"]].sum(
        axis=1
    )
    return out


# ----------------------------------------------------------------------
# 4. Dynamic shift-share (Barff & Knight 1988)
# ----------------------------------------------------------------------
def dynamic_shift_share(E, regions):
    R, _, Tp1 = E.shape
    NE = np.zeros(R)
    IM = np.zeros(R)
    CE = np.zeros(R)
    for t in range(Tp1 - 1):
        E0, E1 = E[:, :, t], E[:, :, t + 1]
        g_ri = _rates(E0, E1)
        g_ni = E1.sum(0) / E0.sum(0) - 1.0
        g_n = E1.sum() / E0.sum() - 1.0
        NE += (E0 * g_n).sum(1)
        IM += (E0 * (g_ni - g_n)[None, :]).sum(1)
        CE += (E0 * (g_ri - g_ni[None, :])).sum(1)
    out = pd.DataFrame(
        {"region": regions, "national": NE, "mix": IM, "competitive": CE}
    )
    out["total_explained"] = out[["national", "mix", "competitive"]].sum(axis=1)
    return out


# ----------------------------------------------------------------------
# 5. Dynamic Esteban-Marquillas
# ----------------------------------------------------------------------
def dynamic_em(E, regions):
    R, _, Tp1 = E.shape
    NE = np.zeros(R)
    IM = np.zeros(R)
    CE = np.zeros(R)
    AE = np.zeros(R)
    for t in range(Tp1 - 1):
        E0, E1 = E[:, :, t], E[:, :, t + 1]
        g_ri = _rates(E0, E1)
        g_ni = E1.sum(0) / E0.sum(0) - 1.0
        g_n = E1.sum() / E0.sum() - 1.0
        E_star = _homothetic(E0)
        NE += (E0 * g_n).sum(1)
        IM += (E0 * (g_ni - g_n)[None, :]).sum(1)
        CE += (E_star * (g_ri - g_ni[None, :])).sum(1)
        AE += ((E0 - E_star) * (g_ri - g_ni[None, :])).sum(1)
    out = pd.DataFrame(
        {
            "region": regions,
            "national": NE,
            "mix": IM,
            "competitive": CE,
            "allocation": AE,
        }
    )
    out["total_explained"] = out[["national", "mix", "competitive", "allocation"]].sum(
        axis=1
    )
    return out


# ----------------------------------------------------------------------
# 6. Berzeg (1978/1984) stochastic / ANOVA shift-share
# ----------------------------------------------------------------------
def berzeg_anova(E, regions):
    """Annual growth rates g[r,i,t] modelled as
           g = (year effect) + (industry-year effect) + residual
    estimated by employment-weighted least squares. The residual, averaged
    (employment-weighted) within a region, is the competitive RATE estimate,
    and its standard error allows a t-test (Berzeg's key contribution).
    Components are converted to employment units with the actual weights.
    """
    R, I, Tp1 = E.shape
    T = Tp1 - 1
    # long arrays
    g = np.zeros((R, I, T))
    W = np.zeros((R, I, T))
    for t in range(T):
        g[:, :, t] = _rates(E[:, :, t], E[:, :, t + 1])
        W[:, :, t] = E[:, :, t]

    # weighted year effects (national rate per year) and industry-year effects
    g_n_t = (W * g).sum(axis=(0, 1)) / W.sum(axis=(0, 1))  # (T,)
    g_ni_t = (W * g).sum(axis=0) / W.sum(axis=0)  # (I,T)
    resid = g - g_ni_t[None, :, :]  # competitive + noise

    # per-region weighted mean residual = competitive rate estimate
    w_r = W.sum(axis=(1, 2))
    c_hat = (W * resid).sum(axis=(1, 2)) / w_r
    # weighted std error of the mean
    dev = resid - c_hat[:, None, None]
    var_w = (W * dev**2).sum(axis=(1, 2)) / w_r
    n_eff = w_r**2 / (W**2).sum(axis=(1, 2))  # effective n
    se = np.sqrt(var_w / np.maximum(n_eff - 1, 1))
    t_stat = c_hat / se

    # employment-unit components using actual annual weights
    NE = (W * g_n_t[None, None, :]).sum(axis=(1, 2))
    IM = (W * (g_ni_t - g_n_t[None, :])[None, :, :]).sum(axis=(1, 2))
    CE = (W * resid).sum(axis=(1, 2))
    out = pd.DataFrame(
        {
            "region": regions,
            "national": NE,
            "mix": IM,
            "competitive": CE,
            "comp_rate": c_hat,
            "comp_rate_se": se,
            "comp_t": t_stat,
            "significant_5pct": np.abs(t_stat) > 1.96,
        }
    )
    out["total_explained"] = out[["national", "mix", "competitive"]].sum(axis=1)
    return out


# ----------------------------------------------------------------------
# 7. Full-analogue regression (Buck-Atkins 1976 / Patterson 1991 style)
# ----------------------------------------------------------------------
def full_analogue_regression(E, regions, sectors):
    """WLS of annual growth rates on year FE + industry FE + region FE,
    with employment-weighted sum-to-zero constraints on the industry and
    region effects, so:
        year FE           ~ national effect
        industry FE       ~ mix rate
        region FE         ~ competitive rate  (with std. error / t-stat)
    Statsmodels WLS provides classical inference.
    """
    import statsmodels.api as sm

    R, I, Tp1 = E.shape
    T = Tp1 - 1
    rows = []
    for t in range(T):
        g = _rates(E[:, :, t], E[:, :, t + 1])
        for r in range(R):
            for i in range(I):
                rows.append((regions[r], sectors[i], t, g[r, i], E[r, i, t]))
    df = pd.DataFrame(rows, columns=["region", "sector", "year", "g", "w"])

    # design: year dummies (full), sector dummies (drop one), region dummies (drop one)
    X = pd.get_dummies(df[["year", "sector", "region"]].astype(str), drop_first=False)
    # drop-first manually for sector and region to avoid collinearity
    X = X.drop(columns=[f"sector_{sectors[0]}", f"region_{regions[0]}"])
    X = sm.add_constant(X.astype(float))
    res = sm.WLS(df["g"], X, weights=df["w"]).fit()

    # recover region effects relative to weighted mean (sum-to-zero recentering)
    reg_cols = [c for c in X.columns if c.startswith("region_")]
    coefs = pd.Series(0.0, index=[f"region_{r}" for r in regions])
    coefs.update(res.params[reg_cols])
    w_r = df.groupby("region")["w"].sum().reindex(regions).to_numpy()
    raw = coefs.reindex([f"region_{r}" for r in regions]).to_numpy()
    c_hat = raw - np.average(raw, weights=w_r)  # weighted sum-to-zero

    # standard errors: reference region has se from re-centering; use the
    # coefficient SEs for the included dummies, pooled se for the base region
    se = pd.Series(np.nan, index=[f"region_{r}" for r in regions])
    se.update(res.bse[reg_cols])
    se.iloc[0] = res.bse[reg_cols].median()
    se = se.values
    t_stat = c_hat / se

    # convert competitive rate to employment units with actual weights
    CE = c_hat * w_r
    out = pd.DataFrame(
        {
            "region": regions,
            "competitive": CE,
            "comp_rate": c_hat,
            "comp_rate_se": se,
            "comp_t": t_stat,
            "significant_5pct": np.abs(t_stat) > 1.96,
        }
    )
    return out, res


# ----------------------------------------------------------------------
# 8. Spatial shift-share (Nazara & Hewings 2004)
# ----------------------------------------------------------------------
def nazara_hewings(E, regions, W):
    """Static spatial shift-share between year 0 and year T.

    Nazara-Hewings replace the single national benchmark in the competitive
    term with the growth rate of industry i in region r's NEIGHBORHOOD,
    g_tilde[r,i] = sum_k W[r,k] * g[k,i]  (row-standardized contiguity W),
    splitting the classic competitive effect into:

        neighborhood effect : E0 * (g_tilde - g_ni)   spatial spillover --
                              is my neighborhood outgrowing the nation?
        own-net competitive : E0 * (g_ri - g_tilde)   am I outgrowing my
                              own neighborhood?

    National and mix effects are as in Dunn, so additivity is preserved:
    NE + IM + NEIGH + OWN = observed change.
    """
    T = E.shape[2] - 1
    E0, ET = E[:, :, 0], E[:, :, T]
    g_ri = _rates(E0, ET)
    g_ni = ET.sum(0) / E0.sum(0) - 1.0
    g_n = ET.sum() / E0.sum() - 1.0
    g_tilde = W @ g_ri  # neighborhood rates (R, I)

    NE = (E0 * g_n).sum(1)
    IM = (E0 * (g_ni - g_n)[None, :]).sum(1)
    NEIGH = (E0 * (g_tilde - g_ni[None, :])).sum(1)
    OWN = (E0 * (g_ri - g_tilde)).sum(1)
    out = pd.DataFrame(
        {
            "region": regions,
            "national": NE,
            "mix": IM,
            "neighborhood": NEIGH,
            "own_net": OWN,
            "competitive": NEIGH + OWN,
        }
    )
    out["total_explained"] = out[["national", "mix", "competitive"]].sum(axis=1)
    return out


def dynamic_nazara_hewings(E, regions, W):
    """Barff-Knight-style annual computation of the Nazara-Hewings
    decomposition, summed over years."""
    R, _, Tp1 = E.shape
    NE = np.zeros(R)
    IM = np.zeros(R)
    NEIGH = np.zeros(R)
    OWN = np.zeros(R)
    for t in range(Tp1 - 1):
        E0, E1 = E[:, :, t], E[:, :, t + 1]
        g_ri = _rates(E0, E1)
        g_ni = E1.sum(0) / E0.sum(0) - 1.0
        g_n = E1.sum() / E0.sum() - 1.0
        g_tilde = W @ g_ri
        NE += (E0 * g_n).sum(1)
        IM += (E0 * (g_ni - g_n)[None, :]).sum(1)
        NEIGH += (E0 * (g_tilde - g_ni[None, :])).sum(1)
        OWN += (E0 * (g_ri - g_tilde)).sum(1)
    out = pd.DataFrame(
        {
            "region": regions,
            "national": NE,
            "mix": IM,
            "neighborhood": NEIGH,
            "own_net": OWN,
            "competitive": NEIGH + OWN,
        }
    )
    out["total_explained"] = out[["national", "mix", "competitive"]].sum(axis=1)
    return out
