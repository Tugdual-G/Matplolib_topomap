#!/usr/bin/env python3
import rasterio
from rasterio.merge import merge
import numpy as np
import matplotlib.pyplot as plt

files_paths = ["exp0.tiff", "exp1.tiff", "exp2.tiff"]

datasets = []

for f in files_paths:
    datasets += [rasterio.open(f)]

data, out_transform = merge(datasets, nodata=0)

rgba = np.moveaxis(data, 0, -1)

plt.imshow(rgba)
plt.show()
