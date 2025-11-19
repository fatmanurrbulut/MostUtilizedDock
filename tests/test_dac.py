import numpy as np

from src.dac import dac_row_counts, dac_best_row
from src.sequential import sequential_best_row


def test_dac_row_counts_matches_numpy_sum():
    rng = np.random.default_rng(42)

    for _ in range(10):
        R = rng.integers(1, 10)
        T = rng.integers(1, 20)
        U = rng.integers(0, 2, size=(R, T), dtype=int)

        counts_dac = dac_row_counts(U)
        counts_np = U.sum(axis=1)

        assert np.array_equal(counts_dac, counts_np)


def test_dac_best_row_matches_sequential_random():
    rng = np.random.default_rng(123)

    for _ in range(20):
        R = rng.integers(1, 15)
        T = rng.integers(1, 25)
        U = rng.integers(0, 2, size=(R, T), dtype=int)

        row_dac, cnt_dac = dac_best_row(U)
        row_seq, cnt_seq = sequential_best_row(U)

        assert cnt_dac == cnt_seq
        assert row_dac == row_seq


def test_single_column_tie_handling():
    # 3 satır, 1 kolon → hepsi 1 olsun, tie case
    U = np.array([
        [1],
        [1],
        [1],
    ], dtype=int)

    counts = dac_row_counts(U)
    assert np.array_equal(counts, np.array([1, 1, 1]))

    best_row, best_count = dac_best_row(U)
    # Hepsi 1 → en küçük index (0) kazanmalı
    assert best_row == 0
    assert best_count == 1


def test_all_zero_matrix():
    U = np.zeros((5, 7), dtype=int)

    counts = dac_row_counts(U)
    assert np.array_equal(counts, np.zeros(5, dtype=int))

    row_dac, cnt_dac = dac_best_row(U)
    row_seq, cnt_seq = sequential_best_row(U)

    assert cnt_dac == cnt_seq == 0
    assert row_dac == row_seq == 0  # tie → index 0


def test_single_row_multiple_columns():
    U = np.array([[1, 0, 1, 1, 0]], dtype=int)

    counts = dac_row_counts(U)
    assert np.array_equal(counts, np.array([3]))

    row_dac, cnt_dac = dac_best_row(U)
    row_seq, cnt_seq = sequential_best_row(U)

    assert row_dac == row_seq == 0
    assert cnt_dac == cnt_seq == 3
