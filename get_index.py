import rasterio
import numpy as np
from skimage import measure
from shapely.geometry import Polygon
import geopandas as gpd
import matplotlib.pyplot as plt

with rasterio.open('vari/vari.tif') as dataset:
    vari = dataset.read(1).astype(np.float32)

    # Define a threshold for VARI
    threshold = 0.3
    vari_mask = vari > threshold


    # Find contours using skimage
    contours = measure.find_contours(vari_mask, 0.5)
    # Convert contours to polygons and save to GeoDataFrame
    geometries = []
    for idx, contour in enumerate(contours):
        polygon = Polygon(contour[:, ::-1])  # Convert numpy array (y, x) to Shapely Polygon (x, y)
        geometries.append(polygon)

    # Create a GeoDataFrame from the list of Shapely geometries
    gdf = gpd.GeoDataFrame({'geometry': geometries})

    # Define the CRS for the GeoDataFrame
    gdf.crs = 'EPSG:32651'  # Set the CRS according to your data

    gdf['area'] = gdf['geometry'].area

    # Add a unique ID for each polygon
    gdf['id'] = range(1, len(gdf) + 1)

    # Add a label indicating nitrogen deficiency
    gdf['label'] = 'nitrogen_deficient'

    # Save GeoDataFrame to a shapefile
    shapefile_path = 'vari_threshold.shp'  # Change this to your desired output path
    gdf.to_file(shapefile_path)