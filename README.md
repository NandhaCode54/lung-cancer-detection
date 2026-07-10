# Lung Cancer Detection

Classifies lung images as **Normal** or **Lung cancer** using a scikit-learn
`VotingClassifier` (Logistic Regression + SVM) over flattened 200×200 grayscale pixels.
Ships with a CLI and a clean Flask web dashboard.

## Project layout

```
classifier.py        Shared model loading + preprocessing (used by CLI and web app)
predict.py           CLI prediction:  python predict.py <image.jpg> [more images...]
cancdee.ipynb        Training notebook -> produces CModel.pkl
GUI/UI.py            Flask web app (JSON API + dashboard)
GUI/templates/       index.html dashboard
GUI/static/          script.js (drag-drop upload) + styles
```

All inference goes through **`classifier.py`**, so the CLI and web app always behave
identically. The model file `CModel.pkl` is located automatically from (in order):

1. the `CMODEL_PATH` environment variable,
2. the repo root (`./CModel.pkl`),
3. `GUI/CModel.pkl`.

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

Run all cells in `cancdee.ipynb`. It writes **`CModel.pkl`** to the repo root and prints
test accuracy, a classification report, and a confusion matrix.

## 2. CLI prediction

```bash
python predict.py path/to/image.jpg
python predict.py img1.png img2.png img3.png   # multiple images
```

## 3. Web app

```bash
python GUI/UI.py
```

Open http://127.0.0.1:5000, drag in (or browse to) an image, and click **Analyze scan**.
The result appears as a color-coded card — green for *Normal*, red for *Lung cancer*.

Endpoints:

| Method | Path        | Description                                            |
|--------|-------------|--------------------------------------------------------|
| GET    | `/`         | Dashboard UI                                           |
| GET    | `/health`   | Readiness probe (also confirms the model loads)        |
| POST   | `/classify` | `multipart/form-data` with a `file` field; returns JSON |

`/classify` returns e.g. `{"label": "Normal", "is_cancer": false, "confidence": null}`.
Uploads are limited to 10 MB and must be an image type.

To enable Flask's debugger during local development (off by default for safety):

```bash
FLASK_DEBUG=1 python GUI/UI.py
```

## Notes / known limitations

- Model files (`*.pkl`) and the dataset are not committed — regenerate with the notebook.
- The classifier uses **hard voting**, so it outputs a label only (no probability). `confidence`
  is always `null`. For a confidence score, retrain with `voting='soft'` and
  `SVC(probability=True)`.
- On a voting tie the ensemble favors *Normal*, which can hide false negatives.
- If you see a scikit-learn `InconsistentVersionWarning`, the `.pkl` was trained with a
  different scikit-learn version than the one installed — retrain the model, or pin the
  training version, to silence it.
- This is an educational project, **not a medical device**.
```
