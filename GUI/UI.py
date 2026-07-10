from flask import Flask, request, render_template
import joblib
import cv2
import os

app = Flask(__name__)

# Load the model
model = joblib.load("CModel.pkl")

# Define a function for image classification
def classify_single_image(image_path):
    img = cv2.imread(image_path, 0)
    img = cv2.resize(img, (200, 200))
    img_processed = img.reshape(1, -1) / 255
    prediction = model.predict(img_processed)
    if prediction[0] == 0:
        return 'Normal'
    else:
        return 'Lung cancer'

# Define a route to render the HTML page with the form
@app.route('/')
def index():
    return render_template('index.html')

# Define a route to handle image classification
@app.route('/classify', methods=['GET','POST'])
def classify():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    if file:
        # Save the uploaded image temporarily
        temp_path = 'temp.jpg'
        file.save(temp_path)
        
        # Perform classification
        prediction = classify_single_image(temp_path)
        print(prediction)
        
        # Delete the temporary file
        #os.remove(temp_path)
        #return render_template('output.html', prediction=prediction)
        return prediction
        

if __name__ == '__main__':
    app.run(debug=True)
