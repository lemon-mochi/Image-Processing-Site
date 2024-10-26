# Image Processing Site
This is the reporsitory for the image processing site. The website takes a user's uploaded photo and performs a selected modification to the image. Then, the website redirects to a results page where the two images are shown side-by-sdie.
## Running Locally
To run locally, enter
```
python3 server.py
```
in the main directory
## Libraries needed
This program's backend is written in Python and C. Both the python interperter and C compiler are needed to run this.
This program uses `NumPy`, `Pandas`, `ctypes`, and `pillow`.
The `gcc` compiler is also needed to create the shared library

## Creating the shared library
```
cc -fPIC -shared my_functions.c -o my_functions.so
```