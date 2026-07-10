# Lung Cancer Detection

Classifies lung images as **Normal** or **Lung cancer** using a scikit-learn
`VotingClassifier` (Logistic Regression + SVM) over flattened 200×200 grayscale pixels,
with a small Flask web GUI.

## Project layout

```
cancdee.ipynb        Training notebook -> produces CModel.pkl
predict.py           CLI prediction:  python predict.py <image.jpg>
GUI/UI.py            Flask web app (loads CModel.pkl next to it)
GUI/templates/       index.html upload form
GUI/static/          script.js + styles
```

## Setup

```bash
pip install -r requirements.txt
```

## 1. Train the model

The dataset is **not included**. Provide these folders next to `cancdee.ipynb`:

```
train/Normal/         normal images
train/Lung cancer/    cancer images
Testing/Normal/       (optional) images for the eval/visualization cells
Testing/Lung cancer/
```

Run all cells in `cancdee.ipynb`. It writes **`CModel.pkl`** to the repo root.

## 2. CLI prediction

```bash
python predict.py path/to/image.jpg
```

`predict.py` loads `CModel.pkl` from the repo root.

## 3. Web app

Copy the trained model into the `GUI/` folder, then run the server:

```bash
cp CModel.pkl GUI/CModel.pkl
python GUI/UI.py
```

Open http://127.0.0.1:5000, upload an image, and click **Submit**.

To enable Flask's debugger during local development (off by default for safety):

```bash
FLASK_DEBUG=1 python GUI/UI.py
```

## Notes / known limitations

- Model files (`*.pkl`) and the dataset are not committed — regenerate with the notebook.
- The classifier uses **hard voting** with two estimators; on a tie it favors *Normal*, which
  can hide false negatives. For clinical-style use, switch to `voting='soft'` with
  `SVC(probability=True)` and surface a confidence score (requires retraining).
- This is an educational project, not a medical device.
