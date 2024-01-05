import rasterio
import numpy as np
from skimage import measure
from shapely.geometry import Polygon
import geopandas as gpd
import matplotlib.pyplot as plt
from rasterio.warp import transform_bounds
from shapely.geometry import box
from osgeo import gdal

#from rasterio import features

with rasterio.open('vari/vari.tif') as dataset:
    vari = dataset.read(1).astype(np.float32)
    raster_bounds = dataset.bounds
    raster_transform = dataset.transform
    raster_crs = dataset.crs
    shape_row = dataset.shape[1]
    shape_col = dataset.shape[0]
    print('raster bounds ', raster_bounds)
    print('raster transform ', raster_transform)
    print('raster crs', raster_crs)

   # Define a threshold for VAR I
    threshold = 0.3
    vari_mask = vari > threshold

   # Find contours using skimage
    contours = measure.find_contours(vari_mask, 0.5)
   
   # Convert contours to polygons and save to GeoDataFrame
    geometries = []
    for idx, contour in enumerate(contours):
        polygon = Polygon(contour[:, ::-1])  
        geometries.append(polygon)
      
   #
    # Create a GeoDataFrame from the list of Shapely geometries
    gdf = gpd.GeoDataFrame(geometry=geometries, crs=raster_crs)

    # Ensure shapefile extent matches raster extent
    # raster_bounds_transformed = transform_bounds(raster_crs, gdf.crs, *raster_bounds)
    # gdf['geometry'] = gdf['geometry'].translate(
    #     -raster_bounds[0] + raster_bounds_transformed[0],
    #     -raster_bounds[1] + raster_bounds_transformed[1]
    # )

    # Set shapefile extent to match raster's extent and resolution
    minx, miny, maxx, maxy = raster_bounds
    print('rbands', raster_bounds)

    # Calculate the scaling factor
    scale_x = (maxx - minx) / shape_row
    scale_y = (maxy - miny) / shape_col

    print('dimen', scale_x, scale_y)
    # Set shapefile extent to match raster's extent and resolution
    gdf['geometry'] = gdf['geometry'].translate(
        xoff=minx, yoff=miny
    ).scale(
        xfact=+scale_x,
        yfact=-scale_y,
        origin=(minx, maxy)
    )

    # Add a unique ID for the transformed bounding box
    gdf['id'] = 1
    
   # Add a label indicating nitrogen deficiency for the bounding box
    gdf['label'] = 'nitrogen_deficient'

    print('bounds', gdf.bounds)
    
    print(gdf.head())

#Save GeoDataFrame to a shapefile
shapefile_path = 'shp/vari_threshold_dd.shp'  # Change this to your desired output path
gdf.to_file(shapefile_path, encoding='utf-8')