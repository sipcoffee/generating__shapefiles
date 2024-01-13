import numpy as np
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
from skimage.morphology import closing, opening 

#from rasterio import features
with rasterio.open('vari/1ha_test.tif') as dataset:
    vari = dataset.read(1).astype(np.float32)


    threshold1 = 0.2  # Adjust thresholds based on your needs
    threshold2 = 0.3

    zonation = np.zeros_like(vari)
    zonation[vari < threshold1] = 1  # Zone 1
    zonation[(vari >= threshold1) & (vari < threshold2)] = 2  # Zone 2
    zonation[vari >= threshold2] = 3  # Zone 3  
    
    selem = np.ones((5, 5))

    # Apply morphological closing to smooth edges and fill small holes
    zonation = closing(zonation, selem)  # Adjust structuring element size as needed

    print('zonation', zonation)

    plt.imshow(zonation, cmap="viridis")
    plt.colorbar(label="Zones")
    plt.show()

# with rasterio.open("zone/zonation_map.tif", "w", **dataset.meta) as dst:
#     dst.write(zonation, 1)
