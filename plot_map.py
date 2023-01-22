#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
import glob
from pyproj import transform
from core.Carte import Carte
import rasterio

# Window, area of interest from center coordinates x0, y0
# projection lambert93
positions = {"mervent": (411684, 6609470), "lebeugnon": (431768, 6615611)}
x0, y0 = positions["lebeugnon"]
x0 += 3e3
step = 1
margin = 5 * 1e3
left = x0 - margin
right = x0 + margin
bottom = y0 - margin
top = y0 + margin
bounds = (left, bottom, right, top)

# Creatin the map object
carte = Carte((x0, y0), margin)

# stylesheet specific to osm data fclass
style_path = "styles"
carte.set_style(style_path + "/default_style.json")
carte.set_label_style(style_path + "/default_labelstyle.json")


# data directory and files path
dir_path1 = "data/osm_pays_loire"
land_path = "/gis_osm_landuse_a_free_1.shp"
water_path = "/gis_osm_water_a_free_1.shp"
road_path = "/gis_osm_roads_free_1.shp"
places_path = "/gis_osm_places_free_1.shp"
filesnames = [land_path, water_path, road_path, places_path]
shapes_paths = [(dir_path1 + name) for name in filesnames]
dir_path2 = "data/osm_poitou-charente"
shapes_paths += [(dir_path2 + name) for name in filesnames]

# extract data in area of interest
carte.set_shape_data(shapes_paths)


# raster data
dir_name1 = "data/raster/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D085_2021-09-15/BDALTIV2/1_DONNEES_LIVRAISON_2021-10-00008/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D085"
dir_name2 = "data/raster/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D079_2022-10-05/BDALTIV2/1_DONNEES_LIVRAISON_2022-12-00016/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D079"
f_paths = glob.glob(dir_name1 + "/*.asc")
f_paths += glob.glob(dir_name2 + "/*.asc")

carte.set_raster_data(f_paths, step)


# PLOT
print("generating figure")
fig, ax = plt.subplots(figsize=[8, 8])

print("ploting shapes")
carte.plot_shapes(ax)

print("adding places labels")
carte.plot_txt(ax)

print("adding hill shade")
x, y = carte.X, carte.Y

carte.plot_hillshaded_raster(ax, shadeargs={"vmin": 0, "vmax": 280})

print("adding contour lines")
# carte.plot_contour(ax)


def onclick(event):
    if event.xdata != None:
        print(f"x0, y0 = {round(event.xdata)}, {round(event.ydata)} (m)")


fig.canvas.mpl_connect("button_press_event", onclick)

carte.save_geotiff("test1.tiff", ax, fig)

plt.show()
