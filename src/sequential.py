# src/sequential.py
"""
Sequential baseline for finding the most utilized dock.

- sequential_best_row(U): scans each row, counts 1s, tracks best row.
"""

from typing import Tuple
import numpy as np


def sequential_best_row(U: np.ndarray) -> Tuple[int, int]:
    """
    Returns (best_row_index, ones_count) using a simple sequential scan.

    Tie-breaking rule: if multiple rows have the same maximum count,
    the smallest row index is returned.

    Parameters
    ----------
    U : np.ndarray
        Binary occupancy matrix of shape (R, T).

    Returns
    -------
    (best_row, best_count) : Tuple[int, int]
    """
    if U.ndim != 2:
        raise ValueError("U must be a 2D array")

    R, T = U.shape
    if T == 0:
        # Hiç kolon yoksa herkesin toplamı 0; dokümanda bu case tanımlı değil,
        # ama biz güvenli taraf için (0, 0) diyelim.
        return 0, 0

    best_row = 0
    best_count = -1

    for i in range(R):
        # Satır toplamı
        row_count = int(U[i, :].sum())

        # Daha büyükse veya ilk satırsa güncelle
        if row_count > best_count:
            best_count = row_count
            best_row = i
        # eşitse hiçbir şey yapmıyoruz → otomatikman küçük index korunuyor

    return best_row, best_count
