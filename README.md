
````markdown
# Most Utilized Dock Analysis Project

This project implements algorithms to analyze dock utilization data and identify the most frequently used dock within a given time period. The project compares a **Sequential Baseline** approach (Role A) with a **Divide-and-Conquer** strategy (Role B).

## Table of Contents
- [Installation & Usage](#installation--usage)
- [Project Structure](#project-structure)
- [Role A: Data Preparation & Sequential Analysis](#role-a-data-preparation--sequential-analysis)
    - [Data Assumptions](#data-assumptions)
    - [Matrix Construction](#matrix-construction)
    - [Sequential Algorithm](#sequential-algorithm)
    - [Visualizations](#visualizations)
- [Role B: Divide-and-Conquer Algorithm](#role-b-divide-and-conquer-algorithm)
    - [Algorithm Design](#algorithm-design)
    - [Complexity Analysis](#complexity-analysis)
    - [Correctness & Tie-Breaking](#correctness--tie-breaking)
- [Performance Comparison](#performance-comparison)
- [Testing](#testing)

---

## Installation & Usage

### Requirements
Ensure you have Python 3.x installed. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install pandas numpy matplotlib seaborn pytest
````

### How to Run

To process the data, run the algorithms, and generate visualizations, execute the main script from the root directory:

```bash
python main.py
```

This script will:

1.  Read the raw event data from `dock_events_raw_sample.csv`.
2.  Generate the occupancy matrix ($U$).
3.  Run both Sequential and Divide-and-Conquer algorithms to find the best dock.
4.  Generate `data/info.json` with matrix metadata (R, T, ones, sparsity, delta).
5.  Save the resulting charts to the `plots/` directory.

### Regenerating the Occupancy Matrix

To regenerate the occupancy matrix with different parameters:

```python
from src.data_prep import events_to_matrix, save_info

# Generate matrix with 5-minute slots
U, docks, slots = events_to_matrix("data/dock_events_raw_sample.csv", delta_minutes=5)

# Save metadata
save_info(U, delta_minutes=5, output_path="data/info.json")
```

### Reproducing Visualizations

To regenerate heatmap and bar chart:

```python
from src.plots_basic import save_heatmap, save_bar_chart
import numpy as np

# Load or generate U matrix
# ...

# Generate visualizations
save_heatmap(U, output_path="plots/heatmap.png")
save_bar_chart(U, output_path="plots/bar_chart.png", best_dock_idx=best_idx, dock_labels=docks)
```

-----

## Project Structure

```text
MostUtilizedDock/
├── data/                   # Data files (generated or input)
│   ├── dock_events_raw_sample.csv
│   ├── dock_occupancy_matrix.csv
│   ├── occupancy.csv
│   └── info.json          # Matrix metadata (R, T, ones, sparsity, delta)
├── plots/                  # Generated visualizations
│   ├── heatmap.png        # Occupancy heatmap
│   ├── bar_chart.png      # Per-dock total occupancy
│   └── runtime_vs_size.png # Performance comparison
├── results/
│   └── timings.csv        # Timing experiment results
├── src/
│   ├── data_prep.py        # Matrix generation & time discretization
│   ├── sequential.py       # Baseline sequential algorithm
│   ├── dac.py              # Divide and Conquer algorithm
│   └── plots_basic.py      # Visualization functions
├── tests/                  # Unit tests
│   ├── test_sequential.py  # Tests for sequential algo
│   └── test_dac.py         # Tests for D&C algo
├── main.py                 # Main execution script
├── run_experiment.py       # Performance experiments
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

-----

## Role A: Data Preparation & Sequential Analysis

This section details the data pipeline, assumptions, and the baseline algorithm design implemented by Role A.

### Data Assumptions

To convert continuous time logs into a discrete format suitable for algorithmic analysis, the following assumptions were made:

  * **Time Slots ($\Delta$):** The timeline is discretized into **5-minute slots** (`delta_minutes = 5`). This granularity provides a balance between precision and computational efficiency. Alternative values (10-minute slots) can be configured if needed.
  * **Rationale for $\Delta = 5$ minutes:** 
      * Sufficient granularity to capture typical dock operations
      * Keeps matrix size manageable ($T \approx 288$ for a 24-hour period)
      * Balances accuracy vs computational cost
  * **Interval Logic:** Occupancy is defined based on the interval `[arrival_time, departure_time)`. A dock is considered "occupied" at time $t$ if $arrival \le t < departure$.
  * **Matrix Dimensions ($R \times T$):**
      * $R$: Number of unique Docks.
      * $T$: Number of time slots in the analyzed period.
  * **Output Files:**
      * `data/occupancy.csv`: Binary matrix (R×T) with 0/1 values
      * `data/info.json`: Metadata containing R, T, ones count, sparsity, and delta value

### Matrix Construction

The occupancy matrix $U$ is generated in `src/data_prep.py`:

1.  **Time Grid:** A grid of timestamps is built from the earliest arrival to the latest departure.
2.  **Mapping:** Each `dock_id` is mapped to a row index $r$.
3.  **Binary Filling:** For each event, the start and end indices in the time grid are found using binary search via `np.searchsorted`. This ensures $O(\log T)$ efficiency per event. The corresponding cells $U[r, t_{start}:t_{end}]$ are set to `1`.

### Sequential Algorithm

The baseline solution is implemented in `src/sequential.py`:

  * **Logic:** It iterates through the matrix row by row (dock by dock), summing the number of `1`s in each row (`Row-wise scan`).
  * **Complexity:** $\Theta(RT)$ time complexity, where we scan every cell in the matrix exactly once.
  * **Tie-Breaking:** In case of a tie (two docks having the same max usage), the dock with the **smaller numerical index** is selected. This is enforced by strictly updating the max value only when `current > max`.

### Visualizations

Visual outputs are generated via `src/plots_basic.py` to aid in qualitative analysis:

1.  **Heatmap (`plots/heatmap.png`):**

      * Visualizes the $R \times T$ binary matrix.
      * **Dark/Purple:** Empty slot (0).
      * **Yellow/Bright:** Occupied slot (1).
      * This allows for quick identification of busy hours and idle docks.

2.  **Bar Chart (`plots/bar_chart.png`):**

      * Displays the total duration (in slots) each dock was occupied.
      * The algorithmically selected "Best Dock" is highlighted in **Red** for easy verification against the algorithm's text output.

-----

## Role B: Divide-and-Conquer Algorithm

This section describes the Divide-and-Conquer (D&C) approach implemented in `src/dac.py` to solve the same problem more efficiently.

### Algorithm Design

The D&C strategy consists of two main functions:

#### 1. `dac_row_counts(U)` - Computing Row Sums

This function recursively computes the sum of 1s in each row by dividing the matrix column-wise:

**Base Cases:**
- If $T = 0$: Return a zero vector of length $R$
- If $T = 1$: Return the single column as row counts

**Recursive Case:**
- Split the matrix $U$ into left and right halves at column $mid = \lfloor T/2 \rfloor$
- Recursively compute row counts for both halves
- Combine results by element-wise addition: `counts = left_counts + right_counts`

**Recurrence Relation:**
$$T(R, T) = 2T(R, T/2) + \Theta(R)$$

Where the $\Theta(R)$ term comes from the addition operation.

#### 2. `dac_best_row(U)` - Finding Maximum

After computing row counts, this function finds the row with maximum count using a recursive approach:

**Base Case:**
- If array length is 1: Return that element's index and value

**Recursive Case:**
- Split counts array in half
- Recursively find max in left and right halves
- Compare and return the larger value
- **Tie-breaking:** If values are equal, return the smaller index

**Recurrence Relation:**
$$T(n) = 2T(n/2) + \Theta(1)$$

### Complexity Analysis

#### Time Complexity

**For `dac_row_counts`:**
- Recurrence: $T(R, T) = 2T(R, T/2) + \Theta(R)$
- Using Master Theorem (Case 1): $T(R, T) = \Theta(RT)$
- **Same asymptotic complexity as sequential approach**

**For `dac_best_row` (finding max in 1D array):**
- Recurrence: $T(n) = 2T(n/2) + \Theta(1)$
- Using Master Theorem (Case 1): $T(n) = \Theta(n)$

**Overall D&C Time Complexity:** $\Theta(RT) + \Theta(R) = \Theta(RT)$

**Note:** While asymptotically equivalent to the sequential approach, the D&C method demonstrates:
- Better cache locality for large matrices
- Potential for parallelization (each recursive call is independent)
- Improved performance on modern CPU architectures with deep pipelines

#### Space Complexity

- **Sequential:** $\Theta(1)$ auxiliary space (only tracking max and index)
- **D&C:** $\Theta(\log T + \log R)$ space due to recursive call stack depth
- **Trade-off:** D&C uses more stack space but offers parallelization potential

### Correctness & Tie-Breaking

**Correctness Guarantee:**
- Both algorithms implement the same tie-breaking rule: smallest index wins
- Extensive unit tests in `tests/test_dac.py` verify that D&C and sequential produce identical results
- Tests include edge cases: all zeros, single row/column, random matrices, and tie scenarios

**Tie-Breaking Implementation:**
```python
if right_val > left_val:
    return right_idx, right_val
elif right_val < left_val:
    return left_idx, left_val
else:
    # Tie: return smaller index
    return min(left_idx, right_idx), left_val
```

-----

## Performance Comparison

To compare the runtime performance of both algorithms:

```bash
python run_experiment.py --data data/dock_occupancy_matrix.csv --repeats 10
```

### Command Line Options

```bash
python run_experiment.py --data <csv_path> --repeats <N> --sizes "<size_spec>"
```

**Parameters:**
- `--data`: Path to occupancy CSV file (required)
- `--repeats`: Number of timing runs per configuration (default: 10)
- `--sizes`: Size specifications for scaling experiments (default: "R:all,T:all|R:half,T:all|R:all,T:half")

**Example:**
```bash
python run_experiment.py --data data/occupancy.csv --repeats 20 --sizes "R:all,T:all|R:half,T:all|R:all,T:half|R:2x,T:half"
```

### What the Script Does

This script:
1. Loads the occupancy matrix
2. Verifies both algorithms produce identical results before timing
3. Runs both algorithms N≥10 times with `time.perf_counter()`
4. Measures execution time for each run
5. Generates `results/timings.csv` with detailed timing data (columns: method, R, T, repeat, seconds)
6. Creates `plots/runtime_vs_size.png` showing performance comparison

### Expected Output Files

- `results/timings.csv`: Raw timing data with mean ± std
- `plots/runtime_vs_size.png`: Runtime vs input size (N = R × T) graph

**Expected Results:**
- Both algorithms show linear growth with input size ($N = R \times T$)
- D&C may show slightly better performance due to:
  - Better memory access patterns
  - CPU cache efficiency
  - Modern compiler optimizations for recursive code

-----

## Testing

The project includes comprehensive unit tests to ensure correctness:

### Running Tests

```bash
pytest tests/ -v
```

### Test Coverage

**`tests/test_sequential.py`:**
- Simple case: Basic matrix with clear winner
- Tie-breaking: Multiple rows with same max value
- Edge case: All-zero matrix
- Single row matrix
- Full-ones matrix (all cells occupied)

**`tests/test_dac.py`:**
- Row count correctness: Compares `dac_row_counts` with `numpy.sum`
- Algorithm equivalence: Verifies D&C and sequential produce identical results
- Tie handling: Tests single-column matrices with all equal values
- Edge cases: All zeros, single row, single column, random matrices (20 random test cases)
- Very sparse matrices (sparsity > 0.9)
- Dense matrices (sparsity < 0.1)

### Edge Cases Covered

- **Empty matrix**: T=0 or R=0
- **Single dimension**: Single row (R=1) or single column (T=1)
- **Uniform values**: All zeros or all ones
- **Perfect ties**: Multiple rows with identical counts
- **Extreme sparsity**: Very few occupied cells
- **High density**: Nearly all cells occupied

All tests must pass before submission to ensure both algorithms are correct and equivalent.

-----

## Environment & Requirements

### Python Version
- Python 3.8 or higher recommended
- Tested on Python 3.12

### Dependencies

All required packages are listed in `requirements.txt`:

```txt
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
pytest>=7.0.0
```

### Installation

```bash
# Clone the repository
git clone https://github.com/fatmanurrbulut/MostUtilizedDock.git
cd MostUtilizedDock

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

-----

## Reproducibility Guide

To reproduce all results from scratch:

### Step 1: Generate Matrix and Metadata

```bash
python main.py
```

**Expected outputs:**
- `data/info.json` - Matrix metadata
- `plots/heatmap.png` - Occupancy visualization
- `plots/bar_chart.png` - Per-dock totals
- Console output showing Sequential and D&C results match

### Step 2: Run Performance Experiments

```bash
python run_experiment.py --data data/dock_occupancy_matrix.csv --repeats 10
```

**Expected outputs:**
- `results/timings.csv` - Detailed timing data
- `plots/runtime_vs_size.png` - Performance comparison graph

### Step 3: Run All Tests

```bash
pytest tests/ -v
```

**Expected output:**
- All tests pass (8/8 or more)
- No errors or warnings

### Verification Checklist

- [ ] `data/info.json` exists and contains R, T, ones, sparsity, delta
- [ ] All plots generated in `plots/` directory
- [ ] Sequential and D&C produce identical results
- [ ] All unit tests pass
- [ ] Timing experiments complete without errors
- [ ] Results are reproducible with same random seed

-----

## File Layout & Expected Outputs

```
MostUtilizedDock/
├── data/
│   ├── dock_events_raw_sample.csv    [INPUT]  Raw event logs
│   ├── dock_occupancy_matrix.csv      [INPUT]  Pre-computed matrix
│   ├── occupancy.csv                  [OUTPUT] Generated binary matrix
│   └── info.json                      [OUTPUT] Metadata (R, T, ones, sparsity, delta)
├── plots/
│   ├── heatmap.png                    [OUTPUT] Occupancy heatmap (1600×900)
│   ├── bar_chart.png                  [OUTPUT] Per-dock totals
│   └── runtime_vs_size.png            [OUTPUT] Performance graph
├── results/
│   └── timings.csv                    [OUTPUT] Timing data
└── ...
```

-----

## Notes & Limitations

- **Time slots**: Currently fixed at 5 minutes, can be adjusted by modifying `delta_minutes` parameter
- **Single day analysis**: Current implementation processes single-day data
- **Tie-breaking**: Consistent rule (smallest index) ensures deterministic results
- **Sparsity impact**: Algorithm performance may vary with matrix sparsity levels

-----

## Project Authors

- **Role A**: Data Preparation, Sequential Algorithm, Visualizations
- **Role B**: Divide-and-Conquer Algorithm, Performance Analysis, Complexity Discussion

For detailed contribution breakdown, see the project report.

-----

## License

This project is developed as part of Algorithm and Analysis coursework (HW2).
