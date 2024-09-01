
import cv2
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.transform import rowcol

def area_calc(image=None,zoom_lvl=None):

    image = cv2.imread('img.png')

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    scaling_factor = 0.25 # Scale down by 50%
    new_width = int(image.shape[1] * scaling_factor)
    new_height = int(image.shape[0] * scaling_factor)

    sd = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    specific_value = 233
    mask = np.where(sd == specific_value, 255, 0).astype(np.uint8)
    print(mask.shape)

    cv2.imwrite('thresholded_image.jpg', mask)
    return mask

m2=area_calc()


# Count the number of white pixels (value = 255)
w= np.sum(m2 == 255)

print(f"Number of white pixels: {w-w%2000}")


def calc_ghi(lat,lng):
    # Open the AAIGRID file
    file_path = "/content/drive/MyDrive/modelz/giss/GHI.asc"
    with rasterio.open(file_path) as dataset:
        # Convert lat/long to row/col in the grid
        row, col = rowcol(dataset.transform, lon, lat)

        # Read the GHI value from the grid
        ghi_value = dataset.read(1)[row, col]
        return ghi_value

lat = 11.025770
lon = 76.938520

ghi_val = calc_ghi(lat,lon)

print(f"GHI value at ({lat}, {lon}): {ghi_val:.4f} KWh/sq.m/Day -- Power/sq.m/Day")

