# functions.py
# contains the functions used to modify the images
import numpy as np
from PIL import Image
import pandas as pd
import sys

def darken(image):
    # handle case where image is using a different encoding scheme
    if image.mode == "P":
        image = image.convert("RGB")

    image_array = np.array(image)
    if image_array.shape[-1] == 3: # RGB
        image_array = (image_array // 2).astype(np.uint8)
    
    elif image_array.shape[-1] == 4: # contains an alpha channel
        image_array[:, :, :3] = (image_array[:, :, :3] // 2).astype(np.uint8)

    else: # probably greyscale
        image_array = (image_array // 2).astype(np.uint8)

    # Convert back to PIL Image
    return Image.fromarray(image_array)
    
def ordered_dithering(image):
    bayer_matrix = np.array([
        [0,  8,  2, 10],
        [12, 4, 14, 6],
        [3,  11, 1, 9],
        [15, 7, 13, 5]
    ], dtype=np.uint8)

    image = image.convert('L')
    image_array = (np.array(image, dtype=np.uint8) // 15).astype(np.uint8)  # Normalize values
    print(image_array)
    
    # Get the dimensions of the image
    height, width = image_array.shape
    
    # Tile the Bayer matrix to cover the whole image
    tiled_matrix = np.tile(bayer_matrix, (height // 4 + 1, width // 4 + 1))[:height, :width]
    
    # Perform the ordered dithering: compare each pixel to the Bayer matrix value
    dithered_image_array = (image_array > tiled_matrix).astype(np.uint8) * 255

    # Convert back to a PIL image
    return Image.fromarray(dithered_image_array)

import numpy as np
from PIL import Image

def auto_lvl(image):
    # Handle case where image is using a different encoding scheme
    if image.mode == "P":
        image = image.convert("RGB")

    # Convert the image to a NumPy array
    image_array = np.array(image)

    # Get the shape of the image array (height, width, channels)
    height, width, channels = image_array.shape

    # Processing for grayscale (1 channel)
    if channels == 1:
        max_intensity = image_array.max()
        min_intensity = image_array.min()

        intensity_factor = 255 / (max_intensity - min_intensity)

        # Apply the adjustment and clip the values
        auto_lvl_array = ((image_array - min_intensity) * intensity_factor).clip(0, 255).astype(np.uint8)

    # Processing for RGB (3 channels) or RGBA (4 channels)
    elif channels in [3, 4]:
        # Separate channels
        r, g, b = image_array[:, :, 0], image_array[:, :, 1], image_array[:, :, 2]

        # Calculate factors for each channel
        red_factor = 255 / (r.max() - r.min())
        green_factor = 255 / (g.max() - g.min())
        blue_factor = 255 / (b.max() - b.min())

        # Apply auto-level for RGB
        r = ((r - r.min()) * red_factor).clip(0, 255).astype(np.uint8)
        g = ((g - g.min()) * green_factor).clip(0, 255).astype(np.uint8)
        b = ((b - b.min()) * blue_factor).clip(0, 255).astype(np.uint8)

        # Rebuild the image
        if channels == 3:
            auto_lvl_array = np.stack([r, g, b], axis=2)
        else:
            a = image_array[:, :, 3]  # Alpha channel
            auto_lvl_array = np.stack([r, g, b, a], axis=2)
    
    else:
        print("Given image does not have three, four, or one channels, returning original image")
        return image

    # Convert back to an image
    return Image.fromarray(auto_lvl_array)

    
def saturation(image):
    # Handle case where image is using a different encoding scheme
    if image.mode == "P":
        image = image.convert("RGB")

    # Convert the image to a NumPy array
    image_array = np.array(image)

    # Get the shape of the image array (height, width, channels)
    height, width, channels = image_array.shape

    # Only process RGB or RGBA images
    if channels == 3:
        r, g, b = image_array[:, :, 0], image_array[:, :, 1], image_array[:, :, 2]
    elif channels == 4:
        r, g, b, a = image_array[:, :, 0], image_array[:, :, 1], image_array[:, :, 2], image_array[:, :, 3]
    else:
        print("Given image does not have three or four channels, returning original image")
        return image

    # Calculate the average (luminance approximation) of the RGB values
    avg = (r + g + b) // 3

    # Use a saturation scale of 1.4
    saturation_scale = 1.4
    r = avg + saturation_scale * (r - avg)
    g = avg + saturation_scale * (g - avg)
    b = avg + saturation_scale * (b - avg)

    # Clip the values to ensure they are within 0-255
    r = r.clip(0, 255).astype(np.uint8)
    g = g.clip(0, 255).astype(np.uint8)
    b = b.clip(0, 255).astype(np.uint8)

    # Rebuild the image with or without alpha channel
    if channels == 3:
        saturated_array = np.stack([r, g, b], axis=2)
    else:
        saturated_array = np.stack([r, g, b, a], axis=2)

    # Convert back to an image
    return Image.fromarray(saturated_array)

def brighten(image):
    image_array = np.array(image)  # Convert to float for scaling

    image_array = image_array * 1.25
    image_array = np.clip(image_array, 0, 255)  # Clip to ensure values are within [0, 255]
    image_array = image_array.astype(np.uint8)  # Convert back to uint8 after clipping
    

    print(image_array)
    # Convert back to PIL Image
    return Image.fromarray(image_array)

def interlace(image):
    # handle case where image is using a different encoding scheme
    if image.mode == "P":
        image = image.convert("RGB")

    image_array = np.array(image)
        
    # Get the shape of the image array (height, width, channels)
    height, width, channels = image_array.shape
    
    # Reshape the array to have each row be as one
    reshaped = image_array.reshape(height, width * channels)

    # I have to set type to int because the default is an 8 bit int which is too small
    df = pd.DataFrame(reshaped)
    
    odd_mask = df.index % 2 != 0

    # set every odd row to 0
    if (channels == 3 or channels == 1):
        df.loc[odd_mask, :] = 0
    elif channels == 4:
        cols_to_modify = [col for col in df.columns if (col + 1) % 4 != 0]
        df.loc[odd_mask, cols_to_modify] = 0
    else:
        return image


    new_reshaped = df.to_numpy(dtype=np.uint8)
    interlaced_arary = new_reshaped.reshape(height, width, channels)

    return Image.fromarray(interlaced_arary)


