import os
import tempfile

from flask import Flask, request, render_template
import joblib
import cv2

app = Flask(__name__)

# Resolve the model relative to this file so the app works from any cwd.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "CModel.pkl")

# Load the model
model = joblib.load(MODEL_PATH)


# Define a function for image classification
def classify_single_image(image_path):
    img = cv2.imread(image_path, 0)
    if img is None:
        return None
    img = cv2.resize(img, (200, 200))
    img_processed = img.reshape(1, -1) / 255
    prediction = model.predict(img_processed)
    return 'Normal' if prediction[0] == 0 else 'Lung cancer'


# Define a route to render the HTML page with the form
@app.route('/')
def index():
    return render_template('index.html')


# Define a route to handle image classification
@app.route('/classify', methods=['POST'])
def classify():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400

    # Save the uploaded image to a unique temporary file, then always clean up.
    fd, temp_path = tempfile.mkstemp(suffix='.jpg')
    os.close(fd)
    try:
        file.save(temp_path)
        prediction = classify_single_image(temp_path)
    finally:
        os.remove(temp_path)

    if prediction is None:
        return 'Invalid or unreadable image file', 400

    print(prediction)
    return prediction


if __name__ == '__main__':
    # Never enable the debugger by default (Werkzeug debugger allows RCE).
    debug = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    app.run(debug=debug)
