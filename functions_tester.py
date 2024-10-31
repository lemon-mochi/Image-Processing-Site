# functions_tester.py
# This file is used for testing functions in functions.py without having to start the server

import functions
from PIL import Image
import sys

imagefile = f'static/uploads/{sys.argv[1]}'
image = Image.open(imagefile)
# handle case where image is using a different encoding scheme
if image.mode == "P":
    image = image.convert("RGB")
image_array = functions.np.array(image)
new_image = functions.ordered_dithering(image)
new_image.save(f'testing/{sys.argv[1]}')
