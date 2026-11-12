# Smart Campus Energy & EV Dashboard

A Python-based data processing and visualization project developed for **ITS72604 – Principles of Programming** at Taylor's University.

The project analyzes EV charging-session data, calculates energy and carbon metrics, identifies high-risk charging sessions, and presents the results through an interactive Streamlit dashboard.

## Live Dashboard

🚀 **[Open Smart Campus Energy & EV Dashboard](https://pop-final-assessment-ev-taylors.streamlit.app/)**

## Project Overview

This project uses Python libraries to clean, process, analyze, and visualize an EV campus charging dataset.

It includes a data-processing pipeline, reusable calculation functions, data visualizations, and a multi-page Streamlit application.

## Key Features

- **Data Processing:** CSV loading, data validation, duplicate checking, and missing-value handling using median imputation.
- **Feature Engineering:** Calculates charging duration in hours, power rate, carbon savings, and estimated billing amounts.
- **Data Analysis:** Uses NumPy, Pandas, and functional programming techniques to analyze charging sessions.
- **Data Visualization:** Generates charging revenue charts, correlation heatmaps, box plots, and scatter plots.
- **Interactive Dashboard:** Provides four pages:
  - Executive Overview
  - Charging Analysis
  - Alert Centre
  - Filtered Data
- **Dynamic Filtering:** Filter charging records by minimum energy and charger type.
- **Risk Monitoring:** Identifies sessions based on battery temperature and overstay thresholds.
- **CSV Export:** Downloads the currently filtered charging records.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| NumPy | Numerical operations |
| Pandas | Data processing and analysis |
| Matplotlib | Data visualization |
| Seaborn | Statistical visualization |
| Plotly | Interactive charts |
| Streamlit | Dashboard development |

## Project Structure

```text
POP-FINAL-ASSESSMENT/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── outputs/
│
├── src/
│   ├── data_processing.py
│   ├── calculations.py
│   ├── section_a.py
│   └── visualizations.py
│
├── app.py
├── requirements.txt
├── test_environment.py
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Shrimun/POP-FINAL-ASSESSMENT.git
```

### 2. Navigate to the project folder

```bash
cd POP-FINAL-ASSESSMENT
```

### 3. Install the required libraries

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit application

```bash
streamlit run app.py
```

The dashboard will open in your local browser.

## Dataset

The project uses an EV campus charging-session dataset containing 1,200 records and 9 original columns.

The dataset includes information such as:

- Charger type
- User type
- Charging start hour
- Charging duration
- Energy consumption
- Overstay duration
- Battery temperature
- Grid status

**Note:** The supplied dataset does not contain calendar timestamps, ambient temperature, measured grid load, or solar generation data. Therefore, some requested analyses are limited by the available dataset.

## Project Information

- **Module:** ITS72604 – Principles of Programming
- **Semester:** September 2026
- **Institution:** Taylor's University
- **Project:** Smart Campus Energy & EV Dashboard

---
