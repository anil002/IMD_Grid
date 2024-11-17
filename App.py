import streamlit as st
import folium
from folium import plugins
import geopandas as gpd
import xarray as xr
import pandas as pd

# Load India state boundaries
india_states = gpd.read_file("India_boundry/India-State-and-Country-Shapefile-Updated-Jan-2020-master/India_State_Boundary.shp")  # Update path if necessary

# Load rainfall data from NetCDF file
ds = xr.open_dataset('1901-2022.nc')

# Streamlit UI elements
st.title("India Weekly Rainfall Map")
year = st.slider("Select Year", 1901, 2022, 2020)
rainfall_threshold = st.slider("Rainfall Threshold (mm)", 0, 200, 20)
week = st.slider("Select Week", 1, 52, 1)

# Filter data for the selected year
ds_year = ds.sel(TIME=slice(f'{year}-01-01', f'{year}-12-31'))

# Calculate weekly rainfall totals
weekly_precip = ds_year['RAINFALL'].resample(TIME='1W').sum()

# Filter for weeks with rainfall > threshold
filtered_weeks = weekly_precip.where(weekly_precip > rainfall_threshold, drop=True)

# Get data for the selected week
week_data = filtered_weeks.isel(TIME=week - 1).to_dataframe().reset_index()

# Remove rows with NaN values
week_data = week_data.dropna(subset=['RAINFALL'])

# Initialize folium map centered on India
m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

# Add India boundaries
folium.GeoJson(india_states, name="India States").add_to(m)

# Add heatmap layer for rainfall data
heat_data = [[row['LATITUDE'], row['LONGITUDE'], row['RAINFALL']] for idx, row in week_data.iterrows()]
plugins.HeatMap(heat_data).add_to(m)

# Custom Legend for Rainfall
legend_html = """
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 150px; height: 120px; 
     border:2px solid grey; z-index:9999; font-size:14px;
     background-color: white; opacity: 0.8;
     ">
     <strong>Rainfall Legend (mm)</strong><br>
     <i style="background: blue; color: blue; font-size:15px;">&nbsp;&nbsp;&nbsp;&nbsp;</i>&nbsp;0-20<br>
     <i style="background: green; color: green; font-size:15px;">&nbsp;&nbsp;&nbsp;&nbsp;</i>&nbsp;20-50<br>
     <i style="background: orange; color: orange; font-size:15px;">&nbsp;&nbsp;&nbsp;&nbsp;</i>&nbsp;50-100<br>
     <i style="background: red; color: red; font-size:15px;">&nbsp;&nbsp;&nbsp;&nbsp;</i>&nbsp;>100<br>
     </div>
     """
m.get_root().html.add_child(folium.Element(legend_html))

# Display map in Streamlit
st.write("Weekly Rainfall Map for Selected Filters")
st.components.v1.html(m._repr_html_(), width=700, height=500)
