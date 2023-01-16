#!/usr/bin/env python3
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import glob
import rasterio
from rasterio.plot import show
import os
from pathlib import Path, PurePosixPath
import numpy as np
from matplotlib.colors import LightSource
from rasterio.merge import merge
step = 10
x0 = 412086
y0 = 6608982
ls = LightSource(azdeg=315, altdeg=45)

dir_name = "/home/tugdual/Downloads/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D085_2021-09-15/BDALTIV2/1_DONNEES_LIVRAISON_2021-10-00008/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D085"
f_paths = glob.glob(dir_name + "/*.asc")
cmap = plt.cm.gist_earth
datasets = []

for f in f_paths:
    p = PurePosixPath(f)
    p = p.with_suffix(".tiff")
    print(p.name)
    datasets += [rasterio.open(p.as_posix(), crs="EPSG:2154")]

print(len(datasets))
dest, out_transform = merge(datasets)
print(dest.shape)
window = rasterio.windows.from_bounds(x0-5e3,y0-5e3,x0+5e3,y0+5e3, transform=out_transform)
print(window.toslices())
subset = dest[0][window.toslices()]
zmax, zmin = np.amax(subset), np.amin(subset)
dx = 25
rgb = ls.shade(subset, cmap=cmap, blend_mode="hsv", dx=dx, dy=dx)
plt.imshow(rgb)
plt.show()
