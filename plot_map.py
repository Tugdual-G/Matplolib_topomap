#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
from core.select_shape import select_shape_data
from core.select_raster import select_raster
import numpy as np
from matplotlib.colors import LightSource
import glob
from rasterio.plot import show

# Window, area of interest from center coordinates x0, y0
# projection lambert93
x0 = 412086
y0 = 6608982
margin = 5e3
left = x0 - margin
right = x0 + margin
bottom = y0 - margin
top = y0 + margin
bounds = (left, bottom, right, top)

txtmargin = margin * 0.8
txtleft = x0 - txtmargin
txtright = x0 + txtmargin
txtbottom = y0 - txtmargin
txttop = y0 + txtmargin
txt_bounds = (txtleft, txtbottom, txtright, txttop)

# stylesheet specific to osm data fclass
style0 = pd.read_csv("map_style.csv")
style = style0[(style0["use"] == True) & (style0["category"] != "places")].set_index(
    "fclass"
)
txt_style = style0[
    (style0["use"] == True) & (style0["category"] == "places")
].set_index("fclass")

# data directory and files path
dir_path = "/home/tugdual/Downloads/osm_pays_loire/"
land_path = "gis_osm_landuse_a_free_1.shp"
water_path = "gis_osm_water_a_free_1.shp"
road_path = "gis_osm_roads_free_1.shp"
places_path = "gis_osm_places_free_1.shp"

# extract data in area of interest
land_df = select_shape_data(bounds, dir_path + land_path)
water_df = select_shape_data(bounds, dir_path + water_path)
road_df = select_shape_data(bounds, dir_path + road_path)
places_df = select_shape_data(txt_bounds, dir_path + places_path)

# stitch into one dataframe
df = pd.concat([land_df, water_df, road_df, places_df])
df = df[df["fclass"].isin(style.index.tolist() + txt_style.index.tolist())]
df = df.to_crs("EPSG:2154")


# raster data
step = 1
dir_name = "/home/tugdual/Downloads/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D085_2021-09-15/BDALTIV2/1_DONNEES_LIVRAISON_2021-10-00008/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D085"
f_paths = glob.glob(dir_name + "/*.asc")
data, x, y = select_raster(bounds, f_paths, step=step)


# PLOT
print("generating figure")
fig, ax = plt.subplots(frameon=False)
for fclass in style.index.tolist():
    styledict = eval(style.loc[fclass]["style"])
    df[df["fclass"] == fclass].plot(ax=ax, **styledict)

for fclass in txt_style.index.tolist():
    styledict = eval(txt_style.loc[fclass]["style"])
    txt_df = df.loc[df["fclass"] == fclass]
    for name in txt_df["name"]:
        xt = txt_df[txt_df["name"] == name]["geometry"].centroid.x.iloc[0]
        yt = txt_df[txt_df["name"] == name]["geometry"].centroid.y.iloc[0]
        ax.text(
            xt,
            yt,
            s=name,
            horizontalalignment="center",
            verticalalignment="center",
            **styledict
        )

ls = LightSource(azdeg=315, altdeg=45)
dx = 25
grayscale = ls.hillshade(data[0], dx=dx, dy=dx)
ax.pcolormesh(x, y, grayscale, alpha=0.4, cmap="gray", shading="gouraud", zorder=20)
# ax.contour(x,y,data[0], colors="k", linewidths=0.5)

ax.set_xlim(left, right)
ax.set_ylim(bottom, top)
ax.set_axis_off()
ax.set_frame_on(False)
# plt.savefig("test.png", dpi=200, bbox_inches="tight", pad_inches=0)
plt.show()
