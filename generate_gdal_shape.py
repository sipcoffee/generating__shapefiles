import rasterio
import numpy as np
from skimage import measure
from shapely.geometry import Polygon
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.ops import unary_union


# Function to calculate the area of each polygon
def calculate_polygon_area(polygon):
    # Round the area to 3 decimal points
    return round(polygon.area, 6)

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
    threshold = 0.15
    vari_mask = vari > threshold

   # Find contours using skimage
    contours = measure.find_contours(vari_mask, 0.2)
   
   # Convert contours to polygons and save to GeoDataFrame
    geometries = []
    for idx, contour in enumerate(contours):
        polygon = Polygon(contour[:, ::-1])
        polygon_with_id = (idx + 1, polygon)    
        geometries.append(polygon_with_id)
      
    # Convert contours to polygons and merge them
    # geometries = [Polygon(contour[:, ::-1]) for contour in contours]
    # merged_geometry = unary_union(geometries)

    #print("merged geom ",merged_geometry)
    # Create a GeoDataFrame from the list of Shapely geometries
    gdf = gpd.GeoDataFrame(geometry=[geom[1] for geom in geometries], crs=raster_crs)

    # Create a GeoDataFrame from the merged geometry
    #gdf = gpd.GeoDataFrame(geometry=[merged_geometry], crs=raster_crs)

    print('gdf', gdf)

    # Set shapefile extent to match raster's extent and resolution
    minx, miny, maxx, maxy = raster_bounds
    print('rbands', raster_bounds)

    # Calculate the scaling factor
    scale_x = (maxx - minx) / shape_row
    scale_y = (maxy - miny) / shape_col

    # Adjust the x and y origin 
    adjusted_scale_x = scale_x * 0.985
    adjusted_scale_y = scale_y * 1.015 

    print('dimen', scale_x, scale_y)
    # Set shapefile extent to match raster's extent and resolution
    gdf['geometry'] = gdf['geometry'].translate(
        xoff=minx, yoff=miny
    ).scale(
        xfact=scale_x,
        yfact=-adjusted_scale_y,
        origin=(minx, maxy)
    )

    # Add a unique ID for the transformed bounding box
    gdf['id'] = [geom[0] for geom in geometries]
    # gdf['id'] = 1 

    # Calculate and add area for each polygon
    gdf['area_sqm'] = gdf['geometry'].apply(lambda geom: calculate_polygon_area(geom))
    
    # Add a label indicating nitrogen deficiency for the bounding box
    gdf['label'] = 'nitrogen_deficient'

    print('bounds', gdf.bounds)
    
    print(gdf.head())

# Check and explode MultiPolygons into Polygons if present
if gdf['geometry'].geom_type.any() == 'MultiPolygon':
    gdf = gdf.explode()
    
#Save GeoDataFrame to a shapefile
shapefile_path = 'shp/1ha_gg.shp'  # Change this to your desired output path
gdf.to_file(shapefile_path, encoding='utf-8')

