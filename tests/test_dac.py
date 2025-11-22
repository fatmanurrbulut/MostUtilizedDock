import numpy as np

from src.dac import dac_row_counts, dac_best_row
from src.sequential import sequential_best_row


def test_dac_row_counts_matches_numpy_sum():
    """
    This test checks if our recursive row counting function
    gives the same result as numpy’s built-in sum over axis=1.
    Basically: make random matrices and compare both outputs.
    """
    rng = np.random.default_rng(42)

    for _ in range(10):
        R = rng.integers(1, 10)
        T = rng.integers(1, 20)

        # Create a random binary matrix
        U = rng.integers(0, 2, size=(R, T), dtype=int)

        counts_dac = dac_row_counts(U)
        counts_np = U.sum(axis=1)

        # They must match exactly
        assert np.array_equal(counts_dac, counts_np)


def test_dac_best_row_matches_sequential_random():
    """
    This test makes sure dac_best_row finds the same best row
    as the simple sequential algorithm.
    We test this on a bunch of random matrices.
    """
    rng = np.random.default_rng(123)

    for _ in range(20):
        R = rng.integers(1, 15)
        T = rng.integers(1, 25)

        U = rng.integers(0, 2, size=(R, T), dtype=int)

        row_dac, cnt_dac = dac_best_row(U)
        row_seq, cnt_seq = sequential_best_row(U)

        # Both methods should agree
        assert cnt_dac == cnt_seq
        assert row_dac == row_seq


def test_single_column_tie_handling():
    """
    Special case: 3 rows and only 1 column.
    All are 1 → so they all tie.
    Our rule says: in ties, the smallest index wins (row 0).
    """
    U = np.array([
        [1],
        [1],
        [1],
    ], dtype=int)

    counts = dac_row_counts(U)
    assert np.array_equal(counts, np.array([1, 1, 1]))

    best_row, best_count = dac_best_row(U)

    # All have 1 → expect the smallest index
    assert best_row == 0
    assert best_count == 1


def test_all_zero_matrix():
    """
    Case where the entire matrix is zeros.
    All rows have 0, so the best row should again be index 0.
    """
    U = np.zeros((5, 7), dtype=int)

    counts = dac_row_counts(U)
    assert np.array_equal(counts, np.zeros(5, dtype=int))

    row_dac, cnt_dac = dac_best_row(U)
    row_seq, cnt_seq = sequential_best_row(U)

    # Both should return row 0 with value 0
    assert cnt_dac == cnt_seq == 0
    assert row_dac == row_seq == 0


def test_single_row_multiple_columns():
    """
    Only one row but several columns.
    The count should simply be the number of 1s in that single row.
    """
    U = np.array([[1, 0, 1, 1, 0]], dtype=int)

    counts = dac_row_counts(U)
    assert np.array_equal(counts, np.array([3]))

    row_dac, cnt_dac = dac_best_row(U)
    row_seq, cnt_seq = sequential_best_row(U)

    assert row_dac == row_seq == 0
    assert cnt_dac == cnt_seq == 3
