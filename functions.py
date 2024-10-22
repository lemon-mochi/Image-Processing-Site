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

def auto_lvl(image):
    # handle case where image is using a different encoding scheme
    if image.mode == "P":
        image = image.convert("RGB")

    image_array = np.array(image)
    # Get the shape of the image array (height, width, channels)
    height, width, channels = image_array.shape
    
    # Reshape the array to have height * width rows and 3 columns (for RGB channels)
    reshaped = image_array.reshape((height * width, channels))

    # I have to set type to int because the default is an 8 bit int which is too small
    if (channels == 3):
        df = pd.DataFrame(reshaped, columns=['red', 'green', 'blue']).astype(int)
    elif (channels == 4):
        df = pd.DataFrame(reshaped, columns=['red', 'green', 'blue', 'alpha']).astype(int)
    elif (channels == 1):
        df = pd.DataFrame(reshaped, columns=['intensity']).astype(int)
        max_intensity = df['intensity'].max()
        min_intensity = df['intensity'].min()

        intensity_factor = 255 / (max_intensity - min_intensity)

        # Apply the adjustment and clip the values
        df['intensity'] = (df['intensity'] - min_intensity) * intensity_factor
        df['intensity'] = df['intensity'].clip(0, 255)

        # Convert back to numpy array and reshape
        new_reshaped = df.to_numpy(dtype=np.uint8)
        auto_lvl_array = new_reshaped.reshape(height, width, channels)
        return Image.fromarray(auto_lvl_array)
    else:
        print("Given image does not have three, four, or one channels, return original image")
        return image

    # find the max and min for each colour channel
    max_r = df['red'].max()
    max_g = df['green'].max()
    max_b = df['blue'].max()

    min_r = df['red'].min()
    min_g = df['green'].min()
    min_b = df['blue'].min()

    red_factor = 255 / (max_r - min_r)
    green_factor = 255 / (max_g - min_g)
    blue_factor = 255 / (max_b - min_b)

    # apply the changes to the pixels
    df['red'] = (df['red'] - min_r) * red_factor
    df['green'] = (df['green'] - min_g) * green_factor
    df['blue'] = (df['blue'] - min_b) * blue_factor

    # ensure that the values are from 0 to 255
    df['red'] = df['red'].clip(0, 255)
    df['green'] = df['green'].clip(0, 255)
    df['blue'] = df['blue'].clip(0, 255)

    # convert back to numpy array
    new_reshaped = df.to_numpy(dtype=np.uint8)
    auto_lvl_array = new_reshaped.reshape(height, width, channels)

    return Image.fromarray(auto_lvl_array)
    
def saturation(image):
    # handle case where image is using a different encoding scheme
    if image.mode == "P":
        image = image.convert("RGB")

    image_array = np.array(image)
    # Get the shape of the image array (height, width, channels)
    height, width, channels = image_array.shape
    # Reshape the array to have height * width rows and 3 columns (for RGB channels)
    reshaped = image_array.reshape((height * width, channels))

    # I have to set type to int because the default is an 8 bit int which is too small
    if (channels == 3):
        df = pd.DataFrame(reshaped, columns=['red', 'green', 'blue']).astype(int)
    elif (channels == 4):
        df = pd.DataFrame(reshaped, columns=['red', 'green', 'blue', 'alpha']).astype(int)
    # no need to check for greyscale image because you cannot saturate a grey image
    else:
        print("Given image does not have three or four channels, return original image")
        return image

    df.loc[:, 'avg'] = (df['red'] + df['green'] + df['blue']) // 3

    # use a scale of 1.4
    df['red'] = (df['avg'] + 1.4  * (df['red'] - df['avg']))
    df['green'] = (df['avg'] + 1.4 * (df['green'] - df['avg']))
    df['blue'] = (df['avg'] + 1.4 * (df['blue'] - df['avg']))

    # I do not need this anymore
    df.drop(['avg'], axis=1, inplace=True)

    # ensure that the values are from 0 to 255
    df['red'] = df['red'].clip(0, 255)
    df['green'] = df['green'].clip(0, 255)
    df['blue'] = df['blue'].clip(0, 255)

    new_reshaped = df.to_numpy(dtype=np.uint8)
    saturated_array = new_reshaped.reshape(height, width, channels)

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


