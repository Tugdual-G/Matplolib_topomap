#!/usr/bin/env python3
import rasterio
from rasterio.merge import merge
from pathlib import Path, PurePosixPath
import numpy as np


def select_raster(bounds, files_paths, step=1, epsg="EPSG:2154"):
    """Merge and crop data"""
    datasets = []

    for f in files_paths:
        p = PurePosixPath(f)
        p = p.with_suffix(".tiff")
        datasets += [rasterio.open(p.as_posix(), crs=epsg)]

    data, out_transform = merge(datasets, bounds=bounds)

    # Creating a grid corresponding to raster data
    x, y = np.meshgrid(
        np.arange(data[0].shape[1] // step) * step,
        np.arange(data[0].shape[0] // step) * step,
    )
    x, y = rasterio.transform.xy(out_transform, y, x)
    x, y = np.array(x), np.array(y)
    return data[..., ::step, ::step], x, y


if __name__ == "__main__":
    from matplotlib.colors import LightSource
    import glob
    from rasterio.plot import show
    import matplotlib.pyplot as plt

    margin = 5e3
    x0 = 412086
    y0 = 6608982
    left = x0 - margin
    right = x0 + margin
    bottom = y0 - margin
    top = y0 + margin
    bounds = (left, bottom, right, top)
    step = 1

    dir_name = "/home/tugdual/Downloads/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D085_2021-09-15/BDALTIV2/1_DONNEES_LIVRAISON_2021-10-00008/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D085"
    f_paths = glob.glob(dir_name + "/*.asc")

    data, x, y = select_raster(bounds, f_paths, step=step)

    fig, ax = plt.subplots()
    ls = LightSource(azdeg=315, altdeg=45)
    dx = 25 * step
    grayscale = ls.hillshade(data[0], dx=dx, dy=dx)
    ax.pcolormesh(x, y, grayscale, vmax=1, vmin=0, cmap="gray")
    plt.show()
