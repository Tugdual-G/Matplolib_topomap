#!/usr/bin/env python3
import matplotlib.pyplot as plt
from select_shape import select_shape_data
from select_raster import select_raster
import numpy as np
from matplotlib.colors import LightSource
import glob
from rasterio.plot import show

def plot_fname(dataframe, fname, theme_dict):
    df = dataframe[dataframe["fclass"].isin(fname)]
    df.plot(ax=ax, color=theme_dict, linewidth=1)

styles = { "category" : {"fname":["fname1","fname2"], "colour":"lightblue"}

}

x0 = 412086
y0 = 6608982
margin = 5e3
left = x0-margin
right = x0 + margin
bottom = y0 - margin
top = y0 + margin
bounds = (left, bottom, right, top)

dir_path = '/home/tugdual/Downloads/osm_pays_loire/'
land_path = 'gis_osm_landuse_a_free_1.shp'
water_path = "gis_osm_water_a_free_1.shp"
road_path = "gis_osm_roads_free_1.shp"

land_df = select_shape_data(bounds, dir_path+land_path)
land_df = land_df.to_crs("EPSG:2154")
forest_df = land_df[land_df["fclass"]=="forest"]
grass_df = land_df[(land_df["fclass"]=="grass")|(land_df["fclass"]=="meadow")]
crop_df = land_df[(land_df["fclass"]=="farmland")]

water_df = select_shape_data(bounds, dir_path+water_path)
water_df = water_df.to_crs("EPSG:2154")
lake_df = water_df[water_df["fclass"].isin(["riverbank","water"])]

road_df = select_shape_data(bounds, dir_path+road_path)
road_df = road_df.to_crs("EPSG:2154")
major_roads = road_df[road_df["fclass"]=="primary"]
sec_roads = road_df[road_df["fclass"]=="secondary"]
tert_roads = road_df[road_df["fclass"]=="tertiary"]



fig, ax = plt.subplots()
forest_df.plot(ax=ax, facecolor="forestgreen", label="forest")
grass_df.plot(ax=ax, facecolor="lawngreen", label="grass, meadow")
crop_df.plot(ax=ax, facecolor="yellow", label="farmland")
major_roads.plot(ax=ax, color="dimgrey", linewidth=3)
sec_roads.plot(ax=ax, color="dimgrey", linewidth=2)
tert_roads.plot(ax=ax, color="dimgrey", linewidth=1)

# raster data
step = 1

dir_name = "/home/tugdual/Downloads/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D085_2021-09-15/BDALTIV2/1_DONNEES_LIVRAISON_2021-10-00008/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D085"
f_paths = glob.glob(dir_name + "/*.asc")

data, x, y = select_raster(bounds, f_paths, step=step)

ls = LightSource(azdeg=315, altdeg=45)
dx = 25*step
grayscale = ls.hillshade(data[0], dx=dx, dy=dx)
ax.pcolormesh(x,y, grayscale, alpha=0.6, cmap="gray")

lake_df.plot(ax=ax, facecolor="lightblue")

ax.set_xlim(left, right)
ax.set_ylim(bottom, top)
plt.show()
