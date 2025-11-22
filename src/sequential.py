# File: src/sequential.py
import numpy as np


def sequential_best_row(U):
    """
    Finds the row with the highest number of 1s using a simple sequential scan.
    This is the most basic (non-recursive) method:
    we just check each row, count how many 1s it has, and keep track of the best one.
    """

    R, T = U.shape      # R = number of rows (docks), T = time slots
    best_idx = -1       # will store the index of the row with the most 1s
    max_ones = -1       # will store the maximum number of 1s found so far

    # Loop through every row and count how many time slots are occupied
    for r in range(R):

        # Count how many 1s are in row r
        count = np.sum(U[r, :])

        # If this row has more 1s than our current best, update the best
        if count > max_ones:
            max_ones = count
            best_idx = r

    # Return the row index and the number of 1s in that row
    return best_idx, max_ones
