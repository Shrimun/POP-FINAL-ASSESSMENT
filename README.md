# Smart Campus Energy & EV Fleet Dashboard

## Project overview
A Python data pipeline and Streamlit dashboard for analysing EV charging sessions,
energy delivery, carbon savings, charging costs, and high-risk sessions.

## Project structure
```text
POP_Final_Assignment/
├── data/
│   ├── raw/
│   │   ├── ev_campus_dataset.csv
│   │   └── sales_data.csv
│   └── processed/
│       └── cleaned_energy_sales_data.csv
├── outputs/charts/
├── src/
│   ├── __init__.py
│   ├── data_processing.py
│   ├── calculations.py
│   ├── section_a.py
│   └── visualizations.py
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Setup (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the data pipeline
```powershell
python -m src.data_processing
```

## Run Section A demonstrations
```powershell
python -m src.section_a
```

## Launch the dashboard
```powershell
streamlit run app.py
```
Open the local URL printed by Streamlit (normally http://localhost:8501).

## Dataset limitations
The supplied `ev_campus_dataset.csv` contains 1,200 records and nine columns.
It does not contain calendar dates, ambient temperature, grid demand, or solar
generation. Therefore, date filtering and the exact grid-demand-versus-solar
time-series panel requested in the exam cannot be computed from this file.
The dashboard clearly labels its hourly energy plot as a proxy and uses available
telemetry for correlation analysis. Do not describe proxy charts as actual grid
demand or solar generation.

## Financial assumptions
The examination brief does not specify tariff rules. For a reproducible example,
this implementation assumes AC = RM6/hour, DC = RM15/hour, a 15% peak surcharge
for records labelled `Grid_Surge`, and RM0.25 per overstay minute. These are
illustrative assumptions and must be replaced if the lecturer supplied official
tariffs elsewhere. Carbon savings use the required factor of 0.475 kg CO2/kWh.
