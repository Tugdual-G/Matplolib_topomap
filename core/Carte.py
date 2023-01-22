#!/usr/bin/env python3
from csv import Error
from core.select_raster import select_raster
from core.select_shape import select_shape_data
import pandas as pd
import numpy as np
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from matplotlib.transforms import Bbox
import json
import rasterio
import warnings


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
        self.max_elev = 8 * 1e3
        self.min_elev = 0

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
        self.step = step
        self.max_elev = np.amax(self.raster_data[0])
        self.min_elev = np.amin(self.raster_data[0])

        self.extent = (self.X[0, 0], self.X[0, -1], self.Y[-1, 0], self.Y[0, 0])

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

    def plot_hillshade(self, ax, **kwargs):

        x, y = self.X, self.Y
        elev = self.raster_data
        ls = LightSource(azdeg=270, altdeg=45)

        dx = (x[0, 1] - [0, 0]) * self.step
        grayscale = ls.hillshade(elev[0], dx=dx, dy=dx, vert_exag=5)
        black = np.zeros_like(grayscale)
        extent = (x[0, 0], x[0, -1], y[-1, 0], y[0, 0])

        imoptions = {
            "alpha": (0.4 * (1 - grayscale)),
            "cmap": "gray",
            "interpolation": "bicubic",
            "extent": extent,
            "zorder": 20,
        }

        imoptions.update(kwargs)

        ax.imshow(
            black,
            **imoptions,
        )

    def plot_hillshaded_raster(self, ax, shadeargs={}, **kwargs):
        x, y = self.X, self.Y
        elev = self.raster_data
        ls = LightSource(azdeg=270, altdeg=45)

        dx = (x[0, 1] - x[0, 0]) * self.step
        extent = (x[0, 0], x[0, -1], y[-1, 0], y[0, 0])

        options = {
            "cmap": plt.cm.gist_earth,
            "dx": dx,
            "dy": dx,
            "vert_exag": 5,
        }

        options.update(shadeargs)
        rgb = ls.shade(elev[0], **options)

        imargs = {"alpha": 1, "zorder": 20, "interpolation": "bicubic"}
        imargs.update(kwargs)
        ax.imshow(rgb, extent=extent, **imargs)

    def plot_contour(self, ax, step=10, **kwargs):

        x, y = self.X, self.Y
        elev = self.raster_data

        interlevels = np.arange(step * (self.min_elev // step), self.max_elev, step)
        ax.contour(
            x,
            y,
            elev[0],
            colors="sienna",
            levels=interlevels,
            linewidths=0.5,
            zorder=28,
        )

        levels = interlevels[::5]
        CS = ax.contour(
            x, y, elev[0], colors="sienna", levels=levels, linewidths=1, zorder=29
        )

        effect = [pe.withStroke(linewidth=2, foreground="white")]
        txts = ax.clabel(CS, fontsize=8, inline=False)
        for txt in txts:
            txt.set(path_effects=effect, zorder=50)

    def save_geotiff(self, name, ax, fig):

        a, b, c, d = self.extent

        ax.set_xlim(a, b)
        ax.set_ylim(c, d)
        ax.set_axis_off()
        # ax.set_frame_on(False)

        px_per_unit = ax.transData.transform([(0, 1), (1, 0)]) - ax.transData.transform(
            (0, 0)
        )
        cropx = 2 / px_per_unit[1, 0]
        cropy = 2 / px_per_unit[0, 1]
        a, b = a + cropx, b - cropx
        c, d = c + cropy, d - cropy
        bbox = Bbox([[a, c], [b, d]])
        bbox = bbox.transformed(ax.transData)
        bbox = bbox.transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(name, dpi=100, bbox_inches=bbox)

        with rasterio.open(
            name,
            "r+",
            driver="GTiff",
        ) as dst:
            crs = rasterio.CRS.from_string(self.crs)
            transform = rasterio.transform.from_bounds(
                a, c, b, d, dst.width, dst.height
            )
            dst.crs = crs
            dst.transform = transform
        print(f"saved {name}")
