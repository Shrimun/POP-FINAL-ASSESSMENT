
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Smart Campus Energy & EV Fleet Dashboard",
    page_icon="⚡",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

# --------------------------------------------------
# 2. LOAD DATASET
# --------------------------------------------------

@st.cache_data
def load_data():

    # Check the project dataset locations in order
    possible_paths = [
        BASE_DIR / "data" / "processed" / "cleaned_energy_sales_data.csv",
        BASE_DIR / "data" / "processed" / "cleaned_energy_sales_data_reference.csv",
        BASE_DIR / "data" / "raw" / "ev_campus_dataset.csv",
        BASE_DIR / "cleaned_energy_sales_data.csv",
        BASE_DIR / "ev_campus_dataset.csv"
    ]

    required_columns = [
        "Session_ID",
        "Charger_Type",
        "User_Type",
        "Start_Hour",
        "Duration_Mins",
        "Energy_kWh",
        "Overstay_Mins",
        "Battery_Temp_C",
        "Grid_Status_Label"
    ]

    for file_path in possible_paths:

        if not file_path.exists():
            continue

        df = pd.read_csv(file_path)

        if df.empty:
            continue

        # Check whether the dataset has all required columns
        missing_columns = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            continue

        # Convert numerical columns into numeric values
        numeric_columns = [
            "Start_Hour",
            "Duration_Mins",
            "Energy_kWh",
            "Overstay_Mins",
            "Battery_Temp_C",
            "Duration_Hours",
            "Power_Rate_kW",
            "Carbon_Savings_kgCO2",
            "Base_Rate_MYR",
            "Base_Fee_MYR",
            "Peak_Surge_MYR",
            "Overstay_Fee_MYR",
            "Net_Billable_MYR"
        ]

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

                df[col] = df[col].fillna(0)

        # Calculate derived columns only if missing
        if "Duration_Hours" not in df.columns:
            df["Duration_Hours"] = (
                df["Duration_Mins"] / 60
            )

        if "Power_Rate_kW" not in df.columns:
            df["Power_Rate_kW"] = np.where(
                df["Duration_Hours"] > 0,
                df["Energy_kWh"] / df["Duration_Hours"],
                0
            )

        if "Carbon_Savings_kgCO2" not in df.columns:
            df["Carbon_Savings_kgCO2"] = (
                df["Energy_kWh"] * 0.475
            )

        if "Base_Fee_MYR" not in df.columns:
            df["Base_Fee_MYR"] = (
                df["Energy_kWh"] * 0.50
            )

        if "Peak_Surge_MYR" not in df.columns:
            df["Peak_Surge_MYR"] = 0.0

        if "Overstay_Fee_MYR" not in df.columns:
            df["Overstay_Fee_MYR"] = 0.0

        if "Net_Billable_MYR" not in df.columns:
            df["Net_Billable_MYR"] = (
                df["Base_Fee_MYR"]
                + df["Peak_Surge_MYR"]
                + df["Overstay_Fee_MYR"]
            )

        # Return the first valid dataset
        return df, str(file_path.relative_to(BASE_DIR))

    raise FileNotFoundError(
        "No valid dataset found. Check the data/processed "
        "and data/raw folders."
    )


try:
    df, dataset_source = load_data()

except Exception as error:
    st.error(f"Dataset loading failed: {error}")
    st.stop()


# --------------------------------------------------
# 3. DASHBOARD HEADER
# --------------------------------------------------

st.title("⚡ Smart Campus Energy & EV Fleet Dashboard")

st.markdown(
    "Integrated Smart Energy & Electric Vehicle Fleet "
    "Management Platform"
)


# --------------------------------------------------
# 4. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

# Minimum energy filter
max_energy = float(df["Energy_kWh"].max())

min_energy = st.sidebar.slider(
    "Minimum Energy Delivered (kWh)",
    min_value=0.0,
    max_value=max(max_energy, 1.0),
    value=0.0,
    step=0.5
)

# Charger type filter
charger_options = sorted(
    df["Charger_Type"].dropna().unique().tolist()
)

selected_chargers = st.sidebar.multiselect(
    "Charger Type",
    options=charger_options,
    default=charger_options
)

# User type filter
user_options = sorted(
    df["User_Type"].dropna().unique().tolist()
)

selected_users = st.sidebar.multiselect(
    "User Type",
    options=user_options,
    default=user_options
)

# Battery temperature alert threshold
temperature_threshold = st.sidebar.slider(
    "Battery Temperature Alert Threshold (°C)",
    min_value=30,
    max_value=60,
    value=40,
    step=1
)

# Overstay alert threshold
overstay_threshold = st.sidebar.slider(
    "Overstay Alert Threshold (Minutes)",
    min_value=0,
    max_value=120,
    value=20,
    step=5
)


# --------------------------------------------------
# 5. APPLY DASHBOARD FILTERS
# --------------------------------------------------

filtered = df.copy()

# Apply minimum energy filter
filtered = filtered[
    filtered["Energy_kWh"] >= min_energy
]

# Apply charger filter
# Empty selection means zero matching records
if selected_chargers:

    filtered = filtered[
        filtered["Charger_Type"].isin(selected_chargers)
    ]

else:
    filtered = filtered.iloc[0:0]

# Apply user filter
# Empty selection means zero matching records
if selected_users:

    filtered = filtered[
        filtered["User_Type"].isin(selected_users)
    ]

else:
    filtered = filtered.iloc[0:0]


# --------------------------------------------------
# 6. CALCULATE KPI VALUES
# --------------------------------------------------

total_energy = filtered["Energy_kWh"].sum()

total_carbon = filtered["Carbon_Savings_kgCO2"].sum()

total_revenue = filtered["Net_Billable_MYR"].sum()

# A high-risk session must exceed both thresholds
alerts = filtered[
    (filtered["Overstay_Mins"] > overstay_threshold)
    &
    (filtered["Battery_Temp_C"] > temperature_threshold)
].copy()

active_alerts = len(alerts)


# --------------------------------------------------
# 7. DISPLAY KPI CARDS
# --------------------------------------------------

st.subheader("Executive Performance Indicators")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Total Energy Delivered",
    f"{total_energy:,.2f} kWh"
)

k2.metric(
    "Carbon Offset",
    f"{total_carbon:,.2f} kg CO₂"
)

k3.metric(
    "Total Revenue",
    f"RM {total_revenue:,.2f}"
)

k4.metric(
    "Active High-Risk Alerts",
    f"{active_alerts}"
)

st.divider()


# --------------------------------------------------
# 8. NAVIGATION
# --------------------------------------------------

page = st.radio(
    "Navigation",
    [
        "Executive Overview",
        "Charging Analysis",
        "Alert Centre",
        "Filtered Data"
    ],
    horizontal=True
)


# --------------------------------------------------
# 9. EXECUTIVE OVERVIEW
# --------------------------------------------------

if page == "Executive Overview":

    st.subheader("Executive Overview & Grid Demand")

    if filtered.empty:

        st.warning("No sessions match the selected filters.")

    else:

        col1, col2 = st.columns(2)

        # Hourly energy demand
        with col1:

            st.markdown("#### Hourly Energy Demand")

            hourly = (
                filtered.groupby("Start_Hour")["Energy_kWh"]
                .sum()
                .reset_index()
                .sort_values("Start_Hour")
            )

            fig, ax = plt.subplots(figsize=(7, 4))

            sns.lineplot(
                data=hourly,
                x="Start_Hour",
                y="Energy_kWh",
                marker="o",
                linewidth=2,
                ax=ax
            )

            ax.set_xlabel("Starting Hour")
            ax.set_ylabel("Energy Delivered (kWh)")
            ax.grid(alpha=0.3)

            st.pyplot(fig)
            plt.close(fig)

        # Revenue by user type
        with col2:

            st.markdown("#### Revenue by User Type")

            revenue = (
                filtered.groupby("User_Type")["Net_Billable_MYR"]
                .sum()
                .reset_index()
            )

            fig, ax = plt.subplots(figsize=(7, 4))

            sns.barplot(
                data=revenue,
                x="User_Type",
                y="Net_Billable_MYR",
                ax=ax
            )

            ax.set_xlabel("User Type")
            ax.set_ylabel("Revenue (RM)")
            ax.grid(axis="y", alpha=0.3)

            st.pyplot(fig)
            plt.close(fig)

        # Charging sessions by charger type
        st.markdown("#### Charging Sessions by Charger Type")

        charger_counts = (
            filtered["Charger_Type"]
            .value_counts()
            .rename_axis("Charger Type")
            .reset_index(name="Sessions")
        )

        st.bar_chart(
            charger_counts.set_index("Charger Type")
        )


# --------------------------------------------------
# 10. CHARGING ANALYSIS
# --------------------------------------------------

elif page == "Charging Analysis":

    st.subheader("Charging Revenue & Correlation Analysis")

    if filtered.empty:

        st.warning("No sessions match the selected filters.")

    else:

        col1, col2 = st.columns(2)

        # Revenue by charger type
        with col1:

            st.markdown("#### Revenue by Charger Type")

            revenue = (
                filtered.groupby("Charger_Type")["Net_Billable_MYR"]
                .sum()
                .reset_index()
            )

            fig, ax = plt.subplots(figsize=(6, 4))

            sns.barplot(
                data=revenue,
                x="Charger_Type",
                y="Net_Billable_MYR",
                ax=ax
            )

            ax.set_xlabel("Charger Type")
            ax.set_ylabel("Revenue (RM)")

            st.pyplot(fig)
            plt.close(fig)

        # Battery temperature vs energy
        with col2:

            st.markdown("#### Battery Temperature vs Energy")

            fig, ax = plt.subplots(figsize=(6, 4))

            sns.scatterplot(
                data=filtered,
                x="Battery_Temp_C",
                y="Energy_kWh",
                hue="Charger_Type",
                ax=ax
            )

            ax.set_xlabel("Battery Temperature (°C)")
            ax.set_ylabel("Energy Delivered (kWh)")

            st.pyplot(fig)
            plt.close(fig)

        # Correlation heatmap
        st.markdown("#### Energy Variable Correlation")

        corr_columns = [
            col for col in [
                "Duration_Mins",
                "Energy_kWh",
                "Overstay_Mins",
                "Battery_Temp_C",
                "Power_Rate_kW",
                "Carbon_Savings_kgCO2",
                "Net_Billable_MYR"
            ]
            if col in filtered.columns
        ]

        if len(corr_columns) > 1:

            correlation = filtered[corr_columns].corr()

            fig, ax = plt.subplots(figsize=(9, 5))

            sns.heatmap(
                correlation,
                annot=True,
                cmap="coolwarm",
                fmt=".2f",
                linewidths=0.5,
                ax=ax
            )

            st.pyplot(fig)
            plt.close(fig)

        else:

            st.info("Not enough numerical columns for correlation analysis.")


# --------------------------------------------------
# 11. ALERT CENTRE
# --------------------------------------------------

elif page == "Alert Centre":

    st.subheader("High-Risk Overstay & Battery Alert Centre")

    if alerts.empty:

        st.success(
            "No sessions currently exceed both alert thresholds."
        )

    else:

        st.error(
            f"{len(alerts)} high-risk session(s) identified."
        )

        display_columns = [
            col for col in [
                "Session_ID",
                "Charger_Type",
                "User_Type",
                "Overstay_Mins",
                "Battery_Temp_C",
                "Overstay_Fee_MYR",
                "Net_Billable_MYR"
            ]
            if col in alerts.columns
        ]

        st.dataframe(
            alerts[display_columns],
            use_container_width=True,
            hide_index=True
        )

        # Display actual overstay fees from the dataset
        potential_surcharge = alerts[
            "Overstay_Fee_MYR"
        ].sum()

        st.metric(
            "Overstay Fees from High-Risk Sessions",
            f"RM {potential_surcharge:,.2f}"
        )


# --------------------------------------------------
# 12. FILTERED DATA
# --------------------------------------------------

elif page == "Filtered Data":

    st.subheader("Filtered Charging Session Records")

    st.write(
        f"Showing **{len(filtered):,}** records "
        "based on the selected filters."
    )

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

    # Export filtered records as CSV
    csv_data = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv_data,
        file_name="filtered_energy_sales_data.csv",
        mime="text/csv"
    )


# --------------------------------------------------
# 13. SIDEBAR FOOTER
# --------------------------------------------------

st.sidebar.divider()

st.sidebar.caption(
    f"Source Dataset: {dataset_source}"
)

st.sidebar.caption(
    f"Total Dataset Records: {len(df):,}"
)

st.sidebar.caption(
    f"Filtered Records: {len(filtered):,}"
)
