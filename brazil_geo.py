"""
brazil_geo.py
=============
Geography for the 27 artificial "states": the actual first-order contiguity
structure of the Brazilian federation (26 states + Distrito Federal).

Provides:
    UFS                   ordered list of the 27 state codes
    ADJACENCY             dict of land-border neighbors
    contiguity_matrix()   binary (27x27) or row-standardized W
    morans_i()            Moran's I with permutation p-value

The row-standardized W is used both in the DGP (to generate spatially
autocorrelated competitive effects via a SAR process) and in the
Nazara-Hewings spatial shift-share model, so spatial recovery is well-posed:
the model is given the same geography that generated the data.
"""

import numpy as np

UFS = [
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
]

ADJACENCY = {
    "AC": ["AM", "RO"],
    "AL": ["PE", "SE", "BA"],
    "AP": ["PA"],
    "AM": ["AC", "RO", "MT", "PA", "RR"],
    "BA": ["SE", "AL", "PE", "PI", "TO", "GO", "MG", "ES"],
    "CE": ["PI", "RN", "PB", "PE"],
    "DF": ["GO", "MG"],
    "ES": ["BA", "MG", "RJ"],
    "GO": ["DF", "MG", "MS", "MT", "TO", "BA"],
    "MA": ["PI", "TO", "PA"],
    "MT": ["MS", "GO", "TO", "PA", "AM", "RO"],
    "MS": ["MT", "GO", "MG", "SP", "PR"],
    "MG": ["SP", "RJ", "ES", "BA", "GO", "MS", "DF"],
    "PA": ["AP", "MA", "TO", "MT", "AM", "RR"],
    "PB": ["RN", "CE", "PE"],
    "PR": ["SP", "SC", "MS"],
    "PE": ["PB", "CE", "PI", "BA", "AL"],
    "PI": ["MA", "CE", "PE", "BA", "TO"],
    "RJ": ["SP", "MG", "ES"],
    "RN": ["CE", "PB"],
    "RS": ["SC"],
    "RO": ["AC", "AM", "MT"],
    "RR": ["AM", "PA"],
    "SC": ["PR", "RS"],
    "SP": ["RJ", "MG", "MS", "PR"],
    "SE": ["AL", "BA"],
    "TO": ["MA", "PI", "BA", "GO", "MT", "PA"],
}


def contiguity_matrix(row_standardize=True):
    """Return the (27, 27) contiguity matrix in UFS order."""
    idx = {uf: k for k, uf in enumerate(UFS)}
    W = np.zeros((len(UFS), len(UFS)))
    for uf, neighbors in ADJACENCY.items():
        for nb in neighbors:
            W[idx[uf], idx[nb]] = 1.0
    assert np.allclose(W, W.T), "contiguity must be symmetric"
    assert W.sum(axis=1).min() >= 1, "every state needs a neighbor"
    if row_standardize:
        W = W / W.sum(axis=1, keepdims=True)
    return W


def morans_i(x, W, n_perm=999, seed=0):
    """Moran's I of vector x under weight matrix W, with permutation p-value."""
    x = np.asarray(x, dtype=float)
    z = x - x.mean()
    s0 = W.sum()
    I = (len(x) / s0) * (z @ W @ z) / (z @ z)
    rng = np.random.default_rng(seed)
    perms = np.array(
        [
            (len(x) / s0) * (zp @ W @ zp) / (zp @ zp)
            for zp in (rng.permutation(z) for _ in range(n_perm))
        ]
    )
    p = (np.sum(np.abs(perms) >= abs(I)) + 1) / (n_perm + 1)  # two-sided
    return I, p


if __name__ == "__main__":
    W = contiguity_matrix(row_standardize=False)
    print("Neighbors per state:", dict(zip(UFS, W.sum(1).astype(int))))
    print("Total borders:", int(W.sum() / 2))
