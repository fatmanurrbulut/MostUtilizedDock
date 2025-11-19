
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

---

## Installation & Usage

### Requirements
Ensure you have Python 3.x installed. Install the required dependencies:

```bash
pip install pandas numpy matplotlib seaborn
````

### How to Run

To process the data, run the algorithms, and generate visualizations, execute the main script from the root directory:

```bash
python main.py
```

This script will:

1.  Read the raw event data from `dock_events_raw_sample.csv`.
2.  Generate the occupancy matrix ($U$).
3.  Run the Sequential algorithm to find the best dock.
4.  Save the resulting charts to the `plots/` directory.

-----

## Project Structure

```text
MostUtilizedDock/
├── data/                   # Data files (generated or input)
├── plots/                  # Generated visualizations (Heatmap, Bar Chart)
├── src/
│   ├── data_prep.py        # Matrix generation & time discretization
│   ├── sequential.py       # Baseline sequential algorithm
│   ├── plots_basic.py      # Visualization functions
│   └── dac.py              # Divide and Conquer algorithm (Role B)
├── tests/                  # Unit tests
│   └── test_sequential.py  # Tests for sequential algo
├── main.py                 # Main execution script
└── README.md               # Project documentation
```

-----

## Role A: Data Preparation & Sequential Analysis

This section details the data pipeline, assumptions, and the baseline algorithm design implemented by Role A.

### Data Assumptions

To convert continuous time logs into a discrete format suitable for algorithmic analysis, the following assumptions were made:

  * **Time Slots ($\Delta$):** The timeline is discretized into **5-minute slots** (`delta_minutes = 5`). This granularity provides a balance between precision and computational efficiency.
  * **Interval Logic:** Occupancy is defined based on the interval `[arrival_time, departure_time)`. A dock is considered "occupied" at time $t$ if $arrival \le t < departure$.
  * **Matrix Dimensions ($R \times T$):**
      * $R$: Number of unique Docks.
      * $T$: Number of time slots in the analyzed period.

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

<!-- end list -->

```
```