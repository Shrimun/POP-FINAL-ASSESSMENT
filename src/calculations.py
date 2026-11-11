"""Functional-programming examples and reusable dashboard calculations."""
from functools import reduce
import pandas as pd


def identify_high_risk_sessions(df: pd.DataFrame,
                                overstay_threshold: float = 20,
                                temperature_threshold: float = 40) -> pd.DataFrame:
    """Filter sessions exceeding both risk thresholds."""
    mask = (
        (df["Overstay_Mins"] > overstay_threshold)
        & (df["Battery_Temp_C"] > temperature_threshold)
    )
    return df.loc[mask].copy()


def calculate_surcharge_revenue(records, surcharge_rate: float = 0.15):
    """Map a 15% surcharge onto base fees and reduce to total surcharge."""
    # map() avoids building an additional intermediate list of fee values.
    surcharge_values = map(
        lambda record: float(record["Base_Fee_MYR"]) * surcharge_rate,
        records
    )
    # reduce() accumulates the surcharge total in one pass.
    return reduce(lambda total, amount: total + amount, surcharge_values, 0.0)


def add_surcharge_to_risk_sessions(df: pd.DataFrame,
                                   surcharge_rate: float = 0.15) -> pd.DataFrame:
    """Return high-risk sessions with surcharge and adjusted bill columns."""
    result = df.copy()
    result["Surcharge_MYR"] = (
        result["Base_Fee_MYR"] * surcharge_rate
    ).round(2)
    result["Adjusted_Bill_MYR"] = (
        result["Net_Billable_MYR"] + result["Surcharge_MYR"]
    ).round(2)
    return result


def revenue_by_hour_and_charger(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate net revenue by charging start hour and charger type."""
    return (
        df.groupby(["Start_Hour", "Charger_Type"], as_index=False)
        ["Net_Billable_MYR"].sum()
    )


def kpi_summary(df: pd.DataFrame) -> dict:
    """Calculate headline dashboard KPIs from the selected records."""
    return {
        "energy": float(df["Energy_kWh"].sum()),
        "carbon": float(df["Carbon_Savings_kgCO2"].sum()),
        "revenue": float(df["Net_Billable_MYR"].sum()),
        "alerts": int(
            ((df["Overstay_Mins"] > 20) & (df["Battery_Temp_C"] > 40)).sum()
        ),
        "sessions": int(len(df)),
    }
