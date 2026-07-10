import os
import sys

import joblib
import cv2

# Resolve the model relative to this file so the script works from any cwd.
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CModel.pkl")


def classify_single_image(image_path):
    model = joblib.load(MODEL_PATH)
    img = cv2.imread(image_path, 0)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    img = cv2.resize(img, (200, 200))
    img_processed = img.reshape(1, -1) / 255
    prediction = model.predict(img_processed)
    return 'Normal' if prediction[0] == 0 else 'Lung cancer'


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python predict.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    prediction = classify_single_image(image_path)
    print("Prediction for", image_path, ":", prediction)
