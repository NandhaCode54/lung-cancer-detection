import joblib
import cv2

def classify_single_image(image_path):
    model=joblib.load("SVModel.pkl")
    img = cv2.imread(image_path, 0)
    img = cv2.resize(img, (200, 200))
    img_processed = img.reshape(1, -1) / 255
    prediction = model.predict(img_processed)
    if prediction[0] == 0:
        return 'Normal'
    else:
        return 'Lung cancer'

image_path = r'C:/Users/VASANTH/Desktop/lu.jpg'
prediction = classify_single_image(image_path)
print("Prediction for", image_path, ":", prediction)
