import streamlit as st
import json
import pandas as pd
from pandas import json_normalize
import requests
# from tabulate import tabulate
from sklearn.cluster import KMeans
# import random
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

facilities_list_name = st.sidebar.multiselect(
    'What are the facilities you are expecting',
    ['Gym', 'Restaurents', 'cafe','market'],
    )






def fill_facilitites(search_query,List,latitude,longitude,index):
    radius = '1000'
    url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{},{};r={}&q={}&apiKey=uJHMEjeagmFGldXp661-pDMf4R-PxvWIu7I68UjYC5Q'.format(
        latitude, longitude, radius, search_query)
    results = requests.get(url).json()
    venues = json_normalize(results['items'])
    List[index].append(venues['title'].count())




def find_facilities(df_final,d2):
    latitudes = list(d2['position.lat'])
    longitudes = list(d2['position.lng'])
    List = [[] for _ in range(len(facilities_list_name))]
    for lat, lng in zip(latitudes, longitudes):
        latitude = lat
        longitude = lng


        for i in range(0,len(facilities_list_name)):
            fill_facilitites(facilities_list_name[i], List, latitude, longitude, i)


    for i in range(0,len(List)):
        # st.sidebar.write(facilities_list_name[i] , " | ", len(List[i]) )
        df_final[facilities_list_name[i]]=List[i]


def make_cluster(df_final):
    # Run K-means clustering on dataframe
    kclusters = 3

    kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(df_final)
    df_final['Cluster'] = kmeans.labels_
    df_final['Cluster'] = df_final['Cluster'].apply(str)


def add_to_map(df_final,d2):
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

def draw_graph(location_name,location_latitude,location_longitude,radius):
    # # url = 'https://discover.search.hereapi.com/v1/discover?in=circle:28.6100216,77.0379647;r=100000&q=appartment&apiKey=kW5ZzpawjBDJ0waMxzGx_a3cFfR9bgWK-5ejXI9xt1s'
    #

    url = 'https://discover.search.hereapi.com/v1/discover?in=circle:{0},{1};r={2}&q=appartment&apiKey=uJHMEjeagmFGldXp661-pDMf4R-PxvWIu7I68UjYC5Q'.format(
        location_latitude, location_longitude, radius)
    data = requests.get(url).json()
    d = json_normalize(data['items'])
    if d.shape[0] ==0:
        return -1,-1,0

    d2 = d[['title','position.lat', 'position.lng']]


    # Counting no. of cafes, department stores and gyms near apartments around IIT Bombay
    df_final = d2[['position.lat', 'position.lng']]

    find_facilities(df_final,d2)
    # st.sidebar.write('after find_facilities')

    make_cluster(df_final)

    # create map object and plot the points

    map_obj = add_to_map(df_final,d2)
    name_df=pd.DataFrame()
    name_df['name']=d2['title']
    sz=len(df_final.columns)

    for i in range(2,sz):
        name_df[df_final.columns[i]]=df_final[df_final.columns[i]]



    return map_obj, name_df,1


if st.sidebar.button('saw result'):
    map_obj, name_df,val =draw_graph(location_name,location_latitude,location_longitude,radius)
    if val == 0:
        st.write('not available')
    else:
        folium_static(map_obj, width=700)
        # st.write(df_final)
        st.write(name_df)












