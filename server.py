from flask import Flask, render_template, request, redirect, url_for
import os
from copy import deepcopy
from functions import *

app = Flask(__name__)

# Set up the upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'JPG', 'JPEG'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(filename, new_image, operation):
    new_filename = f"{operation}_{filename}"
    new_filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    Image.fromarray(new_image).save(new_filepath)
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
        operation0 = request.form.get('operation0')
        operation1 = request.form.get('operation1')
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
                darker_image = darken(greyscale_image)
                return save_file(filename, darker_image, operation)
            
            elif ("auto_and_saturate" == operation):
                auto_lvl_image = auto_lvl(image_array)
                auto_lvl_saturated_image = saturation(auto_lvl_image)
                return save_file(filename, auto_lvl_saturated_image, operation)
        
            elif ("blurred" == operation):
                blurred_image = blur(image_array)
                return save_file(filename, blurred_image, operation)
            
            # handling the case where the user wanted to interlace two modifications
            if (operation1 != None):
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
                        darker_image = darken(image_array)
                        image_arrays.append(darker_image)

                    elif ("dithering" == operations[i]):
                        dithered_image = ordered_dithering(image)
                        image_arrays.append(dithered_image)

                    elif ("autolvl" == operations[i]):
                        auto_lvl_image = auto_lvl(image_array)
                        image_arrays.append(auto_lvl_image)

                    elif ("saturation" == operations[i]):
                        saturated_image = saturation(image_array)
                        image_arrays.append(saturated_image)

                    elif ("brighter" == operations[i]):
                        brighter_image = brighten(image_array)
                        image_arrays.append(brighter_image)

                    elif ("interlaced" == operations[i]):
                        interlaced_image = interlace(image_array)
                        image_arrays.append(interlaced_image)

                    elif ("darken_grey" == operations[i]):
                        greyscale_image = image.convert('L')
                        darker_image = darken(greyscale_image)
                        image_arrays.append(darker_image)

                    elif ("auto_and_saturate" == operations[i]):
                        auto_lvl_image = auto_lvl(image_array)
                        auto_lvl_saturated_image = saturation(auto_lvl_image)
                        image_arrays.append(auto_lvl_saturated_image)                        

                    elif ("blurred" == operations[i]):
                        blurred_image = blur(image_array)
                        image_arrays.append(blurred_image)

                new_image = interlace_two(image_arrays[0], image_arrays[1])
                return save_file(filename, new_image, "interlaced")

    return render_template('index.html')

@app.route('/interlace_two')
def interlace_two_html():
    return render_template('interlace_two.html')

# New route to display the original and modified images
@app.route('/display/<original_image>/<modified_image>')
def display_images(original_image, modified_image):
    return render_template('display.html', original_image=original_image, modified_image=modified_image)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, port=5001)
