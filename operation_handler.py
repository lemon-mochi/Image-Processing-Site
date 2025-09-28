# operation_handler.py
# Written by Gen Blaine
# Nov. 2, 2024
# This file handles the user's input from the two input pages
# On Feb. 10, 2025, I decided to make big changes to this 
# code so that it uses a dictionary for O(1) lookup.
from functions import *

def index_operation(image, operation):
    image_array = np.array(image)

    operations = {
        "greyscale": lambda img: img.convert('L'),
        "darker": lambda img: Image.fromarray(darken(np.array(img))),
        "dithering": lambda img: Image.fromarray(ordered_dithering(img)),
        "autolvl": lambda img: Image.fromarray(auto_lvl(np.array(img))),
        "saturation": lambda img: Image.fromarray(saturation(np.array(img))),
        "brighter": lambda img: Image.fromarray(brighten(np.array(img))),
        "interlaced": lambda img: Image.fromarray(interlace(np.array(img))),
        "darken_grey": lambda img: Image.fromarray(darken(np.array(img.convert('L')))),
        "auto_and_saturate": lambda img: Image.fromarray(saturation(auto_lvl(np.array(img)))),
        "blurred": lambda img: Image.fromarray(blur(np.array(img))),
        "balance": lambda img: Image.fromarray(balance(np.array(img))),
        "distort1": lambda img: Image.fromarray(distort(np.array(img), 1)),
        "distort2": lambda img: Image.fromarray(distort(np.array(img), 2)),
        "upscale": lambda img: Image.fromarray(upscale(np.array(img))),
        "colours1": lambda img: Image.fromarray(colours(np.array(img), 1)),
        "colours2": lambda img: Image.fromarray(colours(np.array(img), 2)),
    }

    return operations.get(operation, lambda img: img)(image)  # Default to returning the original image

    
def interlace_operation(image, operation0, operation1):
    image_array = np.array(image)
    operations = [operation0, operation1]
    
    operation_dict = {
        "original": lambda img: np.array(img),
        "greyscale": lambda img: np.array(img) if img.mode == 'L' else special_greyscale(np.array(img)),
        "darker": lambda img: darken(np.array(img)),
        "dithering": lambda img: np.array(Image.fromarray(ordered_dithering(img)).convert(img.mode) if img.mode != 'L' else ordered_dithering(img)),
        "autolvl": lambda img: auto_lvl(np.array(img)),
        "saturation": lambda img: saturation(np.array(img)),
        "brighter": lambda img: brighten(np.array(img)),
        "interlaced": lambda img: interlace(np.array(img)),
        "darken_grey": lambda img: darken(np.array(img)) if img.mode == 'L' else darken(special_greyscale(np.array(img))),
        "auto_and_saturate": lambda img: saturation(auto_lvl(np.array(img))),
        "blurred": lambda img: blur(np.array(img))
    }

    image_arrays = [operation_dict.get(op, lambda img: np.array(img))(image) for op in operations]

    new_array = interlace_two(image_arrays[0], image_arrays[1])
    return Image.fromarray(new_array)
