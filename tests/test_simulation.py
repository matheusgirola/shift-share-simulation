import numpy as np
import pytest

import ssa_models as M
from ssa_dgp import generate_dataset


@pytest.fixture(scope="module")
def data():
    return generate_dataset(seed=42, rho_space=0.5)


def test_true_components_sum_to_observed_change(data):
    t = data["truth"]
    total = t[["true_national", "true_mix", "true_comp", "true_noise"]].sum(axis=1)
    assert np.allclose(total, t["delta_E"])


@pytest.mark.parametrize(
    "model",
    [
        lambda d: M.classic_dunn(d["E"], d["regions"], "base"),
        lambda d: M.esteban_marquillas(d["E"], d["regions"]),
        lambda d: M.dynamic_shift_share(d["E"], d["regions"]),
        lambda d: M.nazara_hewings(d["E"], d["regions"], d["W"]),
        lambda d: M.arcelus_ii(d["E"], d["regions"]),
    ],
)
def test_identity_models_reproduce_observed_change(data, model):
    est = model(data)
    assert np.allclose(est["total_explained"], data["truth"]["delta_E"])


def test_berzeg_point_estimates_match_barff_knight(data):
    bk = M.dynamic_shift_share(data["E"], data["regions"])
    berzeg = M.berzeg_anova(data["E"], data["regions"])
    assert np.allclose(bk["competitive"], berzeg["competitive"])


def test_arcelus_extra_terms_vanish(data):
    arc = M.arcelus(data["E"], data["regions"])
    assert np.allclose(arc["differential_national"], 0)
    assert np.allclose(arc["expected_mix"], 0)


def test_arcelus_ii_partitions_the_dunn_competitive(data):
    """r_ri + d_ri = CE_ri: Model II splits Dunn's competitive effect."""
    dunn = M.classic_dunn(data["E"], data["regions"], "base")
    a2 = M.arcelus_ii(data["E"], data["regions"])
    assert np.allclose(
        a2["regional_shift"] + a2["differential_shift"], a2["competitive"]
    )
    assert np.allclose(a2["competitive"], dunn["competitive"])
    assert np.allclose(a2["mix"], dunn["mix"])


def test_arcelus_ii_split_degenerates_in_the_regional_aggregate(data):
    """d_r == -mix_r and r_r == mix_r + CE_r, identically (note, Section 7.4)."""
    a2 = M.arcelus_ii(data["E"], data["regions"])
    assert np.allclose(a2["differential_shift"], -a2["mix"])
    assert np.allclose(a2["regional_shift"], a2["mix"] + a2["competitive"])
    assert abs(a2["regional_shift"].sum()) < 1e-6 * a2["national"].sum()


def test_arcelus_ii_is_not_arcelus_i(data):
    """The two models estimate different objects, so they must not coincide."""
    a1 = M.arcelus(data["E"], data["regions"])
    a2 = M.arcelus_ii(data["E"], data["regions"])
    assert not np.allclose(a1["competitive"], a2["competitive"])


def test_arcelus_ii_truth_splits_the_true_competitive(data):
    t = data["truth"]
    assert np.allclose(t["true_reg_shift"] + t["true_diff_shift"], t["true_comp"])


@pytest.mark.parametrize("dynamic", [False, True])
def test_knudsen_estimates_do_not_depend_on_units(data, dynamic):
    E, regs, secs = data["E"], data["regions"], data["sectors"]
    jobs, _ = M.knudsen_mdi(E, regs, secs, dynamic=dynamic)
    thousands, _ = M.knudsen_mdi(E / 1000, regs, secs, dynamic=dynamic)
    assert np.allclose(jobs["log_effect"], thousands["log_effect"])
    assert np.allclose(jobs["comp_t"], thousands["comp_t"])


def test_knudsen_regional_effects_are_weight_centred(data):
    E, regs, secs = data["E"], data["regions"], data["sectors"]
    est, _ = M.knudsen_mdi(E, regs, secs, dynamic=True)
    w_r = E[:, :, :-1].sum(axis=(1, 2))
    assert abs(np.average(est["log_effect"], weights=w_r)) < 1e-12


@pytest.mark.filterwarnings(
    "ignore::statsmodels.tools.sm_exceptions.SingularMatrixWarning"
)
def test_knudsen_dynamic_matches_full_analogue_rates(data):
    E, regs, secs = data["E"], data["regions"], data["sectors"]
    kn, _ = M.knudsen_mdi(E, regs, secs, dynamic=True)
    far, _ = M.full_analogue_regression(E, regs, secs)
    assert np.corrcoef(kn["comp_rate"], far["comp_rate"])[0, 1] > 0.999
