
import io
import math
import yaml
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# -------------------------------
# App setup
# -------------------------------
st.set_page_config(page_title="Mykonos CO₂ — MVP & Traveler Calculator", layout="wide")
st.title("🌍 Mykonos CO₂ — MVP & Traveler Calculator")

st.caption("Demo tool: (1) MVP municipal calculator (upload CSV) and (2) a traveler footprint tool (country/airport/aircraft or helicopter) + on-island daily transport. Factors are indicative—replace with official values.")

# -------------------------------
# Constants
# -------------------------------
JMK = {"iata": "JMK", "name": "Mykonos International Airport", "lat": 37.4351, "lon": 25.3481}
ATH = {"iata": "ATH", "name": "Athens International Airport", "lat": 37.9364, "lon": 23.9445}

# Minimal, editable mapping of countries → representative origin airport (lat/lon).
COUNTRY_AIRPORTS = {
    "Albania":        {"iata": "TIA", "name": "Tirana",               "lat": 41.4147, "lon": 19.7206},
    "Austria":        {"iata": "VIE", "name": "Vienna",               "lat": 48.1103, "lon": 16.5697},
    "Belgium":        {"iata": "BRU", "name": "Brussels",             "lat": 50.9010, "lon": 4.4844},
    "Bulgaria":       {"iata": "SOF", "name": "Sofia",                "lat": 42.6967, "lon": 23.4114},
    "Croatia":        {"iata": "ZAG", "name": "Zagreb",               "lat": 45.7429, "lon": 16.0688},
    "Cyprus":         {"iata": "LCA", "name": "Larnaca",              "lat": 34.8809, "lon": 33.6250},
    "Czechia":        {"iata": "PRG", "name": "Prague",               "lat": 50.1008, "lon": 14.26},
    "Denmark":        {"iata": "CPH", "name": "Copenhagen",           "lat": 55.6180, "lon": 12.6508},
    "Estonia":        {"iata": "TLL", "name": "Tallinn",              "lat": 59.4133, "lon": 24.8328},
    "Finland":        {"iata": "HEL", "name": "Helsinki",             "lat": 60.3172, "lon": 24.9633},
    "France":         {"iata": "CDG", "name": "Paris (CDG)",          "lat": 49.0097, "lon": 2.5479},
    "Germany":        {"iata": "FRA", "name": "Frankfurt",            "lat": 50.0379, "lon": 8.5622},
    "Greece":         {"iata": "ATH", "name": "Athens",               "lat": 37.9364, "lon": 23.9445},
    "Hungary":        {"iata": "BUD", "name": "Budapest",             "lat": 47.4330, "lon": 19.2610},
    "Iceland":        {"iata": "KEF", "name": "Reykjavík (KEF)",      "lat": 63.9850, "lon": -22.6056},
    "Ireland":        {"iata": "DUB", "name": "Dublin",               "lat": 53.4213, "lon": -6.2701},
    "Italy":          {"iata": "FCO", "name": "Rome (FCO)",           "lat": 41.8003, "lon": 12.2389},
    "Latvia":         {"iata": "RIX", "name": "Riga",                 "lat": 56.9236, "lon": 23.9711},
    "Lithuania":      {"iata": "VNO", "name": "Vilnius",              "lat": 54.6341, "lon": 25.2858},
    "Luxembourg":     {"iata": "LUX", "name": "Luxembourg",           "lat": 49.6266, "lon": 6.2115},
    "Malta":          {"iata": "MLA", "name": "Malta",                "lat": 35.8575, "lon": 14.4775},
    "Netherlands":    {"iata": "AMS", "name": "Amsterdam",            "lat": 52.3086, "lon": 4.7639},
    "Norway":         {"iata": "OSL", "name": "Oslo",                 "lat": 60.2028, "lon": 11.0839},
    "Poland":         {"iata": "WAW", "name": "Warsaw",               "lat": 52.1657, "lon": 20.9671},
    "Portugal":       {"iata": "LIS", "name": "Lisbon",               "lat": 38.7742, "lon": -9.1342},
    "Romania":        {"iata": "OTP", "name": "Bucharest",            "lat": 44.5711, "lon": 26.0850},
    "Serbia":         {"iata": "BEG", "name": "Belgrade",             "lat": 44.8184, "lon": 20.3091},
    "Slovakia":       {"iata": "BTS", "name": "Bratislava",           "lat": 48.1698, "lon": 17.2126},
    "Slovenia":       {"iata": "LJU", "name": "Ljubljana",            "lat": 46.2237, "lon": 14.4576},
    "Spain":          {"iata": "MAD", "name": "Madrid",               "lat": 40.4722, "lon": -3.5608},
    "Sweden":         {"iata": "ARN", "name": "Stockholm (ARN)",      "lat": 59.6519, "lon": 17.9186},
    "Switzerland":    {"iata": "ZRH", "name": "Zurich",               "lat": 47.4581, "lon": 8.5555},
    "United Kingdom": {"iata": "LHR", "name": "London (LHR)",         "lat": 51.4700, "lon": -0.4543},
    "United States":  {"iata": "JFK", "name": "New York (JFK)",       "lat": 40.6413, "lon": -73.7781},
    "Canada":         {"iata": "YYZ", "name": "Toronto (YYZ)",        "lat": 43.6777, "lon": -79.6248},
    "Brazil":         {"iata": "GRU", "name": "São Paulo (GRU)",      "lat": -23.4356, "lon": -46.4731},
    "UAE":            {"iata": "DXB", "name": "Dubai",                "lat": 25.2532, "lon": 55.3657},
    "Qatar":          {"iata": "DOH", "name": "Doha",                 "lat": 25.2731, "lon": 51.6081},
    "Turkey":         {"iata": "IST", "name": "Istanbul (IST)",       "lat": 41.2753, "lon": 28.7519},
    "Australia":      {"iata": "SYD", "name": "Sydney",               "lat": -33.9399, "lon": 151.1753},
    "South Africa":   {"iata": "JNB", "name": "Johannesburg",         "lat": -26.1327, "lon": 28.2314},
    "Saudi Arabia":   {"iata": "RUH", "name": "Riyadh",               "lat": 24.9576, "lon": 46.6988},
    "India":          {"iata": "DEL", "name": "Delhi",                "lat": 28.5562, "lon": 77.1000},
    "China":          {"iata": "PEK", "name": "Beijing",              "lat": 40.0799, "lon": 116.6031},
    "Japan":          {"iata": "HND", "name": "Tokyo (HND)",          "lat": 35.5494, "lon": 139.7798},
}

# Greek island airports (for helicopter from Athens; coords used for great-circle distance)
GREEK_ISLANDS = {
    "Mykonos (JMK)":      {"lat": 37.4351, "lon": 25.3481},
    "Santorini (JTR)":    {"lat": 36.3992, "lon": 25.4793},
    "Heraklion (HER)":    {"lat": 35.3397, "lon": 25.1803},
    "Rhodes (RHO)":       {"lat": 36.4054, "lon": 28.0862},
    "Naxos (JNX)":        {"lat": 37.0810, "lon": 25.3681},
    "Paros (PAS)":        {"lat": 37.0206, "lon": 25.1132},
    "Skiathos (JSI)":     {"lat": 39.1771, "lon": 23.5037},
    "Chios (JKH)":        {"lat": 38.3431, "lon": 26.1417},
    "Lesvos/Mytilene (MJT)": {"lat": 39.0579, "lon": 26.5987},
    "Corfu (CFU)":        {"lat": 39.6019, "lon": 19.9117},
    "Zakynthos (ZTH)":    {"lat": 37.7510, "lon": 20.8843},
    "Kos (KGS)":          {"lat": 36.7933, "lon": 27.0917},
}

# Aircraft-type factors (approx kgCO2e per passenger-kilometre). Edit as needed.
AIRCRAFT_FACTORS = {
    "Narrow-body (A320/B737)": 0.13,
    "A321neo / 737 MAX": 0.11,
    "Wide-body (A330/B787)": 0.10,
    "A350 / 787-10 (efficient)": 0.09,
    "Generic short-haul": 0.15,
    "Generic long-haul": 0.11,
}

# Helicopter factors (approx kgCO2e per passenger-km) — indicative placeholders.
HELICOPTER_FACTORS = {
    "Light single (e.g., H125)": 0.25,
    "Light twin (e.g., H135/H145)": 0.30,
    "Medium twin (e.g., AW139)": 0.35,
}

# On-island daily vehicle factors (kgCO2e per km)
ISLAND_VEHICLE_FACTORS = {
    "Car (petrol)": 0.18,
    "Car (diesel)": 0.17,
    "Car (hybrid)": 0.11,
    "Car (EV)": 0.05,        # depends on grid; indicative
    "Scooter / moped": 0.07,
    "ATV (quad)": 0.12,
    "Bicycle": 0.0,
    "E-bike": 0.01,
}

# -------------------------------
# Helpers
# -------------------------------
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def compute_emissions(distance_km, pax_factor):
    return distance_km * pax_factor

# -------------------------------
# Sidebar: global options
# -------------------------------
st.sidebar.header("Options")
round_trip = st.sidebar.checkbox("Round trip", value=True)
island_days = st.sidebar.number_input("Days on island (for daily transport)", min_value=1, value=3, step=1)

# -------------------------------
# Tabs
# -------------------------------
tab_trav, tab_mvp = st.tabs(["✈️ Traveler Calculator", "🏛️ Municipal MVP (CSV)"])

with tab_trav:
    st.subheader("✈️ Flight / 🚁 Helicopter to Greek islands + on-island daily footprint")

    mode = st.radio("Travel mode to the island", ["Flight (airplane)", "Helicopter from Athens"], horizontal=True)

    if mode == "Flight (airplane)":
        countries = sorted(COUNTRY_AIRPORTS.keys())
        country = st.selectbox("Country (alphabetical)", countries, index=countries.index("United Kingdom") if "United Kingdom" in countries else 0)
        origin = COUNTRY_AIRPORTS[country]

        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.write(f"**Origin airport**: {origin['name']} ({origin['iata']})")
            st.write(f"**Coordinates**: {origin['lat']:.4f}, {origin['lon']:.4f}")
        with col2:
            st.write(f"**Destination**: {JMK['name']} ({JMK['iata']})")
            st.write(f"**Coordinates**: {JMK['lat']:.4f}, {JMK['lon']:.4f}")
        with col3:
            d_km = haversine_km(origin["lat"], origin["lon"], JMK["lat"], JMK["lon"])
            st.metric("Great-circle distance (one-way)", f"{d_km:,.0f} km")

        manual = st.checkbox("Override distance manually (km)")
        if manual:
            d_km = st.number_input("Distance (one-way, km)", min_value=1.0, value=float(f"{d_km:.0f}"), step=1.0)

        ac_type = st.selectbox("Aircraft / factor (kgCO₂e per passenger-km)", list(AIRCRAFT_FACTORS.keys()))
        pax_factor = AIRCRAFT_FACTORS[ac_type]

        legs = 2 if round_trip else 1
        total_distance = d_km * legs
        trip_kgco2e = compute_emissions(total_distance, pax_factor)
        flight_details = f"{ac_type} × {total_distance:,.0f} km ({'round-trip' if legs==2 else 'one-way'})"

    else:
        island_name = st.selectbox("Greek island (heli destination)", sorted(GREEK_ISLANDS.keys()))
        dest = GREEK_ISLANDS[island_name]
        d_km = haversine_km(ATH["lat"], ATH["lon"], dest["lat"], dest["lon"])

        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.write(f"**Origin**: {ATH['name']} ({ATH['iata']})")
            st.write(f"**Coordinates**: {ATH['lat']:.4f}, {ATH['lon']:.4f}")
        with col2:
            st.write(f"**Destination**: {island_name}")
            st.write(f"**Coordinates**: {dest['lat']:.4f}, {dest['lon']:.4f}")
        with col3:
            st.metric("Great-circle distance (one-way)", f"{d_km:,.0f} km")

        heli_type = st.selectbox("Helicopter / factor (kgCO₂e per passenger-km)", list(HELICOPTER_FACTORS.keys()))
        pax_factor = HELICOPTER_FACTORS[heli_type]

        legs = 2 if round_trip else 1
        total_distance = d_km * legs
        trip_kgco2e = compute_emissions(total_distance, pax_factor)
        flight_details = f"{heli_type} × {total_distance:,.0f} km ({'round-trip' if legs==2 else 'one-way'})"

    st.markdown("---")
    st.subheader("🚗 On-island daily transport")
    veh = st.selectbox("Vehicle type", list(ISLAND_VEHICLE_FACTORS.keys()))
    veh_factor = ISLAND_VEHICLE_FACTORS[veh]
    km_per_day = st.number_input("Estimated km per day on island", min_value=0.0, value=30.0, step=5.0)
    daily_transport_kg = veh_factor * km_per_day
    total_island_kg = daily_transport_kg * island_days

    st.markdown("### Results")
    res = pd.DataFrame({
        "Component": ["Trip to island", "On-island transport"],
        "Details": [
            flight_details,
            f"{veh} × {km_per_day:.0f} km/day × {island_days} days",
        ],
        "kgCO2e": [trip_kgco2e, total_island_kg]
    })
    res["tCO2e"] = res["kgCO2e"] / 1000.0
    st.dataframe(res, use_container_width=True, hide_index=True)

    total = res["tCO2e"].sum()
    colA, colB = st.columns(2)
    with colA:
        st.metric("Total (tCO₂e)", f"{total:,.3f}")
    with colB:
        st.metric("Trip share (%)", f"{(res.loc[0,'kgCO2e'] / res['kgCO2e'].sum() * 100):.1f}%")

    fig = px.pie(res, names="Component", values="kgCO2e", hole=0.5, title="Share of components (kgCO₂e)")
    st.plotly_chart(fig, use_container_width=True)

    st.info("Notes: Factors are indicative. For precise results use official emission factors per aircraft/helicopter/route and electricity mix for EVs. Distances use great-circle (haversine).")

# -------------------------------
# Municipal MVP tab
# -------------------------------
tab_mvp.subheader("🏛️ Municipal MVP — Upload activities CSV & factors")
tab_mvp.caption("Columns: ετος,μηνας,κατηγορια,υποκατηγορια,μονάδα,ποσοτητα,σημειωσεις")

# Sidebar factors loader
st.sidebar.header("Factors (YAML)")
DEFAULT_FACTORS = b"""
ηλεκτρική_ενέργεια:
  kgco2e_ανα_kwh: 0.40
καύσιμα:
  πετρέλαιο_θέρμανσης_kgco2e_ανα_l: 2.68
  ντίζελ_kgco2e_ανα_l: 2.68
  βενζίνη_kgco2e_ανα_l: 2.31
μεταφορές:
  αυτοκίνητο_kgco2e_ανα_km: 0.18
  λεωφορείο_kgco2e_ανα_επιβατοχλμ: 0.08
  πλοίο_kgco2e_ανα_επιβάτη_km: 0.12
  αεροπορικό_kgco2e_ανα_επιβάτη_km: 0.13
απόβλητα:
  συμμικτα_kgco2e_ανα_kg: 1.2
  ανακυκλωση_kgco2e_ανα_kg: 0.1
νερό:
  αφαλατωση_kwh_ανα_m3: 3.5
λύματα:
  kgco2e_ανα_m3: 0.5
τουρισμός:
  διανυκτέρευση_kgco2e_ανα_επισκέπτη: 15
"""
uploaded_yaml = st.sidebar.file_uploader("Upload factors.yaml", type=["yaml","yml"])
try:
    factors = yaml.safe_load(io.BytesIO(uploaded_yaml.read())) if uploaded_yaml else yaml.safe_load(io.BytesIO(DEFAULT_FACTORS))
except Exception:
    st.sidebar.error("Invalid YAML. Using defaults.")
    factors = yaml.safe_load(io.BytesIO(DEFAULT_FACTORS))

def compute_co2e(row, factors):
    cat = row["κατηγορια"]
    sub = str(row["υποκατηγορια"]) if not pd.isna(row["υποκατηγορια"]) else ""
    unit = row["μονάδα"]
    qty = float(row["ποσοτητα"]) if pd.notna(row["ποσοτητα"]) else 0.0
    f = factors

    if cat == "ηλεκτρική_ενέργεια" and unit == "kWh":
        return qty * f["ηλεκτρική_ενέργεια"]["kgco2e_ανα_kwh"]

    if cat == "καύσιμα":
        if sub in ["ντίζελ", "πετρέλαιο_θέρμανσης", "βενζίνη"] and unit == "l":
            key = f"{sub}_kgco2e_ανα_l"
            return qty * f["καύσιμα"].get(key, 0)

    if cat == "μεταφορές":
        if sub == "εντος_νησιού" and unit == "km":
            return qty * f["μεταφορές"]["αυτοκίνητο_kgco2e_ανα_km"]
        if sub == "πλοίο" and unit == "επιβάτης_km":
            return qty * f["μεταφορές"]["πλοίο_kgco2e_ανα_επιβάτη_km"]
        if sub == "αεροπορικά" and unit == "επιβάτης_km":
            return qty * f["μεταφορές"]["αεροπορικό_kgco2e_ανα_επιβάτη_km"]
        if sub == "λεωφορείο" and unit == "επιβατοχλμ":
            return qty * f["μεταφορές"]["λεωφορείο_kgco2e_ανα_επιβατοχλμ"]

    if cat == "απόβλητα":
        if sub == "συμμικτα" and unit == "kg":
            return qty * f["απόβλητα"]["συμμικτα_kgco2e_ανα_kg"]
        if sub == "ανακυκλωση" and unit == "kg":
            return qty * f["απόβλητα"]["ανακυκλωση_kgco2e_ανα_kg"]

    if cat == "νερό" and sub == "αφαλάτωση" and unit == "m3":
        kwh_per_m3 = f["νερό"]["αφαλατωση_kwh_ανα_m3"]
        elec = kwh_per_m3 * qty * f["ηλεκτρική_ενέργεια"]["kgco2e_ανα_kwh"]
        return elec

    if cat == "λύματα" and unit == "m3":
        return qty * f["λύματα"]["kgco2e_ανα_m3"]

    if cat == "τουρισμός" and sub == "διανυκτερεύσεις" and unit == "επισκέπτης_νύχτα":
        return qty * f["τουρισμός"]["διανυκτέρευση_kgco2e_ανα_επισκέπτη"]

    return 0.0

# Data upload controls
sample_btn = tab_mvp.button("Load sample data")
df = None
if sample_btn:
    try:
        df = pd.read_csv("data/sample_activity_data.csv")
    except Exception:
        tab_mvp.error("Sample file not found. Ensure data/sample_activity_data.csv exists in the repo.")

uploaded = tab_mvp.file_uploader("Upload CSV", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)

if df is None:
    tab_mvp.info("No data yet. Load the sample or upload your CSV.")
else:
    tab_mvp.dataframe(df, use_container_width=True, hide_index=True)
    df_calc = df.copy()
    df_calc["kgCO2e"] = df_calc.apply(lambda r: compute_co2e(r, factors), axis=1)
    df_calc["tCO2e"] = df_calc["kgCO2e"] / 1000.0

    tab_mvp.subheader("Summary")
    c1, c2, c3 = tab_mvp.columns(3)
    with c1:
        tab_mvp.metric("Total (tCO₂e)", f"{df_calc['tCO2e'].sum():,.0f}")
    with c2:
        tab_mvp.metric("Mean per record (tCO₂e)", f"{df_calc['tCO2e'].mean():,.2f}")
    with c3:
        tab_mvp.metric("Records", f"{len(df_calc):,}")

    tab_mvp.subheader("By category")
    cat = df_calc.groupby("κατηγορια")["tCO2e"].sum().reset_index().sort_values("tCO2e", ascending=False)
    tab_mvp.dataframe(cat, use_container_width=True, hide_index=True)
    fig1 = px.pie(cat, names="κατηγορια", values="tCO2e", hole=0.5, title="Share by category (% tCO₂e)")
    tab_mvp.plotly_chart(fig1, use_container_width=True)

    tab_mvp.subheader("Detailed results")
    tab_mvp.dataframe(df_calc, use_container_width=True, hide_index=True)

    # Download
    csv_bytes = df_calc.to_csv(index=False).encode("utf-8")
    tab_mvp.download_button("Download results (CSV)", data=csv_bytes, file_name="results_co2e.csv", mime="text/csv")
