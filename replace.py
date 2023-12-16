import geopandas as gpd
import rasterio


with rasterio.open('extracted_new_crop.tif') as dt:
    crs = dt.crs
    b = dt.bounds
    print('bounds-', b)
    print("raster crs",crs)

# Load the shapefile
shapefile_path = 'vari_threshold.shp'  # Replace with your shapefile path
shapefile = gpd.read_file(shapefile_path)
print('-------')
# Check the CRS of the shapefile
print("Original CRS of Shapefile:", shapefile.crs)

# Load the shapefile
shapefile_path = 'vari_threshold.shp'  # Replace with your shapefile path
shapefile = gpd.read_file(shapefile_path)

# Explicitly set the CRS of the shapefile GeoDataFrame to match the raster CRS
shapefile.crs = crs

# Check the CRS of the shapefile after setting it to match the raster CRS
print("Updated CRS of Shapefile:", shapefile.crs)
# # Reproject the shapefile to match the CRS of the raster data
# # Replace 'raster_crs' with the CRS of your raster data
shapefile = shapefile.to_crs(shapefile.crs)

# # Save the reprojected shapefile to a new file
shapefile.to_file('reprojected_shapefile.shp')
