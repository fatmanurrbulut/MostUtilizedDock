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
    """
    Loads the occupancy matrix from a CSV file.

    In the report, this is the matrix U (R x T).
    We use pandas here so we can easily ignore the first index column in the CSV.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")

    # Read with pandas so we can drop index column easily
    try:
        df = pd.read_csv(path, index_col=0, encoding='utf-8-sig')
        U = df.values.astype(int)
    except Exception as e:
        raise ValueError(f"Error loading matrix from {path}: {e}")

    # If there is only one row, make sure shape is (1, T) not (T,)
    if U.ndim == 1:
        U = U.reshape(1, -1)

    return U


def parse_sizes(size_spec: str, R: int, T: int):
    """
    Parses the size specification string into a list of (R_sub, T_sub) pairs.

    The format is something like:
        "R:all,T:all|R:half,T:all|R:10,T:all"

    - R:all  -> use all rows
    - R:half -> use half of the rows
    - R:10   -> use min(10, R)
    Same idea for T.
    """
    sizes = []
    if not size_spec:
        # Default: only test on the full matrix
        sizes.append((R, T))
        return sizes

    chunks = size_spec.split("|")
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        parts = chunk.split(",")
        kv = {}

        # Parse key:value pairs like "R:all", "T:half"
        for p in parts:
            p = p.strip()
            if not p:
                continue
            key, value = p.split(":")
            kv[key.strip().upper()] = value.strip().lower()

        # --- R part ---
        r_token = kv.get("R", "all")
        if r_token == "all":
            R_sub = R
        elif r_token == "half":
            R_sub = max(1, R // 2)
        else:
            R_sub = min(R, int(r_token))

        # --- T part ---
        t_token = kv.get("T", "all")
        if t_token == "all":
            T_sub = T
        elif t_token == "half":
            T_sub = max(1, T // 2)
        else:
            T_sub = min(T, int(t_token))

        sizes.append((R_sub, T_sub))

    # Remove duplicates while keeping order
    sizes = list(dict.fromkeys(sizes))
    return sizes


def run_timings(U_full: np.ndarray, repeats: int, sizes, csv_path: str):
    """
    For each (R_sub, T_sub) configuration:
      - take a submatrix of U_full
      - check that sequential_best_row and dac_best_row give the same result
      - measure their runtimes multiple times
      - write all timing data into a CSV file

    This function basically generates the data for our performance plot.
    """
    R, T = U_full.shape

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["method", "R", "T", "repeat", "seconds"])

        for (R_sub, T_sub) in sizes:
            # Skip if the requested size is bigger than the original matrix
            if R_sub > R or T_sub > T:
                continue

            # Take the top-left submatrix
            U = U_full[:R_sub, :T_sub]

            # First check correctness: both algorithms must agree
            row_s, cnt_s = sequential_best_row(U)
            row_d, cnt_d = dac_best_row(U)

            if row_s != row_d or cnt_s != cnt_d:
                raise RuntimeError(
                    f"Sequential and D&C disagree for size R={R_sub}, T={T_sub}: "
                    f"seq=({row_s}, {cnt_s}), dac=({row_d}, {cnt_d})"
                )

            # If they agree, measure runtime
            for r in range(repeats):
                # Sequential timing
                t0 = time.perf_counter()
                _ = sequential_best_row(U)
                t1 = time.perf_counter()
                writer.writerow(["sequential", R_sub, T_sub, r, t1 - t0])

                # D&C timing
                t0 = time.perf_counter()
                _ = dac_best_row(U)
                t1 = time.perf_counter()
                writer.writerow(["dac", R_sub, T_sub, r, t1 - t0])


def plot_runtime(csv_path: str, out_path: str):
    """
    Reads the timing CSV and creates a runtime vs input size plot.

    The x-axis shows N = R × T (total number of cells),
    the y-axis shows average runtime in milliseconds,
    and we plot both Sequential and Divide & Conquer curves.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Timing CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Total input size for each configuration
    df["N"] = df["R"] * df["T"]

    # Group by method and N, then take the mean time → convert to ms
    grouped = (
        df.groupby(["method", "N"])["seconds"]
        .mean()
        .reset_index()
        .sort_values("N")
    )
    grouped["ms"] = grouped["seconds"] * 1000.0

    plt.figure(figsize=(8, 4.5))

    # Draw a separate line for each method
    for method in grouped["method"].unique():
        sub = grouped[grouped["method"] == method]

        if method == "sequential":
            label = "Sequential"
            plt.plot(
                sub["N"],
                sub["ms"],
                marker="o",
                linestyle="-",
                label=label,
            )
        else:
            label = "Divide & Conquer"
            plt.plot(
                sub["N"],
                sub["ms"],
                marker="x",
                linestyle="--",
                label=label,
            )

    plt.xlabel("Input Size (R × T)")
    plt.ylabel("Runtime (ms)")
    plt.title("Performance Comparison: Sequential vs D&C")
    plt.grid(True, alpha=0.3)
    plt.legend()

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def main():
    """
    Command-line entry point for running timing experiments.

    Example usage:
        python run_experiment.py --data data/occupancy.csv

    This will:
      - load the matrix
      - run timings for different sizes
      - write results to results/timings.csv
      - generate plots/runtime_vs_size.png
    """
    parser = argparse.ArgumentParser(description="Run timing experiments for HW2.")

    parser.add_argument(
        "--data",
        required=True,
        help="Path to occupancy CSV file, e.g., data/occupancy.csv",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        # Slightly higher so the average is more stable
        default=50,
        help="Number of repeats per configuration (default: 50)",
    )
    parser.add_argument(
        "--sizes",
        type=str,
        # Multiple sizes so we get more points in the graph
        default="R:10,T:all|R:20,T:all|R:half,T:all|R:all,T:all",
        help='Size specs, e.g. "R:all,T:all|R:half,T:all|R:10,T:all"',
    )

    args = parser.parse_args()

    # 1) Load matrix from CSV
    U_full = load_matrix(args.data)
    R, T = U_full.shape
    print(f"Loaded matrix with shape R={R}, T={T}")

    # 2) Parse the size configurations
    sizes = parse_sizes(args.sizes, R, T)
    print("Sizes to test:", sizes)

    # 3) Run timing experiments and save raw data
    csv_path = "results/timings.csv"
    run_timings(U_full, args.repeats, sizes, csv_path)
    print(f"Timing results written to {csv_path}")

    # 4) Create the runtime vs size plot
    out_plot = "plots/runtime_vs_size.png"
    plot_runtime(csv_path, out_plot)
    print(f"Runtime plot saved to {out_plot}")


if __name__ == "__main__":
    main()
