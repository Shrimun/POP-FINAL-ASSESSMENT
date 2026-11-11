"""Section A demonstrations required by the examination brief."""
import numpy as np
import pandas as pd
from src.calculations import identify_high_risk_sessions, calculate_surcharge_revenue


def run_section_a_examples(df: pd.DataFrame) -> None:
    """Run NumPy, Pandas, and functional-programming examples."""
    print("\nSECTION A(a): NUMPY EXAMPLES")
    # Convert selected telemetry columns into a compact NumPy matrix.
    telemetry = df[["Start_Hour", "Energy_kWh", "Battery_Temp_C"]].to_numpy()

    # 2D slicing: select records starting in peak daytime hours (10:00-14:00).
    peak_hours = telemetry[
        (telemetry[:, 0] >= 10) & (telemetry[:, 0] <= 14)
    ]
    print("Peak-hour telemetry shape:", peak_hours.shape)

    # Boolean masking: identify battery temperatures above 45 degrees C.
    hot_batteries = telemetry[telemetry[:, 2] > 45]
    print("Battery readings above 45°C:", len(hot_batteries))

    print("\nSECTION A(a): PANDAS EXAMPLES")
    # Median imputation example for a numeric telemetry field.
    demo = df.copy()
    demo["Energy_kWh"] = demo["Energy_kWh"].fillna(
        demo["Energy_kWh"].median()
    )
    print("Missing energy values after median imputation:",
          int(demo["Energy_kWh"].isna().sum()))

    # Group-wise revenue calculation with a DataFrame abstraction.
    revenue = demo.groupby("Charger_Type")["Net_Billable_MYR"].sum()
    print("Revenue by charger type (MYR):\n", revenue)

    print("\nSECTION A(b): FILTER, MAP, REDUCE")
    risk = identify_high_risk_sessions(df)
    records = risk[["Base_Fee_MYR"]].to_dict("records")
    total = calculate_surcharge_revenue(records, surcharge_rate=0.15)
    print("High-risk sessions:", len(risk))
    print("Total 15% surcharge (MYR):", round(total, 2))


if __name__ == "__main__":
    from src.data_processing import process_dataset
    run_section_a_examples(process_dataset())
