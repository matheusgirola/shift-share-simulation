"""Checks on the real RAIS panel: that the committed aggregate is intact and
that the shift-share identities still close on numbers nobody designed."""

import numpy as np
import pytest

import rais_data as RD
import ssa_models as M
from brazil_geo import UFS


@pytest.fixture(scope="module")
def panel():
    return RD.load_panel(years=RD.YEARS, level="secao")


def test_panel_covers_every_state_sector_year(panel):
    E = panel["E"]
    assert E.shape == (27, 18, 4)  # section O, T and U dropped by default
    assert panel["regions"] == list(UFS)  # order must match the W matrix
    assert (E > 0).all(), "a zero cell would break the Poisson offset ln E0"


def test_employment_totals_grow_monotonically(panel):
    tot = panel["E"].sum(axis=(0, 1))
    assert (np.diff(tot) > 0).all()
    assert 40e6 < tot[0] < 50e6  # ~44.1 million active links in 2022


def test_all_21_sections_are_mapped_and_partitioned():
    divisions = [d for _, lo, hi in RD.SECOES.values() for d in range(lo, hi + 1)]
    assert len(divisions) == len(set(divisions)), "a division in two sections"
    assert set(RD.SECOES) == {s for ss in RD.GRANDES.values() for s in ss}


@pytest.mark.parametrize(
    "model",
    [
        lambda d: M.classic_dunn(d["E"], d["regions"], "base"),
        lambda d: M.esteban_marquillas(d["E"], d["regions"]),
        lambda d: M.dynamic_shift_share(d["E"], d["regions"]),
        lambda d: M.nazara_hewings(d["E"], d["regions"], d["W"]),
    ],
)
def test_identity_closes_on_real_data(panel, model):
    E = panel["E"]
    delta = E[:, :, -1].sum(1) - E[:, :, 0].sum(1)
    assert np.allclose(model(panel)["total_explained"], delta)


def test_two_point_and_annual_panels_share_the_endpoints():
    short = RD.load_panel(years=(2022, 2025), level="secao")
    long = RD.load_panel(years=RD.YEARS, level="secao")
    assert np.array_equal(short["E"][:, :, 0], long["E"][:, :, 0])
    assert np.array_equal(short["E"][:, :, -1], long["E"][:, :, -1])


def test_broad_sectors_preserve_total_employment():
    fine = RD.load_panel(years=RD.YEARS, level="secao")
    coarse = RD.load_panel(years=RD.YEARS, level="grande")
    assert np.allclose(fine["E"].sum(axis=1), coarse["E"].sum(axis=1))


def test_static_dunn_on_annual_panel_equals_two_point_dunn():
    """The static variants only ever look at the endpoints, so the extra
    years in the annual panel must not move them."""
    short = RD.load_panel(years=(2022, 2025), level="secao")
    long = RD.load_panel(years=RD.YEARS, level="secao")
    a = M.classic_dunn(short["E"], short["regions"], "base")["competitive"]
    b = M.classic_dunn(long["E"], long["regions"], "base")["competitive"]
    assert np.allclose(a, b)
