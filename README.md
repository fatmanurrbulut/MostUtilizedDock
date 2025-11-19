# Most Utilized Dock Analysis Project

This project implements algorithms to analyze dock utilization data and identify the most frequently used dock within a given time period. The project compares a **Sequential Baseline** approach with a **Divide-and-Conquer** strategy.

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

How to Run
To process the data, run the algorithms, and generate visualizations, execute the main script from the root directory:

python main.py

This script will:Read the raw event data from dock_events_raw_sample.csv.Generate the occupancy matrix ($U$).Run the Sequential algorithm to find the best dock.Save the resulting charts to the plots/ directory.


Role A: Data Preparation & Sequential AnalysisThis section details the data pipeline, assumptions, and the baseline algorithm design.Data AssumptionsTo convert continuous time logs into a discrete format suitable for algorithmic analysis, the following assumptions were made1111:Time Slots ($\Delta$): The timeline is discretized into 5-minute slots (delta_minutes = 5). This granularity provides a balance between precision and computational efficiency.Interval Logic: Occupancy is defined based on the interval [arrival_time, departure_time). A dock is considered "occupied" at time $t$ if $arrival \le t < departure$2.Matrix Dimensions ($R \times T$):$R$: Number of unique Docks.$T$: Number of time slots in the analyzed period.Matrix ConstructionThe occupancy matrix $U$ is generated in src/data_prep.py3333:Time Grid: A grid of timestamps is built from the earliest arrival to the latest departure.Mapping: Each dock_id is mapped to a row index $r$.Binary Filling: For each event, the start and end indices in the time grid are found using binary search ($O(\log T)$). The corresponding cells $U[r, t_{start}:t_{end}]$ are set to 1.Sequential AlgorithmThe baseline solution is implemented in src/sequential.py4.Logic: It iterates through the matrix row by row (dock by dock), summing the number of 1s in each row.Complexity: $\Theta(RT)$ time complexity, where we scan every cell in the matrix5555.Tie-Breaking: In case of a tie (two docks having the same max usage), the dock with the smaller numerical index is selected6.VisualizationsVisual outputs are generated via src/plots_basic.py to aid in qualitative analysis7777:Heatmap (plots/heatmap.png):Visualizes the $R \times T$ binary matrix.Dark/Purple: Empty slot (0).Yellow/Bright: Occupied slot (1).This allows for quick identification of busy hours and idle docks.Bar Chart (plots/bar_chart.png):Displays the total duration (in slots) each dock was occupied.The algorithmically selected "Best Dock" is highlighted in Red for easy verification.