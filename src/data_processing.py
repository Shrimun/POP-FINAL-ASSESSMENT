"""Load, validate, clean, engineer, and export EV charging session data."""
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "ev_campus_dataset.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_energy_sales_data.csv"

REQUIRED_COLUMNS = [
    "Session_ID", "Charger_Type", "User_Type", "Start_Hour",
    "Duration_Mins", "Energy_kWh", "Overstay_Mins",
    "Battery_Temp_C", "Grid_Status_Label"
]
VALID_CHARGERS = {"AC", "DC"}
VALID_USERS = {"Student", "Staff", "Visitor"}
VALID_GRID_STATUSES = {"Normal", "Grid_Surge", "Overheated"}

# These are transparent project assumptions because the examination brief
# does not provide a tariff table or surcharge rates.
CHARGER_RATES_MYR_PER_HOUR = {"AC": 6.00, "DC": 15.00}
GRID_SURGE_RATE = 0.15
OVERSTAY_RATE_MYR_PER_MIN = 0.25
CARBON_FACTOR_KG_PER_KWH = 0.475


def load_raw_data(file_path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Read the supplied CSV and verify that required columns exist."""
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")
    df = pd.read_csv(file_path)
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    return df


def clean_and_engineer_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean values and derive charging, carbon, and billing metrics."""
    data = df.copy()
    data.columns = data.columns.str.strip()

    # Normalize text categories before validation.
    for col in ["Session_ID", "Charger_Type", "User_Type", "Grid_Status_Label"]:
        data[col] = data[col].astype("string").str.strip()

    # Convert numeric fields safely; invalid strings become missing values.
    numeric_cols = [
        "Start_Hour", "Duration_Mins", "Energy_kWh",
        "Overstay_Mins", "Battery_Temp_C"
    ]
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    # Remove duplicate session identifiers because each row should represent
    # one unique charging session.
    data = data.drop_duplicates(subset=["Session_ID"], keep="first")

    # Impute missing numerical measurements with each column's median.
    for col in numeric_cols:
        median_value = data[col].median()
        data[col] = data[col].fillna(median_value)

    # Validate categories and use explicit safe labels for unexpected values.
    data["Charger_Type"] = data["Charger_Type"].where(
        data["Charger_Type"].isin(VALID_CHARGERS), "Unknown"
    )
    data["User_Type"] = data["User_Type"].where(
        data["User_Type"].isin(VALID_USERS), "Unknown"
    )
    data["Grid_Status_Label"] = data["Grid_Status_Label"].where(
        data["Grid_Status_Label"].isin(VALID_GRID_STATUSES), "Unknown"
    )

    # Apply basic range checks to prevent invalid calculations.
    data["Start_Hour"] = data["Start_Hour"].clip(0, 23)
    data["Duration_Mins"] = data["Duration_Mins"].clip(lower=0)
    data["Energy_kWh"] = data["Energy_kWh"].clip(lower=0)
    data["Overstay_Mins"] = data["Overstay_Mins"].clip(lower=0)
    data["Battery_Temp_C"] = data["Battery_Temp_C"].clip(lower=-20, upper=100)

    # Derive the required operational metrics.
    data["Duration_Hours"] = data["Duration_Mins"] / 60
    data["Power_Rate_kW"] = (
        data["Energy_kWh"] / data["Duration_Hours"].replace(0, pd.NA)
    ).fillna(0)
    data["Carbon_Savings_kgCO2"] = (
        data["Energy_kWh"] * CARBON_FACTOR_KG_PER_KWH
    )

    # Transparent assumed tariffs: AC = RM6/hour; DC = RM15/hour.
    data["Base_Rate_MYR"] = data["Charger_Type"].map(
        CHARGER_RATES_MYR_PER_HOUR
    ).fillna(0)
    data["Base_Fee_MYR"] = data["Duration_Hours"] * data["Base_Rate_MYR"]

    # A 15% peak surcharge is applied only to sessions labelled Grid_Surge.
    data["Peak_Surge_MYR"] = (
        data["Base_Fee_MYR"]
        * GRID_SURGE_RATE
        * data["Grid_Status_Label"].eq("Grid_Surge").astype(int)
    )
    data["Overstay_Fee_MYR"] = (
        data["Overstay_Mins"] * OVERSTAY_RATE_MYR_PER_MIN
    )
    data["Net_Billable_MYR"] = (
        data["Base_Fee_MYR"]
        + data["Peak_Surge_MYR"]
        + data["Overstay_Fee_MYR"]
    )

    money_cols = [
        "Carbon_Savings_kgCO2", "Base_Rate_MYR", "Base_Fee_MYR",
        "Peak_Surge_MYR", "Overstay_Fee_MYR", "Net_Billable_MYR"
    ]
    data[money_cols] = data[money_cols].round(2)
    data["Power_Rate_kW"] = data["Power_Rate_kW"].round(2)
    return data


def process_dataset(file_path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Run the full pipeline, export the cleaned CSV, and print summaries."""
    raw = load_raw_data(file_path)
    cleaned = clean_and_engineer_data(raw)
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(PROCESSED_DATA_PATH, index=False)

    print("DATA PROCESSING COMPLETED")
    print("-" * 45)
    print(f"Original records: {len(raw):,}")
    print(f"Cleaned records:  {len(cleaned):,}")
    print(f"Removed records:  {len(raw) - len(cleaned):,}")
    print(f"Cleaned dataset shape: {cleaned.shape}")
    print("\nMissing values after cleaning:")
    print(cleaned.isna().sum().to_string())
    print("\nSummary statistics:")
    print(cleaned.select_dtypes(include="number").describe().round(2).to_string())
    print(f"\nSaved cleaned dataset: {PROCESSED_DATA_PATH}")
    return cleaned


if __name__ == "__main__":
    process_dataset()
