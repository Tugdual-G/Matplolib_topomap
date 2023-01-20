#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LightSource
import glob
from rasterio.plot import show
from core.Carte import Carte

# Window, area of interest from center coordinates x0, y0
# projection lambert93
positions = {"mervent": (411684, 6609470), "lebeugnon": (431768, 6615611)}
x0, y0 = positions["mervent"]
step = 1
margin = 4e3
left = x0 - margin
right = x0 + margin
bottom = y0 - margin
top = y0 + margin
bounds = (left, bottom, right, top)

# Creatin the map object
carte = Carte((x0, y0), margin)

# stylesheet specific to osm data fclass
style_path = "map_style.csv"
carte.set_style(style_path)


# data directory and files path
dir_path1 = "data/shapes/osm_pays_loire"
land_path = "/gis_osm_landuse_a_free_1.shp"
water_path = "/gis_osm_water_a_free_1.shp"
road_path = "/gis_osm_roads_free_1.shp"
places_path = "/gis_osm_places_free_1.shp"
filesnames = [land_path, water_path, road_path, places_path]
shapes_paths = [(dir_path1 + name) for name in filesnames]
dir_path2 = "data/shapes/osm_poitou-charente"
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
fig, ax = plt.subplots(frameon=False)

carte.plot_shapes(ax)
carte.plot_txt(ax)

x, y = carte.X, carte.Y
elev = carte.raster_data[0]

ls = LightSource(azdeg=100, altdeg=45)
dx = 25 * step
grayscale = ls.hillshade(elev, dx=dx, dy=dx)
black = np.zeros_like(grayscale)
ax.pcolormesh(
    x, y, black, alpha=0.3 * (1 - grayscale), cmap="gray", shading="gouraud", zorder=20
)

interlevels = np.arange(0, 300, 10)
ax.contour(x, y, elev, colors="sienna", levels=interlevels, linewidths=0.5, zorder=18)
levels = np.arange(0, 300, 50)
CS = ax.contour(x, y, elev, colors="sienna", levels=levels, linewidths=0.7, zorder=19)
# plt.clabel(CS, fontsize=7, inline=False, inline_spacing=5)


def onclick(event):
    print(f"x0, y0 = {round(event.xdata)}, {round(event.ydata)}")


cid = fig.canvas.mpl_connect("button_press_event", onclick)

ax.set_xlim(left, right)
ax.set_ylim(bottom, top)
ax.set_axis_off()
ax.set_frame_on(False)
plt.savefig("test.png", dpi=200, bbox_inches="tight", pad_inches=0)
plt.show()
