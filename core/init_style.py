#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
from select_shape import select_shape_data
from select_raster import select_raster
import numpy as np
from matplotlib.colors import LightSource
import glob

map_data = {}

x0 = 412086
y0 = 6608982
margin = 5e3
left = x0 - margin
right = x0 + margin
bottom = y0 - margin
top = y0 + margin
bounds = (left, bottom, right, top)

dir_path = "/home/tugdual/Downloads/osm_pays_loire/"
land_path = "gis_osm_landuse_a_free_1.shp"
water_path = "gis_osm_water_a_free_1.shp"
road_path = "gis_osm_roads_free_1.shp"
places_path = "gis_osm_places_free_1.shp"

land_df = select_shape_data(bounds, dir_path + land_path)
styles = [
    {"category": "land_use", "fclass": x, "style": {"facecolor": "green"}, "use": False}
    for x in land_df["fclass"].unique()
]

water_df = select_shape_data(bounds, dir_path + water_path)
styles += [
    {"category": "water", "fclass": x, "style": {"facecolor": "lightblue"}, "use": True}
    for x in water_df["fclass"].unique()
]

road_df = select_shape_data(bounds, dir_path + road_path)
styles += [
    {
        "category": "roads",
        "fclass": x,
        "style": {"color": "black", "linewidth": 1},
        "use": False,
    }
    for x in road_df["fclass"].unique()
]

places_df = select_shape_data(bounds, dir_path + places_path)
styles += [
    {
        "category": "places",
        "fclass": x,
        "style": {"color": "black", "marker": "o"},
        "use": False,
    }
    for x in places_df["fclass"].unique()
]

theme = pd.DataFrame(styles)
theme = theme.set_index("fclass")

theme.loc["forest"]["style"]["facecolor"] = "forestgreen"
theme["use"].loc["forest"] = True

print(theme)

theme.to_csv("map_style.csv")
