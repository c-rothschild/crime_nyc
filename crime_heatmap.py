# 1. Imports
import pandas as pd
import folium
from sodapy import Socrata
from folium.plugins import HeatMap
from datetime import datetime
from datetime import datetime

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("data.cityofnewyork.us", None)

# Get unique offense types for the dropdown
crime_types = client.get("5uac-w243", select="DISTINCT ofns_desc", limit=100)
crime_options = [crime["ofns_desc"] for crime in crime_types]

from ipywidgets import interact, widgets
from IPython.display import clear_output

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
        df = df.dropna(subset=['latitude', 'longitude'])
        df = df[(df['longitude'] != 0) & (df['latitude'] != 0)]
    
    return df

def create_crime_map(crime_type="RAPE", 
                    start_date_str="2024-02-16", 
                    end_date_str="2025-02-16", 
                    show_markers=True,
                    heat_radius=15,
                    heat_blur=10):
    """Create and display crime heatmap"""
    clear_output(wait=True)
    
    print(f"Fetching data for {crime_type} from {start_date_str} to {end_date_str}...")
    
    # Format dates for API

    start_date_api = f"{start_date_str}T00:00:00.000"
    end_date_api = f"{end_date_str}T00:00:00.000"
    
    # Fetch data
    df = fetch_crime_data(crime_type, start_date_api, end_date_api)
    
    if df.empty:
        print("No data found for the selected criteria.")
        return None
    
    print(f"Found {len(df)} incidents. Creating map...")
    
    # Create map
    nyc_coords = (40.7128, -74.0060)
    crime_map = folium.Map(location=nyc_coords, zoom_start=11)
    
    # Add heatmap
    heat_data = [[row['latitude'], row['longitude']] for _, row in df.iterrows()]
    HeatMap(heat_data, radius=heat_radius, blur=heat_blur, 
            gradient={'0.4': 'blue', '0.65': 'lime', '0.8': 'orange', '1': 'red'}).add_to(crime_map)
    
    # Add title
    title_html = f'''
        <h3 align="center" style="font-size:16px"><b>NYC {crime_type} Incidents Heatmap</b><br>
        {start_date_str} to {end_date_str}</h3>
    '''
    crime_map.get_root().html.add_child(folium.Element(title_html))
    
    # Add markers if requested
    if show_markers:
        marker_cluster = folium.plugins.MarkerCluster().add_to(crime_map)
        for idx, row in df.iterrows():
            try:
                # Create popup content with safe string conversion
                popup_content = f"""
                <b>Offense:</b> {str(row.get('ofns_desc', 'N/A'))}<br>
                <b>Date:</b> {str(row.get('cmplnt_fr_dt', 'N/A'))}<br>
                <b>Time:</b> {str(row.get('cmplnt_fr_tm', 'N/A'))}<br>
                <b>Location:</b> {str(row.get('loc_of_occur_desc', 'N/A'))}<br>
                <b>Premise:</b> {str(row.get('prem_typ_desc', 'N/A'))}<br>
                """
                
                # Add marker
                folium.Marker(
                    location=[float(row['latitude']), float(row['longitude'])],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(marker_cluster)
            except:
                continue
    
    return crime_map

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
interact(create_crime_map,
         crime_type=crime_dropdown,
         start_date_str=start_date_picker,
         end_date_str=end_date_picker,
         show_markers=show_markers_checkbox,
         heat_radius=radius_slider,
         heat_blur=blur_slider);