import rasterio
import json
import os
from pyproj import CRS, Transformer
import numpy as np
import pyproj
import matplotlib.pyplot as plt
from skimage import measure
from osgeo import ogr, osr
from shapely.geometry import Polygon

shapefile_path = 'output/vari_threshold.shp'  # Change this to your desired output path
driver = ogr.GetDriverByName("ESRI Shapefile")

try:
    data_source = driver.CreateDataSource(shapefile_path)
    if data_source is None:
        raise Exception("Failed to create the data source.")

    layer = data_source.CreateLayer("vari_threshold", geom_type=ogr.wkbPolygon)
    if layer is None:
        raise Exception("Failed to create the layer.")

    # Rest of your code for adding features, setting CRS, etc.

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

        # Define a threshold for VARI
        threshold = 0.3
        vari_mask = vari > threshold

        # Find contours using skimage
        contours = measure.find_contours(vari_mask, 0.5)

        # Create a field for VARI values
        field_defn = ogr.FieldDefn("VARI", ogr.OFTReal)
        layer.CreateField(field_defn)

        # Convert contours to polygons and save to shapefile
        for contour in contours:
            polygon = ogr.Geometry(ogr.wkbPolygon)
            ring = ogr.Geometry(ogr.wkbLinearRing)

            # Add points to the ring
            for point in contour:
                ring.AddPoint(*point[::-1])  # Convert numpy array (y, x) to (x, y)

            # Close the ring
            ring.CloseRings()
            polygon.AddGeometry(ring)

            # Create a feature and set the VARI value
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetGeometry(polygon)
            feature.SetField("VARI", float(threshold))  # Set VARI value
            layer.CreateFeature(feature)
            feature = None

        # Set the CRS for the layer
        if layer.GetLayerDefn().GetGeomType() == ogr.wkbPoint:
            geom_type = ogr.wkbPoint
        elif layer.GetLayerDefn().GetGeomType() == ogr.wkbPolygon:
            geom_type = ogr.wkbPolygon
        else:
            geom_type = ogr.wkbUnknown

        # Create the SpatialReference and assign it to the layer
        spatial_ref = osr.SpatialReference()
        spatial_ref.ImportFromEPSG(32651)
        layer_defn = layer.GetLayerDefn()
        layer.CreateField(ogr.FieldDefn("ID", ogr.OFTInteger))  # Add a dummy field
        layer.CreateField(ogr.FieldDefn("VARI", ogr.OFTReal))  # Add a dummy field
        layer.StartTransaction()
        layer.CommitTransaction()
        layer = None  # Close the layer to save changes
        data_source = None  # Close the data source

        # Open the shapefile again to set the Spatial Reference
        data_source = driver.Open(shapefile_path, 1)  # 1 is read/write mode
        layer = data_source.GetLayer()
        layer.SetSpatialRef(spatial_ref)
        
        data_source = None

        # Displaying the vari array using Matplotlib
        plt.figure(figsize=(8, 8))
        plt.imshow(vari, cmap='RdYlGn')  # You can choose any colormap you prefer
        plt.colorbar(label='Variability Index')
        plt.title('Vegetation Ratio Index (VARI)')
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.show()

except Exception as e:
    print("Error:", e)
finally:
    if data_source:
        data_source.Destroy()