"""Flask web app for lung-cancer image classification.

Serves a single-page dashboard and a JSON classification endpoint. Inference is
delegated to the shared ``classifier`` module at the repo root so the web app
and CLI stay in lockstep.
"""

import os
import sys
import tempfile

from flask import Flask, jsonify, render_template, request

# Make the repo-root shared module importable when running from GUI/.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from classifier import classify_single_image, load_model  # noqa: E402

app = Flask(__name__)

# Reject uploads larger than 10 MB (Flask returns 413 automatically).
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def _allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    """Lightweight readiness probe that also confirms the model loads."""
    try:
        load_model()
    except Exception as exc:  # noqa: BLE001 - report any load failure
        return jsonify(status="error", detail=str(exc)), 503
    return jsonify(status="ok")


@app.route("/classify", methods=["POST"])
def classify():
    if "file" not in request.files:
        return jsonify(error="No file was uploaded."), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify(error="No file was selected."), 400

    if not _allowed_file(file.filename):
        return jsonify(error="Unsupported file type. Please upload an image."), 400

    # Save to a unique temp file, classify, then always clean up.
    suffix = os.path.splitext(file.filename)[1] or ".img"
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    try:
        file.save(temp_path)
        prediction = classify_single_image(temp_path)
    except FileNotFoundError as exc:
        # Model missing / not loadable.
        return jsonify(error=str(exc)), 503
    finally:
        os.remove(temp_path)

    if prediction is None:
        return jsonify(error="The uploaded file could not be read as an image."), 400

    is_cancer = prediction == "Lung cancer"
    return jsonify(
        label=prediction,
        is_cancer=is_cancer,
        # Model uses hard voting, so no probability is available.
        confidence=None,
    )


@app.errorhandler(413)
def too_large(_error):
    return jsonify(error="File is too large (max 10 MB)."), 413


if __name__ == "__main__":
    # Never enable the debugger by default (Werkzeug debugger allows RCE).
    debug = os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true", "yes")
    app.run(debug=debug)
