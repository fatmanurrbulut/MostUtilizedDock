import unittest
import numpy as np
import sys
import os

# Add src folder to Python path so we can import the module correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sequential import sequential_best_row


class TestSequential(unittest.TestCase):

    def test_simple_case(self):
        """
        Simple check: does the function correctly find the row
        with the highest number of 1s?
        """
        U = np.array([[1, 0],
                      [1, 1],
                      [0, 0]])

        idx, count = sequential_best_row(U)

        # Row 1 has 2 ones → it should be selected
        self.assertEqual(idx, 1)
        self.assertEqual(count, 2)

    def test_tie_breaking(self):
        """
        If two rows have the same number of 1s,
        the function should return the row with the smaller index.
        """
        U = np.array([[1, 1],
                      [1, 1]])  # both rows have 2 ones → tie

        idx, count = sequential_best_row(U)

        # Tie rule: smallest index wins (index 0)
        self.assertEqual(idx, 0)
        self.assertEqual(count, 2)

    def test_all_zeros(self):
        """
        If every entry in the matrix is zero, the best row should be 0
        because all rows are equal (tie case).
        """
        U = np.zeros((3, 5), dtype=int)

        idx, count = sequential_best_row(U)

        # All counts are zero → smallest index: 0
        self.assertEqual(idx, 0)
        self.assertEqual(count, 0)


if __name__ == '__main__':
    unittest.main()
