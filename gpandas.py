import rasterio
import numpy as np
from skimage import measure
from shapely.geometry import Polygon
import geopandas as gpd
import matplotlib.pyplot as plt
import pyproj
from rasterio.warp import reproject, Resampling, CRS
from io import BytesIO
import tempfile
import shutil


# Open the raster file
with rasterio.open('extracted_new_crop.tif') as dataset:
        red_band = dataset.read(1).astype(np.float32)
        green_band = dataset.read(2).astype(np.float32)
        blue_band = dataset.read(3).astype(np.float32)

        denominator = green_band + red_band - blue_band
        denominator = np.where(np.isclose(denominator, 0), 1e-6, denominator)  # Avoid division by nearly zero
        vari = (green_band - red_band) / denominator

        vari[np.logical_or(vari == 0, np.isnan(vari))] = 0
        vari = np.clip(vari, -1, 1)


        new_tiff_profile = dataset.profile  # Copy the profile from the original dataset
        new_tiff_profile.update(
            dtype=rasterio.float32,  # Update the data type to match the VARI data
            count=1,  # Only one band for VARI
            compress='lzw',  # You can choose a compression method if needed
            tiled=False,
            blockysize=1,
            nodata=0.0
        )

        output_tiff_path = 'vari/vari.tif'

        new_crs = pyproj.CRS.from_epsg(32651)
        new_tiff_profile.update(crs=new_crs)

        with rasterio.open(output_tiff_path, 'w', **new_tiff_profile) as new_tiff:
            new_tiff.write(vari, 1)

