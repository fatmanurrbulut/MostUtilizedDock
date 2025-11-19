import argparse
import csv
import os
import time

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from src.sequential import sequential_best_row
from src.dac import dac_best_row



def load_matrix(path: str) -> np.ndarray:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")

    try:
        # Header yoksa direkt okur
        U = np.loadtxt(path, delimiter=",", dtype=int)
    except ValueError:
        # Header varsa ilk satırı atla
        U = np.loadtxt(path, delimiter=",", dtype=int, skiprows=1)

    if U.ndim == 1:
        # Tek satırlı matris durumunda shape'i (1, T) yap
        U = U.reshape(1, -1)

    return U


def parse_sizes(size_spec: str, R: int, T: int):
    sizes = []
    if not size_spec:
        # Default: sadece full matrix
        sizes.append((R, T))
        return sizes

    chunks = size_spec.split("|")
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        parts = chunk.split(",")
        kv = {}
        for p in parts:
            p = p.strip()
            if not p:
                continue
            key, value = p.split(":")
            kv[key.strip().upper()] = value.strip().lower()

        r_token = kv.get("R", "all")
        if r_token == "all":
            R_sub = R
        elif r_token == "half":
            R_sub = max(1, R // 2)
        else:
            R_sub = min(R, int(r_token))

        t_token = kv.get("T", "all")
        if t_token == "all":
            T_sub = T
        elif t_token == "half":
            T_sub = max(1, T // 2)
        else:
            T_sub = min(T, int(t_token))

        sizes.append((R_sub, T_sub))

    sizes = list(dict.fromkeys(sizes))
    return sizes


def run_timings(U_full: np.ndarray, repeats: int, sizes, csv_path: str):
    R, T = U_full.shape

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["method", "R", "T", "repeat", "seconds"])

        for (R_sub, T_sub) in sizes:
            if R_sub > R or T_sub > T:
                continue

            U = U_full[:R_sub, :T_sub]

            row_s, cnt_s = sequential_best_row(U)
            row_d, cnt_d = dac_best_row(U)

            if row_s != row_d or cnt_s != cnt_d:
                raise RuntimeError(
                    f"Sequential and D&C disagree for size R={R_sub}, T={T_sub}: "
                    f"seq=({row_s}, {cnt_s}), dac=({row_d}, {cnt_d})"
                )

            for r in range(repeats):
                t0 = time.perf_counter()
                _ = sequential_best_row(U)
                t1 = time.perf_counter()
                writer.writerow(["sequential", R_sub, T_sub, r, t1 - t0])

                t0 = time.perf_counter()
                _ = dac_best_row(U)
                t1 = time.perf_counter()
                writer.writerow(["dac", R_sub, T_sub, r, t1 - t0])


def plot_runtime(csv_path: str, out_path: str):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Timing CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    df["N"] = df["R"] * df["T"]

    grouped = df.groupby(["method", "N"])["seconds"].mean().reset_index()

    plt.figure()
    for method in grouped["method"].unique():
        sub = grouped[grouped["method"] == method]
        plt.plot(sub["N"], sub["seconds"], marker="o", label=method)

    plt.xlabel("Input size N = R * T")
    plt.ylabel("Average runtime (seconds)")
    plt.title("Runtime vs Input Size (Sequential vs D&C)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()




def main():
    parser = argparse.ArgumentParser(description="Run timing experiments for HW2.")
    parser.add_argument(
        "--data",
        required=True,
        help="Path to occupancy CSV file, e.g., data/occupancy.csv",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=10,
        help="Number of repeats per configuration (default: 10)",
    )
    parser.add_argument(
        "--sizes",
        type=str,
        default="R:all,T:all|R:half,T:all|R:all,T:half",
        help='Size specs, e.g. "R:all,T:all|R:half,T:all|R:all,T:half"',
    )

    args = parser.parse_args()

    U_full = load_matrix(args.data)
    R, T = U_full.shape
    print(f"Loaded matrix with shape R={R}, T={T}")

    sizes = parse_sizes(args.sizes, R, T)
    print("Sizes to test:", sizes)

    csv_path = "results/timings.csv"
    run_timings(U_full, args.repeats, sizes, csv_path)
    print(f"Timing results written to {csv_path}")

    out_plot = "plots/runtime_vs_size.png"
    plot_runtime(csv_path, out_plot)
    print(f"Runtime plot saved to {out_plot}")


if __name__ == "__main__":
    main()
