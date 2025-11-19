from typing import Tuple
import numpy as np


def dac_row_counts(U: np.ndarray) -> np.ndarray:

    if U.ndim != 2:
        raise ValueError("U must be a 2D array")

    R, T = U.shape

    if T == 0:
        return np.zeros(R, dtype=int)

    if T == 1:
        return U[:, 0].astype(int)

    mid = T // 2
    left = U[:, :mid]
    right = U[:, mid:]

    left_counts = dac_row_counts(left)
    right_counts = dac_row_counts(right)

    return left_counts + right_counts


def _dac_argmax_recursive(counts: np.ndarray, offset: int = 0) -> Tuple[int, int]:
    
    if counts.ndim != 1:
        raise ValueError("counts must be a 1D array")

    n = counts.shape[0]
    if n == 0:
        raise ValueError("counts must be non-empty")

    if n == 1:
        return offset, int(counts[0])

    mid = n // 2
    left_counts = counts[:mid]
    right_counts = counts[mid:]

    left_idx, left_val = _dac_argmax_recursive(left_counts, offset)
    right_idx, right_val = _dac_argmax_recursive(right_counts, offset + mid)

    if right_val > left_val:
        return right_idx, right_val
    elif right_val < left_val:
        return left_idx, left_val
    else:
        # Tie: küçük index kazanır
        if left_idx <= right_idx:
            return left_idx, left_val
        else:
            return right_idx, right_val


def dac_best_row(U: np.ndarray) -> Tuple[int, int]:
  
    if U.ndim != 2:
        raise ValueError("U must be a 2D array")

    counts = dac_row_counts(U)

    best_idx, best_val = _dac_argmax_recursive(counts)

    return int(best_idx), int(best_val)
