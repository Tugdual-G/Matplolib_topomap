#!/usr/bin/env python3
import geopandas as gpd
import pandas as pd
import pyproj


def select_shape_data(bounds, file_path, data_crs="EPSG:4326", bounds_crs="epsg:2154"):
    """Crop and merge data files"""
    left, bottom, right, top = bounds
    lamb93_osmproj = pyproj.Transformer.from_crs("epsg:2154", "EPSG:4326")

    # have to swap x and y :(
    bottom, left, top, right = lamb93_osmproj.transform_bounds(left, bottom, right, top)
    bbox = (left, bottom, right, top)

    return gpd.read_file(file_path, bbox=bbox)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

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

    land_df = select_shape_data(bounds, dir_path + land_path)
    land_df = land_df.to_crs("EPSG:2154")
    print(land_df.crs)
    forest_df = land_df[land_df["fclass"] == "forest"]
    print(forest_df.head)

    water_df = select_shape_data(bounds, dir_path + water_path)
    water_df = water_df.to_crs("EPSG:2154")
    print(water_df.head)
    lake_df = water_df[
        (water_df["fclass"] == "riverbank") | (water_df["fclass"] == "water")
    ]

    ax = forest_df.plot(facecolor="green")
    lake_df.plot(ax=ax, facecolor="blue")
    plt.savefig("fig.png")
    print("done")
    plt.show()
