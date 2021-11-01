from flask import Flask, render_template, request, redirect
import os, time
from flask.helpers import flash
from werkzeug.utils import secure_filename
from gaussian_pyramid import MakeGaussianPyramid
from face_detect import FaceDetect
from PIL import Image


app = Flask(__name__)
app.secret_key = '_%s`UPH4S{&FU;8'
app.config["IMAGE_UPLOADS"] = "/Users/aziz/Desktop/webapp/static/uploads"
app.config["FACES_DETECTED_IMAGES"] = "/Users/aziz/Desktop/webapp/static/detected_faces"
app.config["ALLOWED_IMAGE_TYPES"] = ["PNG", "JPG", "JPEG"]
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Check if the submitted file has appropriate extensions
def allowed_image(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_TYPES"]:
        return True
    else:
        return False
    

@app.route('/', methods=["GET", "POST"])
def main():

    upload_page_url = "/upload_image.html"
    filename = ""

    # if there are some files requested (submitted) by the user,
    # then create a storage object for that file
    if request.method == 'POST' and request.files:
        image = request.files["image"]

        scale_input = request.form["scale"]
        threshold_input = request.form["threshold"]

        print(scale_input)
        print(threshold_input)

        if (scale_input == ""):
            scale_input = 0.75
        else:
            scale_input = float(scale_input)

        if (threshold_input == ""):
            threshold_input = 0.58
        else:
            threshold_input = float(threshold_input)


        if image.filename == "":
            #print("Image must have a filename")
            flash('Invalid extension or missing file', 'alert-danger')
            return render_template(upload_page_url, image_path="placeholder-image.png", detected_faces_image_path="placeholder-image.png")
        
        if not allowed_image(image.filename):
            print("File type is unsupported")
            flash('File type is unsupported', 'alert-danger')
            return render_template(upload_page_url, image_path="placeholder-image.png", detected_faces_image_path="placeholder-image.png") 

        else:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
        
        image_name = "/uploads/" + filename
        flash('Successfully uploaded the image!', 'alert-success')

        uploaded_image = Image.open(os.path.join(app.config["IMAGE_UPLOADS"], filename)).convert("L")
        template = Image.open("/Users/aziz/Desktop/webapp/static/template.jpg")
        gaussian_pyramid = MakeGaussianPyramid(uploaded_image, scale_input, 1)
        detected_faces = FaceDetect(gaussian_pyramid, template, threshold_input, scale_input)
        detected_faces_image_name = "detected_faces_"+str(time.time_ns())+filename
        detected_faces.save(os.path.join(app.config["FACES_DETECTED_IMAGES"], detected_faces_image_name))

        detected_faces_name = "/detected_faces/" + detected_faces_image_name

        return render_template(upload_page_url, image_path=image_name, detected_faces_image_path=detected_faces_name)

    
    return render_template(upload_page_url, image_path="placeholder-image.png", detected_faces_image_path="placeholder-image.png")
