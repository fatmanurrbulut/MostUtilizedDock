import unittest
import numpy as np
import sys
import os

# src klasörünü path 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sequential import sequential_best_row

class TestSequential(unittest.TestCase):
    
    def test_simple_case(self):
        """Basit bir durumda en çok 1 olan satırı buluyor mu?"""
        U = np.array([[1, 0], [1, 1], [0, 0]])
        idx, count = sequential_best_row(U)
        self.assertEqual(idx, 1)
        self.assertEqual(count, 2)

    def test_tie_breaking(self):
        """Eşitlik durumunda küçük indeksli olanı seçiyor mu?"""
        # İki satır da eşit dolulukta (2 tane 1 var)
        U = np.array([[1, 1], [1, 1]])
        idx, count = sequential_best_row(U)
        # Kural: Eşitse küçük indeks (0) kazanır.
        self.assertEqual(idx, 0)
        self.assertEqual(count, 2)

    def test_all_zeros(self):
        """Hiç gemi yoksa patlıyor mu?"""
        U = np.zeros((3, 5), dtype=int)
        idx, count = sequential_best_row(U)
        self.assertEqual(count, 0)

if __name__ == '__main__':
    unittest.main()