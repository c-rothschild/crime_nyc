#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from sodapy import Socrata
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("🗽 NYC Crime Heatmap")

# — Sidebar controls —
st.sidebar.header("Filter Options")
DATASET_ID = "5uac-w243"
client = Socrata("data.cityofnewyork.us", None)

@st.cache_data
def get_crime_types():
    recs = client.get(DATASET_ID, select="DISTINCT ofns_desc", limit=5000)
    types = sorted(r['ofns_desc'] for r in recs if r.get('ofns_desc'))
    return ["ALL CRIMES"] + types

crime_options = get_crime_types()
selected_crimes = st.sidebar.multiselect("Crime Types", crime_options, default=["ALL CRIMES"])
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2024-01-01"))
end_date   = st.sidebar.date_input("End Date",   value=pd.to_datetime("2025-01-01"))
radius     = st.sidebar.slider("Heat Radius", min_value=5, max_value=30, value=15)
blur       = st.sidebar.slider("Heat Blur",   min_value=5, max_value=30, value=10)

@st.cache_data
def fetch_data(crimes, start, end):
    where = (
        f"cmplnt_fr_dt >= '{start}T00:00:00.000' AND "
        f"cmplnt_fr_dt <= '{end}T23:59:59.000'"
    )
    if "ALL CRIMES" not in crimes:
        safe_list = "', '".join(crimes)
        where += f" AND ofns_desc IN ('{safe_list}')"
    recs = client.get(DATASET_ID, where=where, limit=100_000)
    df = pd.DataFrame.from_records(recs)
    df['latitude']  = pd.to_numeric(df.get('latitude'),  errors='coerce')
    df['longitude'] = pd.to_numeric(df.get('longitude'), errors='coerce')
    return df.dropna(subset=['latitude','longitude'])

# Load & filter
df = fetch_data(selected_crimes, start_date.isoformat(), end_date.isoformat())

# Show warning if empty
if df.empty:
    st.warning("No incidents found for those filters.")
else:
    # Build map
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=11)
    heat_data = df[['latitude','longitude']].values.tolist()
    HeatMap(heat_data, radius=radius, blur=blur).add_to(m)

    # Embed in Streamlit
    st_folium(m, width=800, height=600)