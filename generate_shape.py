import rasterio
import numpy as np
from skimage import measure
from shapely.geometry import Polygon
import geopandas as gpd
import matplotlib.pyplot as plt
from rasterio.warp import transform_bounds
from shapely.geometry import box

#from rasterio import features

with rasterio.open('vari/vari.tif') as dataset:
   vari = dataset.read(1).astype(np.float32)
   raster_bounds = dataset.bounds
   raster_transform = dataset.transform
   print('raster bounds ', raster_bounds)
   print('raster transform ', raster_transform)
   print('raster crs', dataset.crs)


   # Define a threshold for VARI
   threshold = 0.45
   vari_mask = vari > threshold

   # Find contours using skimage
   contours = measure.find_contours(vari_mask, 0.5)
   
   # Convert contours to polygons and save to GeoDataFrame
   geometries = []
   for idx, contour in enumerate(contours):
      # polygon = Polygon(contour[:, ::-1])  # Set CRS here
      # geometries.append(polygon)
      polygon = Polygon(transform_bounds(dataset.crs, 'EPSG:4326', *raster_bounds, raster_transform)(contour[:, ::-1]))
      geometries.append(polygon)
      
   #
    # Create a GeoDataFrame from the list of Shapely geometries
   gdf = gpd.GeoDataFrame(geometry=geometries, crs=dataset.crs)

   # Add a unique ID for the transformed bounding box
   gdf['id'] = 1
    
   # Add a label indicating nitrogen deficiency for the bounding box
   gdf['label'] = 'nitrogen_deficient'
   print("crs ", gdf.crs)
   print('bounds', gdf.bounds)
    
   print(gdf.head())

    #Save GeoDataFrame to a shapefile
   # shapefile_path = 'shp/vari_threshold_zz.shp'  # Change this to your desired output path
   # gdf.to_file(shapefile_path, encoding='utf-8')