from typing import Tuple
import numpy as np


def dac_row_counts(U: np.ndarray) -> np.ndarray:
    """
    Recursively computes the number of '1's in each row of matrix U using
    a divide-and-conquer splitting strategy on the columns.

    Parameters
    ----------
    U : np.ndarray
        2D binary matrix (R x T). Each row represents a dock, each column a time slot.

    Returns
    -------
    np.ndarray
        1D array of length R, where each element is the total count of '1's in that row.
    """

    # Ensure U is a 2D matrix
    if U.ndim != 2:
        raise ValueError("U must be a 2D array")

    R, T = U.shape

    # If no columns, all rows have count 0
    if T == 0:
        return np.zeros(R, dtype=int)

    # Base case: single column → return that column as counts
    if T == 1:
        return U[:, 0].astype(int)

    # Split columns into two halves
    mid = T // 2
    left = U[:, :mid]
    right = U[:, mid:]

    # Recursively compute counts for each half
    left_counts = dac_row_counts(left)
    right_counts = dac_row_counts(right)

    # Combine results by element-wise summation
    return left_counts + right_counts


def _dac_argmax_recursive(counts: np.ndarray, offset: int = 0) -> Tuple[int, int]:
    """
    Recursively finds the index of the maximum value in the array using
    divide-and-conquer. In case of ties, the smaller index wins.

    Parameters
    ----------
    counts : np.ndarray
        1D integer array representing row totals.
    offset : int
        Used to correct indices when merging recursive halves.

    Returns
    -------
    Tuple[int, int]
        (best_index, best_value)
    """

    # Ensure input is 1D
    if counts.ndim != 1:
        raise ValueError("counts must be a 1D array")

    n = counts.shape[0]
    if n == 0:
        raise ValueError("counts must be non-empty")

    # Base case: only one element
    if n == 1:
        return offset, int(counts[0])

    # Divide into left and right segments
    mid = n // 2
    left_counts = counts[:mid]
    right_counts = counts[mid:]

    # Solve subproblems
    left_idx, left_val = _dac_argmax_recursive(left_counts, offset)
    right_idx, right_val = _dac_argmax_recursive(right_counts, offset + mid)

    # Compare results
    if right_val > left_val:
        return right_idx, right_val
    elif right_val < left_val:
        return left_idx, left_val
    else:
        # Tie-breaker: return smaller index
        return (left_idx, left_val) if left_idx <= right_idx else (right_idx, right_val)


def dac_best_row(U: np.ndarray) -> Tuple[int, int]:
    """
    Computes the dock (row) with the highest number of '1's using
    a full divide-and-conquer pipeline:
        1. Compute row counts with column splitting
        2. Find index of maximum using recursive tournament

    Parameters
    ----------
    U : np.ndarray
        2D binary matrix.

    Returns
    -------
    Tuple[int, int]
        (best_row_index, count_of_ones)
    """

    # Validate input
    if U.ndim != 2:
        raise ValueError("U must be a 2D array")

    # Step 1: compute row totals
    counts = dac_row_counts(U)

    # Step 2: recursively determine the row with the maximum count
    best_idx, best_val = _dac_argmax_recursive(counts)

    return int(best_idx), int(best_val)
