#!/usr/bin/env python3
from csv import Error
from core.select_raster import select_raster
from core.select_shape import select_shape_data
import pandas as pd
import numpy as np
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import json


class Carte:
    def __init__(self, center, margin):

        self.x0, self.y0 = center
        self.margin = margin
        left = self.x0 - margin
        right = self.x0 + margin
        bottom = self.y0 - margin
        top = self.y0 + margin
        self.bounds = (left, bottom, right, top)
        self.label_style = pd.DataFrame()
        self.style = pd.DataFrame()
        self.codes = []
        self.lbl_codes = []

        self.crs = "epsg:2154"

    # stylesheet specific to osm data code
    def set_style(self, path):
        """Read a style sheet in .json format"""

        with open(path, "r") as infile:
            jstyles = json.load(infile)
            stl_df = pd.json_normalize(jstyles, "obj", ["type"], max_level=0)
        self.style = stl_df[stl_df["use"] == True].set_index("code")

    def set_label_style(self, path):
        """Read a style sheet in .json format"""
        with open(path, "r") as infile:
            jstyles = json.load(infile)
            lbl_stl_df = pd.json_normalize(jstyles, "obj", ["type"], max_level=0)
        self.label_style = lbl_stl_df[lbl_stl_df["use"] == True].set_index("code")

    def set_raster_data(self, paths, step=1):
        self.raster_data, self.X, self.Y = select_raster(self.bounds, paths, step=step)

    def set_shape_data(self, paths):
        if self.label_style.empty and self.style.empty:
            raise ValueError("Set the style of the map before importing data")

        # extract data in area of interest
        df = select_shape_data(self.bounds, paths).set_index("code")

        # stl_codes = np.unique(
        # np.array(self.style.index.tolist() + self.label_style.index.tolist())
        # )

        stl_idx = np.array(self.style.index.tolist())
        stl_idx_lbl = np.array(self.label_style.index.tolist())
        self.shape_df = df[df.index.isin(np.append(stl_idx, stl_idx_lbl))]

        stl_idx = self.shape_df[self.shape_df.index.isin(stl_idx)].index.unique()
        stl_idx_lbl = self.shape_df[
            self.shape_df.index.isin(stl_idx_lbl)
        ].index.unique()
        self.style = self.style[self.style.index.isin(stl_idx)]
        self.lablel_style = self.style[self.style.index.isin(stl_idx_lbl)]

        self.shape_df = self.shape_df.to_crs(self.crs)

    def plot_shapes(self, ax):
        for code in self.style.index.unique():
            styledict = self.style.loc[code]["style"]
            if "path_effects" in styledict:
                styledict["path_effects"] = eval(styledict["path_effects"])

            # code have duplicates so I can't use .loc[]
            self.shape_df[self.shape_df.index == code].plot(ax=ax, **styledict)

    def plot_txt(self, ax):

        for code in self.label_style.index.tolist():

            styledict = self.label_style.loc[code]["style"]
            if "path_effects" in styledict:
                styledict["path_effects"] = eval(styledict["path_effects"])

            txt_df = self.shape_df[self.shape_df["name"].notna()]
            txt_df = txt_df[txt_df.index == code]
            for osm_id in txt_df["osm_id"]:
                name = txt_df[txt_df["osm_id"] == osm_id]["name"].iloc[0]
                xt = txt_df[txt_df["osm_id"] == osm_id]["geometry"].centroid.x.iloc[0]
                yt = txt_df[txt_df["osm_id"] == osm_id]["geometry"].centroid.y.iloc[0]
                ax.text(
                    xt,
                    yt,
                    s=name,
                    **styledict,
                )
