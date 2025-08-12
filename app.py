import io
import sys

# Runtime safe import for yaml
try:
    import yaml
except ModuleNotFoundError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml==6.0.2"])
    import yaml

import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Mykonos CO₂ — MVP & Traveler Calculator", layout="wide")
st.title("🌍 Mykonos CO₂ — MVP & Traveler Calculator")

st.write("This is a hotfix version with PyYAML auto-install at runtime to avoid import errors.")

# Minimal placeholder content
st.header("Traveler Calculator")
st.info("Traveler calculation functionality here.")

st.header("Municipal MVP")
st.info("Municipal MVP CSV calculation functionality here.")
