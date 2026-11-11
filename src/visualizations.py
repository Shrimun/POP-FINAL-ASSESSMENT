"""Matplotlib and Seaborn charts for the EV charging dashboard."""
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set_theme(style="whitegrid", context="notebook")


def create_dashboard_figure(df: pd.DataFrame):
    """Create three analytical panels using only columns present in the CSV."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Panel 1: The supplied dataset has no timestamp, grid-demand, or solar
    # generation columns. Show hourly session energy as an honest proxy,
    # rather than inventing grid demand or solar generation.
    hourly = df.groupby("Start_Hour")["Energy_kWh"].sum()
    axes[0].plot(hourly.index, hourly.values, marker="o", linewidth=2)
    axes[0].set_title("Hourly Energy Delivered")
    axes[0].set_xlabel("Session Start Hour")
    axes[0].set_ylabel("Energy Delivered (kWh)")

    # Panel 2: Compare session cost across the three user categories.
    sns.boxplot(
        data=df, x="User_Type", y="Net_Billable_MYR",
        order=["Student", "Staff", "Visitor"], ax=axes[1]
    )
    axes[1].set_title("Charging Cost by User Type")
    axes[1].set_xlabel("User Type")
    axes[1].set_ylabel("Net Billable Amount (MYR)")

    # Panel 3: Battery temperature versus energy, with a linear trendline.
    sns.regplot(
        data=df, x="Battery_Temp_C", y="Energy_kWh",
        scatter_kws={"alpha": 0.35}, line_kws={"color": "red"}, ax=axes[2]
    )
    axes[2].set_title("Battery Temperature vs Energy")
    axes[2].set_xlabel("Battery Temperature (°C)")
    axes[2].set_ylabel("Energy Delivered (kWh)")

    fig.tight_layout()
    return fig


def create_revenue_chart(df: pd.DataFrame):
    """Create a grouped hourly revenue chart for AC and DC chargers."""
    pivot = df.pivot_table(
        index="Start_Hour", columns="Charger_Type",
        values="Net_Billable_MYR", aggfunc="sum", fill_value=0
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    pivot.plot(kind="bar", ax=ax)
    ax.set_title("Hourly Charging Revenue by Charger Type")
    ax.set_xlabel("Charging Start Hour")
    ax.set_ylabel("Revenue (MYR)")
    ax.legend(title="Charger Type")
    fig.tight_layout()
    return fig


def create_correlation_heatmap(df: pd.DataFrame):
    """Plot correlations among numeric telemetry fields available in the CSV."""
    cols = [
        "Battery_Temp_C", "Duration_Mins", "Energy_kWh",
        "Overstay_Mins", "Start_Hour"
    ]
    corr = df[cols].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(corr, annot=True, cmap="coolwarm", center=0,
                vmin=-1, vmax=1, fmt=".2f", ax=ax)
    ax.set_title("Correlation Between Available Energy Variables")
    fig.tight_layout()
    return fig


def save_charts(df: pd.DataFrame, output_dir: Path):
    """Save generated charts as PNG files for the report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    charts = {
        "dashboard_panels.png": create_dashboard_figure(df),
        "hourly_revenue.png": create_revenue_chart(df),
        "correlation_heatmap.png": create_correlation_heatmap(df),
    }
    for filename, fig in charts.items():
        fig.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
        plt.close(fig)
