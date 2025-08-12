import streamlit as st
import pandas as pd
import yaml
import plotly.express as px

st.title("🌍 Mykonos CO₂ MVP Demo")

st.write("Upload your activity data CSV or use the sample dataset.")

# Load factors
with open("factors.yaml", "r", encoding="utf-8") as f:
    factors = yaml.safe_load(f)

uploaded = st.file_uploader("Upload CSV", type="csv")
if uploaded:
    df = pd.read_csv(uploaded)
else:
    df = pd.read_csv("data/sample_activity_data.csv")

st.dataframe(df)

# Placeholder for calculation logic
st.write("Factors:", factors)
