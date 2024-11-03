from flask import Flask, render_template, request, redirect, url_for
import os
from operation_handler import index_operation, interlace_operation, Image

app = Flask(__name__)

# Set up the upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'JPG', 'JPEG', 'PNG', 'jfif'}

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
                
            # User wanted to modify the image from index.html
            if (operation != None):
                new_image = index_operation(image, operation)
                
                return save_file(filename, new_image, operation)
            
            # handling the case where the user wanted to interlace two modifications
            if (operation1 != None):
                new_image = interlace_operation(image, operation0, operation1)

                return save_file(filename, new_image, f"{operation0}_{operation1}_interlaced")

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
