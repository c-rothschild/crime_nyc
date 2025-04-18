# 1. Imports
import pandas as pd
import folium
from sodapy import Socrata
from folium.plugins import HeatMap
from datetime import datetime
from datetime import datetime
from ipywidgets import interactive, widgets, HTML
from IPython.display import clear_output
from ipywidgets.embed import embed_minimal_html

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("data.cityofnewyork.us", None)

# Get unique offense types for the dropdown
crime_types = client.get("5uac-w243", select="DISTINCT ofns_desc", limit=100)
crime_options = [crime["ofns_desc"] for crime in crime_types]



def fetch_crime_data(crime_type, start_date_str, end_date_str, limit=5000):
    """Fetch crime data based on parameters"""
    query = f"cmplnt_fr_dt <= '{end_date_str}' AND cmplnt_fr_dt >= '{start_date_str}'"
    if crime_type != "ALL CRIMES":
        query += f" AND ofns_desc = '{crime_type}'"
    print(f"Query: {query}")
    results = client.get("5uac-w243", limit=limit, where=query)
    df = pd.DataFrame.from_records(results)
    
    # Clean coordinates
    if 'latitude' in df.columns and 'longitude' in df.columns:
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        df = df.dropna(subset=['latitude', 'longitude'])p
        df = df[(df['longitude'] != 0) & (df['latitude'] != 0)]
    
    return df

def create_crime_map(crime_type="RAPE",
                     start_date_str="2024-02-16",
                     end_date_str="2025-02-16",
                     show_markers=True,
                     heat_radius=15,
                     heat_blur=10):
    # 1) Get your DataFrame
    df = fetch_crime_data(crime_type, f"{start_date_str}T00:00:00.000", f"{end_date_str}T00:00:00.000")
    if df.empty:
        return HTML("<b>No data found for those criteria.</b>")

    # 2) Build the Folium map
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=11)
    coords = df[['latitude','longitude']].values.tolist()
    HeatMap(coords, radius=heat_radius, blur=heat_blur,
            gradient={'0.4':'blue','0.65':'lime','0.8':'orange','1':'red'}
    ).add_to(m)
    # (optionally add markers…)

    # 3) Grab the rendered HTML from the map
    map_html = m.get_root().render()

    # 4) Return it as an HTML widget
    return HTML(map_html)


# Add ALL CRIMES option to the beginning
crime_options = ["ALL CRIMES"] + crime_options

# Create interactive widgets
crime_dropdown = widgets.Dropdown(
    options=crime_options,
    value='RAPE',
    description='Crime Type:',
    style={'description_width': 'initial'}
)

start_date_picker = widgets.DatePicker(
    description='Start Date:',
    value=datetime(2024, 2, 16).date(),
    style={'description_width': 'initial'}
)

end_date_picker = widgets.DatePicker(
    description='End Date:',
    value=datetime(2025, 2, 16).date(),
    style={'description_width': 'initial'}
)

show_markers_checkbox = widgets.Checkbox(
    value=True,
    description='Show Individual Markers',
    style={'description_width': 'initial'}
)

radius_slider = widgets.IntSlider(
    value=15,
    min=5,
    max=30,
    step=1,
    description='Heat Radius:',
    style={'description_width': 'initial'}
)

blur_slider = widgets.IntSlider(
    value=10,
    min=5,
    max=30,
    step=1,
    description='Heat Blur:',
    style={'description_width': 'initial'}
)

# Create interactive visualization
map_widget = interactive(create_crime_map,
         crime_type=crime_dropdown,
         start_date_str=start_date_picker,
         end_date_str=end_date_picker,
         show_markers=show_markers_checkbox,
         heat_radius=radius_slider,
         heat_blur=blur_slider)

# Finally, export everything (controls + map) into a self‑contained HTML
embed_minimal_html(
    "nyc_crime_heatmap.html",
    views=[map_widget],
    title="NYC Crime Heatmap"
)