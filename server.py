from flask import Flask, render_template, request, redirect, url_for
import os
from copy import deepcopy
from functions import *

app = Flask(__name__)

# Set up the upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(filename, new_image, operation):
    new_filename = f"{operation}_{filename}"
    new_filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    new_image.save(new_filepath)
    # Redirect to the display route with the filenames as parameters
    return redirect(url_for('display_images', original_image=filename, modified_image=new_filename))

# Home page where users can upload an image
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        operation = request.form.get('operation')
        if file.filename == '':
            return "No selected file"
        
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the image (convert to greyscale)
            image = Image.open(filepath)
            # handle case where image is using a different encoding scheme
            if image.mode == "P":
                image = image.convert("RGB")
                
            image_array = np.array(image)

            if ("greyscale" == operation):
                greyscale_image = image.convert('L')
                return save_file(filename, greyscale_image, operation)
            
            elif ("darker" == operation):
                darker_image = darken(image_array)
                return save_file(filename, darker_image, operation)
            
            elif ("dithering" == operation):
                dithered_image = ordered_dithering(image)
                return save_file(filename, dithered_image, operation)

            elif ("autolvl" == operation):
                auto_lvl_image = auto_lvl(image_array)
                return save_file(filename, auto_lvl_image, operation)
        
            elif ("saturation" == operation):
                saturated_image = saturation(image_array)
                return save_file(filename, saturated_image, operation)
        
            elif ("brighter" == operation):
                brighter_image = brighten(image_array)
                return save_file(filename, brighter_image, operation)
            
            elif ("interlaced" == operation):
                interlaced_image = interlace(image_array)
                return save_file(filename, interlaced_image, operation)

            elif ("darken_grey" == operation):
                greyscale_image = image.convert('L')
                darker_image = darken(np.array(greyscale_image))
                return save_file(filename, darker_image, operation)
            
            elif ("auto_and_saturate" == operation):
                auto_lvl_image = auto_lvl(image_array)
                auto_lvl_saturated_image = saturation(np.array(auto_lvl_image))
                return save_file(filename, auto_lvl_saturated_image, operation)
            
            elif ("og_and_darker" == operation):
                darker_image = darken(image_array)
                new_image = interlace_two(image_array, np.array(darker_image))
                return save_file(filename, new_image, operation)
            
            elif ("darker_and_auto" == operation):
                darker_image = darken(image_array)
                auto_lvl_image = auto_lvl(image_array)
                new_image = interlace_two(np.array(darker_image), np.array(auto_lvl_image))
                return save_file(filename, new_image, operation)

    return render_template('index.html')

@app.route('/interlace_two')
def interlace_two():
    return render_template('interlace_two.html')

# New route to display the original and modified images
@app.route('/display/<original_image>/<modified_image>')
def display_images(original_image, modified_image):
    return render_template('display.html', original_image=original_image, modified_image=modified_image)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, port=5001)
