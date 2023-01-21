#!/usr/bin/env python3
from core.select_raster import select_raster
from core.select_shape import select_shape_data
import pandas as pd
import numpy as np
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt


class Carte:
    def __init__(self, center, margin):

        self.x0, self.y0 = center
        self.margin = margin
        left = self.x0 - margin
        right = self.x0 + margin
        bottom = self.y0 - margin
        top = self.y0 + margin
        self.bounds = (left, bottom, right, top)

        self.crs = "epsg:2154"

    # stylesheet specific to osm data fclass
    def set_style(self, path):
        style = pd.read_csv(path)
        # TODO modify style sheet to add a txt column
        self.style = style[
            (style["use"] == True) & (style["category"] != "places")
        ].set_index("fclass")
        self.txt_style = style[
            (style["use"] == True) & (style["category"] == "places")
        ].set_index("fclass")

    def set_raster_data(self, paths, step=1):
        self.raster_data, self.X, self.Y = select_raster(self.bounds, paths, step=step)

    def set_shape_data(self, paths):
        # extract data in area of interest
        df = select_shape_data(self.bounds, paths)

        # stitch into one dataframe
        self.shape_df = df[
            df["fclass"].isin(self.style.index.tolist() + self.txt_style.index.tolist())
        ]
        self.shape_df = self.shape_df.to_crs(self.crs)

    def plot_shapes(self, ax):

        for fclass in self.style.index.tolist():
            styledict = eval(self.style.loc[fclass]["style"])
            self.shape_df[self.shape_df["fclass"] == fclass].plot(ax=ax, **styledict)

    def plot_txt(self, ax):

        for fclass in self.txt_style.index.tolist():
            styledict = eval(self.txt_style.loc[fclass]["style"])
            txt_df = self.shape_df.loc[self.shape_df["fclass"] == fclass]
            for name in txt_df["name"]:
                xt = txt_df[txt_df["name"] == name]["geometry"].centroid.x.iloc[0]
                yt = txt_df[txt_df["name"] == name]["geometry"].centroid.y.iloc[0]
                ax.text(
                    xt,
                    yt,
                    s=name,
                    horizontalalignment="center",
                    verticalalignment="center",
                    clip_on=True,
                    path_effects=[
                        pe.withStroke(linewidth=3, alpha=0.7, foreground="white")
                    ],
                    **styledict,
                )
