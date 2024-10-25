# functions_tester.py
# This file is used for testing functions in functions.py without having to start the server

import functions
from PIL import Image
import sys

imagefile = f'static/uploads/{sys.argv[1]}'
image = Image.open(imagefile)
new_image = functions.saturation(image)
new_image.save(f'testing/{sys.argv[1]}')
