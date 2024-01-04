import rasterio
import numpy as np
from skimage import measure
from shapely.geometry import Polygon, box
import geopandas as gpd
import pandas as pd

with rasterio.open('vari/vari.tif') as dataset:
    vari = dataset.read(1).astype(np.float32)
    raster_bounds = dataset.bounds

    # Define a threshold for VARI
    threshold = 0.3
    vari_mask = vari > threshold

    # Find contours using skimage
    contours = measure.find_contours(vari_mask, 0.5)

    # Convert contours to polygons and save to GeoDataFrame
    geometries = []
    for idx, contour in enumerate(contours):
        polygon = Polygon(contour[:, ::-1])  # Assuming CRS is already set in dataset
        geometries.append(polygon)

    # Create a GeoDataFrame from the list of Shapely geometries
    gdf = gpd.GeoDataFrame({'geometry': geometries})

    gdf.crs = dataset.crs  # Set CRS from the raster dataset

    # Add the bounding box as a new row in the GeoDataFrame
    bbox_polygon = box(*raster_bounds)
    bbox_gdf = gpd.GeoDataFrame({'geometry': bbox_polygon, 'label': 'bounding_box'}, index=[0])
    bbox_gdf.crs = dataset.crs  # Set CRS explicitly
    gdf = pd.concat([gdf, bbox_gdf], ignore_index=True)
    
    # Calculate area for the polygons (excluding the bounding box)
    gdf['area'] = gdf.loc[gdf['label'] != 'bounding_box', 'geometry'].area

    # Add a unique ID for each polygon (excluding the bounding box)
    gdf.loc[gdf['label'] != 'bounding_box', 'id'] = range(1, len(gdf.loc[gdf['label'] != 'bounding_box']) + 1)

    # Save GeoDataFrame to a shapefile
    shapefile_path = 'shp/vari_threshold_zz.shp'  # Change this to your desired output path
    gdf.to_file(shapefile_path, encoding='utf-8')
