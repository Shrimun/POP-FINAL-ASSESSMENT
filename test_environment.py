"""Quick dependency and data availability check."""
import pandas as pd
import numpy as np
import matplotlib
import seaborn
import streamlit
from pathlib import Path

print("NumPy:", np.__version__)
print("Pandas:", pd.__version__)
print("Matplotlib:", matplotlib.__version__)
print("Seaborn:", seaborn.__version__)
print("Streamlit:", streamlit.__version__)

data_path = Path("data/raw/ev_campus_dataset.csv")
assert data_path.exists(), f"Dataset missing: {data_path}"
df = pd.read_csv(data_path)
print("Dataset shape:", df.shape)
print("Environment and dataset check passed.")
