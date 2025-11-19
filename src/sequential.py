# Dosya: src/sequential.py
import numpy as np

def sequential_best_row(U):

    R, T = U.shape
    best_idx = -1
    max_ones = -1

    for r in range(R):
        
        count = np.sum(U[r, :])
        
        if count > max_ones:
            max_ones = count
            best_idx = r
            
    return best_idx, max_ones