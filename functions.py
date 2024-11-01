# functions.py
# contains the functions used to modify the images
import numpy as np
from PIL import Image
import pandas as pd
import sys
import ctypes

my_functions = ctypes.CDLL('./my_functions.so')

def darken(image_array):
    if image_array.shape[-1] == 3: # RGB
        image_array = (image_array // 2).astype(np.uint8)
    
    elif image_array.shape[-1] == 4: # contains an alpha channel
        image_array[:, :, :3] = (image_array[:, :, :3] // 2).astype(np.uint8)

    elif len(image_array.shape) == 2: # probably greyscale
        image_array = (image_array // 2).astype(np.uint8)

    else: # weird format
        image_array = (image_array // 2).astype(np.uint8)

    # Convert back to PIL Image
    return Image.fromarray(image_array)
    
# IMPORTANT: unlike other functions, this function takes an image as input
def ordered_dithering(image):
    bayer_matrix = np.array([
        [0,  8,  2, 10],
        [12, 4, 14, 6],
        [3,  11, 1, 9],
        [15, 7, 13, 5]
    ], dtype=np.uint8)

    image = image.convert('L')
    image_array = (np.array(image, dtype=np.uint8) // 15).astype(np.uint8)  # Normalize values
    
    # Get the dimensions of the image
    height, width = image_array.shape
    
    # Tile the Bayer matrix to cover the whole image
    tiled_matrix = np.tile(bayer_matrix, (height // 4 + 1, width // 4 + 1))[:height, :width]
    
    # Perform the ordered dithering: compare each pixel to the Bayer matrix value
    dithered_image_array = (image_array > tiled_matrix).astype(np.uint8) * 255

    # Convert back to a PIL image
    return Image.fromarray(dithered_image_array)

def auto_lvl(image_array):
    # Processing for grayscale
    if len(image_array.shape) == 2:
        max_intensity = image_array.max()
        min_intensity = image_array.min()

        intensity_factor = 255 / (max_intensity - min_intensity)

        # Apply the adjustment and clip the values
        auto_lvl_array = ((image_array - min_intensity) * intensity_factor).clip(0, 255).astype(np.uint8)
        
    else:
        # Get the shape of the image array (height, width, channels)
        _,  _, channels = image_array.shape

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

    # Convert back to an image
    return Image.fromarray(auto_lvl_array)

def saturation(image_array):
    if len(image_array.shape) == 2:
        # you cannot sautrate a greyscale image. return original image
        return Image.fromarray(image_array)        

    height, width, channels = image_array.shape

    # Reshape the array to have height * width rows and 3 columns (for RGB channels)
    reshaped = image_array.reshape((height * width * channels)).astype(np.int16)
    
    my_functions.saturate.argtypes = (ctypes.POINTER(ctypes.c_short), ctypes.c_int, ctypes.c_int)
    my_functions.saturate(reshaped.ctypes.data_as(ctypes.POINTER(ctypes.c_short)), reshaped.size, channels)
    saturated_array = reshaped.reshape(height, width, channels).astype(np.uint8)
    return Image.fromarray(saturated_array)

def brighten(image_array):
    if image_array.shape[-1] == 3: # RGB
        image_array = image_array * 1.25
    
    elif image_array.shape[-1] == 4: # contains an alpha channel
        image_array[:, :, :3] = (image_array[:, :, :3] * 1.25)

    elif len(image_array.shape == 2): # probably greyscale
        image_array = image_array * 1.25
    
    else: # weird format
        image_array = image_array * 1.25
    
    image_array = np.clip(image_array, 0, 255)  # Clip to ensure values are within [0, 255]
    image_array = image_array.astype(np.uint8)  # Convert back to uint8 after clipping
    
    # Convert back to PIL Image
    return Image.fromarray(image_array)

def interlace(image_array):
    if len(image_array.shape) == 2:
        height, width = image_array.shape
        channels = 1
    else:
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
        return Image.fromarray(image_array)


    new_reshaped = df.to_numpy(dtype=np.uint8)
    interlaced_arary = new_reshaped.reshape(height, width, channels)

    return Image.fromarray(interlaced_arary)

# for this function, the two arrays must have the same size and shape, otherwise an error will occur
def interlace_two(image_array1, image_array2):
    if len(image_array1.shape) == 2:
        height, width = image_array1.shape
        channels = 1
    else:
        height, width, channels = image_array1.shape

    reshaped1 = image_array1.reshape(height, width * channels)
    reshaped2 = image_array2.reshape(height, width * channels)

    df1 = pd.DataFrame(reshaped1)
    df2 = pd.DataFrame(reshaped2)

    odd_mask = df1.index % 2 != 0

    if (channels == 3 or channels == 1):
        df1.loc[odd_mask, :] = df2.loc[odd_mask, :]
    elif channels == 4:
        cols_to_modify = [col for col in df1.columns if (col + 1) % 4 != 0]
        df1.loc[odd_mask, cols_to_modify] = df2.loc[odd_mask, :]

    new_reshaped = df1.to_numpy(dtype=np.uint8)
    interlaced_array = new_reshaped.reshape(height, width, channels)

    return Image.fromarray(interlaced_array)

def blur(image_array):
    if len(image_array.shape) == 2: # greyscale image
        height, width = image_array.shape

        my_functions.blurGrey.argtypes = (
            ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int
        )

        my_functions.blurGrey(
            height, width, reshaped.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)), outputC.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)), size
        )
        
    else: # coloured image
        height, width, channels = image_array.shape

        size = height * width * channels
        reshaped = image_array.reshape(size)
        outputC = np.zeros(size).astype(np.uint8)

        my_functions.blur.argtypes = (
            ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int
        )

        my_functions.blur(
            height, width, reshaped.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)), outputC.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)), size, channels
        )

    blurred_array = outputC.reshape(height, width, channels)
    return Image.fromarray(blurred_array)

    


