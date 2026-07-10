"""Shared lung-cancer image classification logic.

This module centralizes model loading and image preprocessing so that both the
CLI (``predict.py``) and the Flask web app (``GUI/UI.py``) use exactly the same
inference path. The trained model (``CModel.pkl``) is located automatically from
a few well-known locations, or via the ``CMODEL_PATH`` environment variable.
"""

import os

import cv2
import joblib

# Model input geometry — must match how the model was trained (see cancdee.ipynb).
IMG_SIZE = (200, 200)

# Numeric prediction -> human-readable label.
LABELS = {0: "Normal", 1: "Lung cancer"}

_MODEL = None  # Lazily loaded, cached model instance.


def _candidate_model_paths():
    """Return the ordered list of paths to search for ``CModel.pkl``."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.environ.get("CMODEL_PATH"),      # explicit override
        os.path.join(here, "CModel.pkl"),   # repo root (CLI / notebook output)
        os.path.join(here, "GUI", "CModel.pkl"),  # copied next to the web app
    ]
    return [p for p in candidates if p]


def find_model_path():
    """Return the first existing model path, or raise a helpful error."""
    for path in _candidate_model_paths():
        if os.path.isfile(path):
            return path
    searched = "\n  ".join(_candidate_model_paths())
    raise FileNotFoundError(
        "Could not find the trained model 'CModel.pkl'. Train it by running "
        "cancdee.ipynb, or set the CMODEL_PATH environment variable.\n"
        f"Searched:\n  {searched}"
    )


def load_model(path=None):
    """Load and cache the model. Pass ``path`` to load a specific file."""
    global _MODEL
    if path is not None:
        return joblib.load(path)
    if _MODEL is None:
        _MODEL = joblib.load(find_model_path())
    return _MODEL


def preprocess(image_path):
    """Read and normalize an image into the model's input vector.

    Returns ``None`` if the file cannot be read as an image.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    img = cv2.resize(img, IMG_SIZE)
    return img.reshape(1, -1) / 255.0


def classify_single_image(image_path, model=None):
    """Classify one image path.

    Returns the label string (``"Normal"`` / ``"Lung cancer"``), or ``None`` if
    the file is not a readable image.
    """
    features = preprocess(image_path)
    if features is None:
        return None
    model = model if model is not None else load_model()
    prediction = model.predict(features)
    return LABELS.get(int(prediction[0]), "Unknown")
