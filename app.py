import streamlit as st
import json
import pandas as pd
from pandas import json_normalize
import requests
from tabulate import tabulate
from sklearn.cluster import KMeans
import random
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium,folium_static
import warnings
warnings.filterwarnings('ignore')
import os
os.environ.keys()

# st.write("hello world")

location_name = st.sidebar.selectbox(
    "Location",
    ("Nsut", "IIT Bombay")
)



location_latitude=st.sidebar.text_input(
    label="Enter a latitude :",
    value="28.6100216",
    placeholder="like : 28.6100216",
)
location_longitude=st.sidebar.text_input(
    label="Enter a longitude :",
    value="77.0379647",
    placeholder="like : 77.0379647",
)

radius=st.sidebar.number_input(
    label="Enter an radius (in meters) : ",
    value=100000,
    min_value=1,
    step=1000,
)



#
# latitude=0.3
# longitude=0.5
# if location_name=='Nsut':
#     latitude=28.6100216
#     longitude=77.0379647
# else:
#     latitude = 0.8989
#     longitude = 779647

# st.sidebar.write(latitude," ",longitude," ",radius);
# st.write(type(latitude))


#
#

def draw_graph(location_name,location_latitude,location_longitude,radius):
    # # url = 'https://discover.search.hereapi.com/v1/discover?in=circle:28.6100216,77.0379647;r=100000&q=appartment&apiKey=kW5ZzpawjBDJ0waMxzGx_a3cFfR9bgWK-5ejXI9xt1s'
    #
    url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{0},{1};r={2}&q=appartment&apiKey=uJHMEjeagmFGldXp661-pDMf4R-PxvWIu7I68UjYC5Q'.format(
        location_latitude, location_longitude, radius)
    data = requests.get(url).json()
    d = json_normalize(data['items'])
    # st.write(d)
    # Cleaning API data
    d2 = d[['title', 'address.label', 'distance', 'access', 'position.lat', 'position.lng', 'address.postalCode',
            'contacts', 'id']]
    # d2.to_csv('api-data/cleaned_apartment.csv')
    # st.write(d2)

    # Counting no. of cafes, department stores and gyms near apartments around IIT Bombay
    df_final = d2[['position.lat', 'position.lng']]

    def find_facilities(df_final):
        CafeList = []
        ResList = []
        GymList = []
        latitudes = list(d2['position.lat'])
        longitudes = list(d2['position.lng'])
        for lat, lng in zip(latitudes, longitudes):
            radius = '1000'  # Set the radius to 1000 metres
            latitude = lat
            longitude = lng

            search_query = 'cafe'  # Search for any cafes
            url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{},{};r={}&q={}&apiKey=uJHMEjeagmFGldXp661-pDMf4R-PxvWIu7I68UjYC5Q'.format(
                latitude, longitude, radius, search_query)
            results = requests.get(url).json()
            venues = json_normalize(results['items'])
            CafeList.append(venues['title'].count())

            search_query = 'gym'  # Search for any gyms
            url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{},{};r={}&q={}&apiKey=uJHMEjeagmFGldXp661-pDMf4R-PxvWIu7I68UjYC5Q'.format(
                latitude, longitude, radius, search_query)
            results = requests.get(url).json()
            venues = json_normalize(results['items'])
            GymList.append(venues['title'].count())

            search_query = 'restaurents'  # search for supermarkets
            url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{},{};r={}&q={}&apiKey=uJHMEjeagmFGldXp661-pDMf4R-PxvWIu7I68UjYC5Q'.format(
                latitude, longitude, radius, search_query)
            results = requests.get(url).json()
            venues = json_normalize(results['items'])
            ResList.append(venues['title'].count())

        df_final['Cafes'] = CafeList
        df_final['Restaurents'] = ResList
        df_final['Gyms'] = GymList

        # df_final

    find_facilities(df_final)

    # st.write(df_final)

    # st.sidebar.write(location_latitude, " ", location_longitude, " ", radius);

    def make_cluster(df_final):
        # Run K-means clustering on dataframe
        kclusters = 3

        kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(df_final)
        df_final['Cluster'] = kmeans.labels_
        df_final['Cluster'] = df_final['Cluster'].apply(str)
        # df_final

    make_cluster(df_final)

    # st.write(df_final)

    def add_to_map(df_final):
        # Plotting clustered locations on map using Folium

        # define coordinates of the college
        map_bom = folium.Map(location=[location_latitude, location_longitude], zoom_start=12)

        # instantiate a feature group for the incidents in the dataframe
        locations = folium.map.FeatureGroup()

        # set color scheme for the clusters
        def color_producer(cluster):
            if cluster == '0':
                return 'green'
            elif cluster == '1':
                return 'orange'
            else:
                return 'red'

        latitudes = list(df_final['position.lat'])
        longitudes = list(df_final['position.lng'])
        labels = list(df_final['Cluster'])
        names = list(d2['title'])
        for lat, lng, label, names in zip(latitudes, longitudes, labels, names):
            folium.CircleMarker(
                [lat, lng],
                fill=True,
                fill_opacity=1,
                popup=folium.Popup(names, max_width=300),
                radius=5,
                color=color_producer(label)
            ).add_to(map_bom)

        # add locations to map
        map_bom.add_child(locations)
        folium.Marker([location_latitude, location_longitude], popup=location_name).add_to(map_bom)
        return map_bom

    map_obj = add_to_map(df_final)

    # st_folium(map_obj)
    return map_obj


if st.sidebar.button('saw result'):
    map_obj=draw_graph(location_name,location_latitude,location_longitude,radius)

    folium_static(map_obj, width=700)










