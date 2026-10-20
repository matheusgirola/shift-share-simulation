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
