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

    return image_array
    
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

    return dithered_image_array

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

    return auto_lvl_array

def saturation(image_array):
    if len(image_array.shape) == 2:
        # you cannot sautrate a greyscale image. return original image
        return Image.fromarray(image_array)        

    height, width, channels = image_array.shape

    # Reshape the array to have height * width rows and 3 columns (for RGB channels)
    reshaped = image_array.reshape((height * width * channels)).astype(np.int16)
    
    my_functions.saturate.argtypes = (ctypes.POINTER(ctypes.c_short), ctypes.c_int, ctypes.c_int)
    my_functions.saturate(
        reshaped.ctypes.data_as(ctypes.POINTER(ctypes.c_short)),
        reshaped.size, 
        channels
    )
    saturated_array = reshaped.reshape(height, width, channels).astype(np.uint8)
    return saturated_array

def brighten(image_array):
    if image_array.shape[-1] == 3: # RGB
        image_array = image_array * 1.25
    
    elif image_array.shape[-1] == 4: # contains an alpha channel
        image_array[:, :, :3] = (image_array[:, :, :3] * 1.25)

    elif len(image_array.shape) == 2: # probably greyscale
        image_array = image_array * 1.25
    
    else: # weird format
        image_array = image_array * 1.25
    
    image_array = np.clip(image_array, 0, 255)  # Clip to ensure values are within [0, 255]
    image_array = image_array.astype(np.uint8)  # Convert back to uint8 after clipping
    
    return image_array

def interlace(image_array):
    # store the greyscale boolean test so that the computer does not need
    # to check the length twice    
    greyScaleFlag = False
    if len(image_array.shape) == 2:
        height, width = image_array.shape
        reshaped = image_array.reshape(height, width)
        greyScaleFlag = True

    else:
        # Get the shape of the image array (height, width, channels)
        height, width, channels = image_array.shape

        # Reshape the array to have each row be as one
        reshaped = image_array.reshape(height, width * channels)

    df = pd.DataFrame(reshaped)
    
    odd_mask = df.index % 2 != 0

    # set every odd row to 0
    if (greyScaleFlag or channels == 3):
        df.loc[odd_mask, :] = 0
    elif channels == 4:
        cols_to_modify = [col for col in df.columns if (col + 1) % 4 != 0]
        df.loc[odd_mask, cols_to_modify] = 0
    else:
        return Image.fromarray(image_array)

    new_reshaped = df.to_numpy(dtype=np.uint8)

    if (greyScaleFlag):
        interlaced_arary = new_reshaped.reshape(height, width)
    else:
        interlaced_arary = new_reshaped.reshape(height, width, channels)

    return interlaced_arary

# for this function, the two arrays must have the same size and shape, 
# otherwise an error will occur
def interlace_two(image_array1, image_array2):
    # store the greyscale boolean test so that the computer does not need
    # to check the length twice
    greyscaleFlag = False
    if len(image_array1.shape) == 2:
        height, width = image_array1.shape
        reshaped1 = image_array1.reshape(height, width)
        reshaped2 = image_array2.reshape(height, width)
        greyscaleFlag = True

    else:
        height, width, channels = image_array1.shape
        reshaped1 = image_array1.reshape(height, width * channels)
        reshaped2 = image_array2.reshape(height, width * channels)

    df1 = pd.DataFrame(reshaped1)
    df2 = pd.DataFrame(reshaped2)

    odd_mask = df1.index % 2 != 0

    if (greyscaleFlag or channels == 3):
        df1.loc[odd_mask, :] = df2.loc[odd_mask, :]
    elif channels == 4:
        cols_to_modify = [col for col in df1.columns if (col + 1) % 4 != 0]
        df1.loc[odd_mask, cols_to_modify] = df2.loc[odd_mask, :]

    new_reshaped = df1.to_numpy(dtype=np.uint8)

    if greyscaleFlag:
        interlaced_array = new_reshaped.reshape(height, width)
    else:    
        interlaced_array = new_reshaped.reshape(height, width, channels)

    return interlaced_array

def blur(image_array):
    if len(image_array.shape) == 2: # greyscale image
        height, width = image_array.shape
        size = height * width
        reshaped = image_array.reshape(size)
        outputC = np.zeros(size).astype(np.uint8)

        my_functions.blurGrey.argtypes = (
            ctypes.c_int, 
            ctypes.c_int, 
            ctypes.POINTER(ctypes.c_ubyte), 
            ctypes.POINTER(ctypes.c_ubyte), 
            ctypes.c_int
        )

        my_functions.blurGrey(
            height, 
            width,
            reshaped.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)),
            outputC.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)), 
            size
        )

        blurred_array = outputC.reshape(height, width)
        
    else: # coloured image
        height, width, channels = image_array.shape

        size = height * width * channels
        reshaped = image_array.reshape(size)
        outputC = np.zeros(size).astype(np.uint8)

        my_functions.blur.argtypes = (
            ctypes.c_int,
            ctypes.c_int, 
            ctypes.POINTER(ctypes.c_ubyte), 
            ctypes.POINTER(ctypes.c_ubyte), 
            ctypes.c_int, 
            ctypes.c_int
        )

        my_functions.blur(
            height, 
            width, 
            reshaped.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)), 
            outputC.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)), 
            size, 
            channels
        )

        blurred_array = outputC.reshape(height, width, channels)

    return blurred_array

# Since the interlace_two function expects the two images to have the same size and shape, the
# regular greyscale method will not do as it creates a 2-dimensional array. The best way is 
# probably to create a new image which maintains the original format but all of the rgb values
# are the same so that it creates a greyscale image. This function assumes the image is not 
# already in greyscale.
def special_greyscale(image_array):
    # Check if the image has an alpha channel (4 channels)
    if image_array.shape[2] == 4:
        # Separate RGB and Alpha channels
        r, g, b, alpha = image_array[:, :, 0], image_array[:, :, 1], image_array[:, :, 2], image_array[:, :, 3]
        greyscale = 0.299 * r + 0.587 * g + 0.114 * b

        # Expand greyscale to three channels and add the original alpha channel
        greyscale = np.stack((greyscale, greyscale, greyscale, alpha), axis=-1)
    else:
        # Process as a standard RGB image if only three channels
        r, g, b = image_array[:, :, 0], image_array[:, :, 1], image_array[:, :, 2]
        greyscale = 0.299 * r + 0.587 * g + 0.114 * b

        # Expand greyscale to three channels
        greyscale = np.stack((greyscale, greyscale, greyscale), axis=-1)
    
    return greyscale