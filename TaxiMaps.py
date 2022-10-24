global System, DataTable, AMO, ADOMD

import pandas as pd
import ssas_api as ssas
import seaborn as sns
import streamlit as st
import altair as alt
import pydeck as pdk

import matplotlib.pyplot as plt
import numpy as np

sns.set_style("whitegrid")
blue, = sns.color_palette("muted", 1)

import sys
import os
sys.path.insert(0,os.path.abspath(' ./' ))
import clr
clr.AddReference('System.Data' )
r = clr.AddReference(r"C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.AnalysisServices.Tabular\v4.0_15.0.0.0__89845dcd8080cc91\Microsoft.AnalysisServices.Tabular.dll")
r = clr.AddReference(r"C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.AnalysisServices.AdomdClient\v4.0_15.0.0.0__89845dcd8080cc91\Microsoft.AnalysisServices.AdomdClient.dll")
from System import Data
from System import Converter
from System.Data import DataTable
import Microsoft.AnalysisServices.Tabular as TOM
import Microsoft.AnalysisServices.AdomdClient as ADOMD


server = 'powerbi://api.powerbi.com/v1.0/myorg/ModelosMayores1GB'

username = 'a.garcia@bdigitalsolutions.com'

password = '..Paris@Diagonal550'

conn = ssas.set_conn_string(
        server=server,
        db_name='ModeloUber',
        username=username,
        password=password
        )

st.set_page_config(layout="wide", page_title="NYC Ridesharing Demo", page_icon=":taxi:")

dax_UberData = '''
EVALUATE
    TOPN(100000,
    'uber-raw-data-sep14')
'''

@st.experimental_singleton
def load_data():
    df_UberData = (ssas.get_DAX(
                connection_string = conn,
                dax_string=dax_UberData)
            )
    data = pd.DataFrame(
        df_UberData,
        columns=['uber-raw-data-sep14[Lat]', 'uber-raw-data-sep14[Lon]', 'uber-raw-data-sep14[Date/Time]'],
        )

    data.rename(columns = {'uber-raw-data-sep14[Lat]':'lat', 'uber-raw-data-sep14[Lon]':'lon', 'uber-raw-data-sep14[Date/Time]':'date/time'}, inplace = True)

    data['date/time'] = pd.to_datetime(data['date/time'])

    return data

def map(data, lat, lon, zoom):
    st.write(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={
                "latitude": lat,
                "longitude": lon,
                "zoom": zoom,
                "pitch": 50,
            },
            layers=[
                pdk.Layer(
                    "HexagonLayer",
                    data=data,
                    get_position=["lon", "lat"],
                    radius=100,
                    elevation_scale=4,
                    elevation_range=[0, 1000],
                    pickable=True,
                    extruded=True,
                ),
            ],
        )
    )


@st.experimental_memo
def filterdata(df, hour_selected):
    return df[df["date/time"].dt.hour == hour_selected]


# CALCULATE MIDPOINT FOR GIVEN SET OF DATA
@st.experimental_memo
def mpoint(lat, lon):
    return (np.average(lat), np.average(lon))


@st.experimental_memo
def histdata(df, hr):
    filtered = data[
        (df["date/time"].dt.hour >= hr) & (df["date/time"].dt.hour < (hr + 1))
    ]

    hist = np.histogram(filtered["date/time"].dt.minute, bins=60, range=(0, 60))[0]

    return pd.DataFrame({"minute": range(60), "pickups": hist})

data = load_data()

row1_1, row1_2 = st.columns((2, 3))
if not st.session_state.get("url_synced", False):
    try:
        pickup_hour = int(st.experimental_get_query_params()["pickup_hour"][0])
        st.session_state["pickup_hour"] = pickup_hour
        st.session_state["url_synced"] = True
    except KeyError:
        pass

# IF THE SLIDER CHANGES, UPDATE THE QUERY PARAM
def update_query_params():
    hour_selected = st.session_state["pickup_hour"]
    st.experimental_set_query_params(pickup_hour=hour_selected)


with row1_1:
    st.title("NYC Uber Ridesharing Data")
    hour_selected = st.slider(
        "Select hour of pickup", 0, 23, key="pickup_hour", on_change=update_query_params
    )


with row1_2:
    st.write(
        """
    ##
    Examining how Uber pickups vary over time in New York City's and at its major regional airports.
    By sliding the slider on the left you can view different slices of time and explore different transportation trends.
    """
    )

# LAYING OUT THE MIDDLE SECTION OF THE APP WITH THE MAPS
row2_1, row2_2, row2_3, row2_4 = st.columns((2, 1, 1, 1))

# SETTING THE ZOOM LOCATIONS FOR THE AIRPORTS
la_guardia = [40.7900, -73.8700]
jfk = [40.6650, -73.7821]
newark = [40.7090, -74.1805]
zoom_level = 12
midpoint = mpoint(data["lat"], data["lon"])

with row2_1:
    st.write(
        f"""**All New York City from {hour_selected}:00 and {(hour_selected + 1) % 24}:00**"""
    )
    map(filterdata(data, hour_selected), midpoint[0], midpoint[1], 11)

with row2_2:
    st.write("**La Guardia Airport**")
    map(filterdata(data, hour_selected), la_guardia[0], la_guardia[1], zoom_level)

with row2_3:
    st.write("**JFK Airport**")
    map(filterdata(data, hour_selected), jfk[0], jfk[1], zoom_level)

with row2_4:
    st.write("**Newark Airport**")
    map(filterdata(data, hour_selected), newark[0], newark[1], zoom_level)
