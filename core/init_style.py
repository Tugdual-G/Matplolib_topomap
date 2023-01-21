#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
from select_shape import select_shape_data
from select_raster import select_raster
import numpy as np
import json
import glob

map_data = {}

x0 = 412086
y0 = 6608982
margin = 100e3
left = x0 - margin
right = x0 + margin
bottom = y0 - margin
top = y0 + margin
bounds = (left, bottom, right, top)

dir_path = (
    "/home/tugdual/Documents/Programmation/topo_map/carte_topo/data/osm_pays_loire/"
)
layers = ["roads", "land", "water", "places"]

layers_files = {
    "roads": "gis_osm_roads_free_1.shp",
    "land": "gis_osm_landuse_a_free_1.shp",
    "water": "gis_osm_water_a_free_1.shp",
    "places": "gis_osm_places_free_1.shp",
}

default_styles = {
    "roads": {
        "color": "w",
        "linewidth": 1,
        "path_effects": "[pe.withStroke(linewidth=2, foreground='k')]",
        "zorder": 110,
    },
    "land": {"facecolor": "green", "zorder": 10},
    "water": {"facecolor": "lightblue", "zorder": 100},
    "places": {"facecolor": "grey", "zorder": 10},
}


txtprop = {
    "horizontalalignment": "center",
    "verticalalignment": "center",
    "clip_on": True,
    "path_effects": '[pe.withStroke(linewidth=3, alpha=0.7, foreground="white")]',
}

default_labelstyles = {
    "roads": {"color": "black", "fontsize": 8, "zorder": 200, **txtprop},
    "land": {"color": "black", "fontsize": 8, "zorder": 200, **txtprop},
    "water": {"color": "blue", "fontsize": 8, "zorder": 200, **txtprop},
    "places": {"color": "black", "fontsize": 8, "zorder": 201, **txtprop},
}

styles = []
labelstyles = []

for i, layer in enumerate(layers):
    df = select_shape_data(bounds, [dir_path + layers_files[layer]])
    clist = df["code"].unique()
    styles += [{"type": layer, "obj": []}]
    labelstyles += [{"type": layer, "obj": []}]
    for code in clist:
        styles[i]["obj"] += [
            {
                "fclass": (df[df["code"] == code]["fclass"]).iloc[0],
                "code": int(code),
                "use": False,
                "style": (default_styles[layer]),
            }
        ]

        labelstyles[i]["obj"] += [
            {
                "fclass": (df[df["code"] == code]["fclass"]).iloc[0],
                "code": int(code),
                "use": False,
                "style": (default_labelstyles[layer]),
            }
        ]

print(json.dumps(styles, indent=4))
print("writing to file")
with open("default_style.json", "w") as outfile:
    json.dump(styles, outfile, indent=4, sort_keys=False)

print(json.dumps(labelstyles, indent=4))
print("writing to file")
with open("default_labelstyle.json", "w") as outfile:
    json.dump(labelstyles, outfile, indent=4, sort_keys=False)
