from flask import Flask, render_template, request, jsonify
from PIL import Image
import io
import base64
import numpy as np
import rasterio
from rasterio.transform import rowcol
import cv2

app = Flask(__name__)

# Global variable to store the cropped image as a NumPy array
cropped_image_np_array = None

def create_mask(image=None, latitude=None, zoom_level=None):
    if image is not None:
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        specific_value = 210
        mask = np.where((image_gray == specific_value) | (image_gray == specific_value + 1) | (image_gray == specific_value - 1), 255, 0).astype(np.uint8)
        num_white_pixels = np.sum(mask == 255)
        print(f"Number of white pixels: {num_white_pixels}")

        earth_circumference_m = 40075017
        ground_resolution = (earth_circumference_m * np.cos(np.radians(latitude))) / (2 ** (zoom_level ))
        print(f"Ground resolution: {ground_resolution} meters per pixel")

        area = num_white_pixels * (ground_resolution ** 2)
        print(f"Calculated area: {area} square meters")

        return area


def calc_ghi(lat,lng):
    # Open the AAIGRID file
    file_path = "./GHI.asc"
    with rasterio.open(file_path) as dataset:
        # Convert lat/long to row/col in the grid
        row, col = rowcol(dataset.transform, lng, lat)

        # Read the GHI value from the grid
        ghi_value = dataset.read(1)[row, col]
        return ghi_value

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_cropped_image', methods=['POST'])
def upload_cropped_image():
    global cropped_image_np_array
    
    try:
        img_data = request.form['image']
        img_data = img_data.split(",")[1]
        img_bytes = base64.b64decode(img_data)
        image = Image.open(io.BytesIO(img_bytes))
        cropped_image_np_array = np.array(image)

        latitude = float(request.form.get('latitude'))
        zoom_level = int(request.form.get('zoom_level'))
        
        area = create_mask(cropped_image_np_array, latitude, zoom_level)
        
        # Calculate the center of the selected area
        center_lat = latitude  # For the center latitude, you might need to adjust this calculation
        center_lon = 0  # Replace with actual center longitude if available
        
        ghi_value = 4.2  #calc_ghi(center_lat, center_lon)
        if ghi_value is None:
            ghi_value = 0  # Handle the case where GHI value cannot be retrieved
        
        pv_output = area * ghi_value *0.15
        
        return jsonify({'status': 'success', 'area': area, 'ghi': ghi_value, 'pv_output': pv_output})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
