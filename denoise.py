import numpy as np
import rasterio
import matplotlib.pyplot as plt
from skimage.restoration import denoise_nl_means, estimate_sigma
from skimage import exposure
from skimage import img_as_float, img_as_ubyte, io

#from rasterio import features
with rasterio.open('vari_grid_means_200ha.tif') as dataset:
    vari = dataset.read(1).astype(np.float32)
    meta = dataset.meta

    sigma_est = np.mean(estimate_sigma(vari,  average_sigmas=False, channel_axis=None))

    denoise = denoise_nl_means(vari, h=1.15 * sigma_est, fast_mode=True, patch_size=5, patch_distance=3)

plt.imshow(denoise)