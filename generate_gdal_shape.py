import rasterio
import numpy as np
from skimage import measure
from shapely.geometry import Polygon
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.ops import unary_union
from matplotlib.colors import to_hex


# Function to calculate the area of each polygon
def calculate_polygon_area(polygon):
    # Round the area to 3 decimal points
    return round(polygon.area, 6)

#from rasterio import features
with rasterio.open('out_raster/filters/green_average_filter_3.tif') as dataset:
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
    num_class = 5
    threshold = 0.15
    vari_mask = vari > threshold

    print('min value', np.min(vari))
    print('mean value', np.mean(vari))
    print('max value',np.max(vari))

    max_val = np.max(vari)
    min_val = np.min(vari)

    class_bins = np.linspace(0, max_val, 6)

    print('class bins', class_bins)
    # Step 3: Classify vari values into 5 classes
    classified_vari = np.digitize(vari, class_bins, right=True)

    # Step 4: Save the result as a raster
    # output_file = 'class_shapes/classified_vari_1.tif'
    # with rasterio.open(output_file, 'w', driver='GTiff', height=shape_col, width=shape_row, count=1, dtype='uint8',
    #                    crs=raster_crs, transform=raster_transform, nodata=0.0) as output_dataset:
    #     output_dataset.write(classified_vari, 1)

    #class_one = np.logical_and(classified_vari >= 0.1, classified_vari <= 1.04)

    #contours = measure.find_contours(class_one, 0.2)
    
    # Convert contours to polygons and save to GeoDataFrame
    # Find contours for each class

    contours_list = []
    for class_num in range(1, num_class + 1):
        class_mask = (classified_vari == class_num)
        contours = measure.find_contours(class_mask, 0.35)

        for idx, contour in enumerate(contours):
            polygon = Polygon(contour[:, ::-1])
            polygon_with_id = (idx + 1, polygon, class_num)
            contours_list.append(polygon_with_id)

    # geometries = []
    # for idx, contour in enumerate(contours):
    #     polygon = Polygon(contour[:, ::-1])
    #     polygon_with_id = (idx + 1, polygon)    
    #     geometries.append(polygon_with_id)
      
    # Convert contours to polygons and merge them
    # geometries = [Polygon(contour[:, ::-1]) for contour in contours]
    # merged_geometry = unary_union(geometries)

    #print("merged geom ",merged_geometry)
    # Create a GeoDataFrame from the list of Shapely geometries
    gdf = gpd.GeoDataFrame(geometry=[geom[1] for geom in contours_list], crs=raster_crs)

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
        xoff=minx, yoff=maxy
    ).scale(
        xfact=scale_x,
        yfact=-scale_y,
        origin=(minx, maxy)
    )

    # Add a unique ID for the transformed bounding box
    gdf['id'] = [geom[0] for geom in contours_list]
    # gdf['id'] = 1 
    gdf['class'] = [geom[2] for geom in contours_list]


    # Calculate and add area for each polygon
    gdf['area_sqm'] = gdf['geometry'].apply(lambda geom: calculate_polygon_area(geom))
    
    # Add a label indicating nitrogen deficiency for the bounding box
    gdf['label'] = 'nitrogen_deficient'

    # Assign different colors to each class
    colors = plt.cm.get_cmap('viridis', num_class)
    gdf['color'] = gdf['class'].map(lambda x: to_hex(colors(x - 1)))

    print('bounds', gdf.bounds)
    
    print(gdf.head())

# Check and explode MultiPolygons into Polygons if present
if gdf['geometry'].geom_type.any() == 'MultiPolygon':
    gdf = gdf.explode()
    
#Save GeoDataFrame to a shapefile
shapefile_path = 'class_shapes/all_class_5.shp'  # Change this to your desired output path
gdf.to_file(shapefile_path, encoding='utf-8')

# Save QML file for styling
qml_file_path = 'class_shapes/all_class_1.qml'  # Change this to your desired output path
style = '<!DOCTYPE qgis PUBLIC "http://mrcc.com/qgis.dtd" "SYSTEM">'
style += '<qgis version="3.0">'
style += '<renderer-v2 symbollevels="0" type="categorizedSymbol">'
style += '<categories>'
for index, row in gdf.iterrows():
    style += f'<category render="true" symbol="1" value="{row["class"]}">'
    style += f'<label>{row["class"]}</label>'
    style += f'<color alpha="1" blue="{int(row["color"][5:7], 16)}" green="{int(row["color"][3:5], 16)}" red="{int(row["color"][1:3], 16)}"/>'
    style += '</category>'
style += '</categories></renderer-v2></qgis>'

with open(qml_file_path, 'w') as qml_file:
    qml_file.write(style)