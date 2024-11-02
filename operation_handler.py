# operation_handler.py
# Written by Gen Blaine
# Nov. 2, 2024
# This file handles the user's input from the two input pages
from functions import *

def index_operation(image, operation):
    image_array = np.array(image)

    if ("greyscale" == operation):
        greyscale_array = image.convert('L')
        return greyscale_array
    
    elif ("darker" == operation):
        darker_array = darken(image_array)
        return darker_array
    
    elif ("dithering" == operation):
        dithered_array = ordered_dithering(image)
        return dithered_array

    elif ("autolvl" == operation):
        auto_lvl_array = auto_lvl(image_array)
        return auto_lvl_array

    elif ("saturation" == operation):
        saturated_array = saturation(image_array)
        return saturated_array

    elif ("brighter" == operation):
        brighter_array = brighten(image_array)
        return brighter_array
    
    elif ("interlaced" == operation):
        interlaced_array = interlace(image_array)
        return interlaced_array

    elif ("darken_grey" == operation):
        greyscale_array = image.convert('L')
        darker_array = darken(greyscale_array)
        return darker_array
    
    elif ("auto_and_saturate" == operation):
        auto_lvl_array = auto_lvl(image_array)
        auto_lvl_saturated_array = saturation(auto_lvl_array)
        return auto_lvl_saturated_array

    elif ("blurred" == operation):
        blurred_array = blur(image_array)
        return blurred_array
    
def interlace_operation(image, operation0, operation1):
    image_array = np.array(image)
    operations = [operation0, operation1]
    image_arrays = []

    for i in range(2):
        if ("original" == operations[i]):
            image_arrays.append(image_array)

        elif ("greyscale" == operations[i]):
            if image.mode == 'L': # input image is already in greyscale
                image_arrays.append(image_array)
            else:
                greyscale_array = special_greyscale(image_array)
                # The interlace_two function expects both inputs to be the 
                # same shape and size
                image_arrays.append(greyscale_array)

        elif ("darker" == operations[i]):
            darker_array = darken(image_array)
            image_arrays.append(darker_array)

        elif ("dithering" == operations[i]):
            dithered_array = ordered_dithering(image)
            # here, dithered_image is a 2-d array. If the original
            # is different, we must set the dithered_image to whatever the heck
            # the original image's mode is. This is because interlace two requires
            # the two images to be the same shape.
            if (image.mode != 'L'):
                dithered_image = Image.fromarray(dithered_array).convert(image.mode)
                dithered_array = np.array(dithered_image)

            image_arrays.append(dithered_array)

        elif ("autolvl" == operations[i]):
            auto_lvl_array = auto_lvl(image_array)
            image_arrays.append(auto_lvl_array)

        elif ("saturation" == operations[i]):
            saturated_array = saturation(image_array)
            image_arrays.append(saturated_array)

        elif ("brighter" == operations[i]):
            brighter_array = brighten(image_array)
            image_arrays.append(brighter_array)

        elif ("interlaced" == operations[i]):
            interlaced_array = interlace(image_array)
            image_arrays.append(interlaced_array)

        elif ("darken_grey" == operations[i]):
            if image.mode == 'L': # already greyscale
                image_arrays.append(image_array)
            else:
                greyscale_array = special_greyscale(image_array)
                darker_array = darken(greyscale_array)
                image_arrays.append(darker_array)

        elif ("auto_and_saturate" == operations[i]):
            auto_lvl_array = auto_lvl(image_array)
            auto_lvl_saturated_array = saturation(auto_lvl_array)
            image_arrays.append(auto_lvl_saturated_array)                        

        elif ("blurred" == operations[i]):
            blurred_array = blur(image_array)
            image_arrays.append(blurred_array)

    new_array = interlace_two(image_arrays[0], image_arrays[1])
    return new_array