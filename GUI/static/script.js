(function () {
    "use strict";

    const MAX_BYTES = 10 * 1024 * 1024; // keep in sync with UI.py MAX_CONTENT_LENGTH

    const form = document.getElementById("imageForm");
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const emptyView = dropZone.querySelector(".dropzone-empty");
    const previewView = dropZone.querySelector(".dropzone-preview");
    const previewImg = document.getElementById("previewImg");
    const fileName = document.getElementById("fileName");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const btnLabel = analyzeBtn.querySelector(".btn-label");
    const spinner = analyzeBtn.querySelector(".spinner");
    const resetBtn = document.getElementById("resetBtn");
    const errorMsg = document.getElementById("errorMsg");
    const placeholder = document.getElementById("resultPlaceholder");
    const resultContent = document.getElementById("resultContent");
    const resultBadge = document.getElementById("resultBadge");
    const resultLabel = document.getElementById("resultLabel");
    const resultDetail = document.getElementById("resultDetail");

    let selectedFile = null;

    function showError(message) {
        errorMsg.textContent = message;
        errorMsg.hidden = false;
    }

    function clearError() {
        errorMsg.hidden = true;
        errorMsg.textContent = "";
    }

    function resetResult() {
        placeholder.hidden = false;
        resultContent.hidden = true;
    }

    function selectFile(file) {
        clearError();
        resetResult();

        if (!file) return;
        if (!file.type.startsWith("image/")) {
            showError("Please choose an image file (PNG, JPG, etc.).");
            return;
        }
        if (file.size > MAX_BYTES) {
            showError("That image is larger than 10 MB. Please choose a smaller file.");
            return;
        }

        selectedFile = file;
        fileName.textContent = file.name;
        previewImg.src = URL.createObjectURL(file);
        emptyView.hidden = true;
        previewView.hidden = false;
        analyzeBtn.disabled = false;
        resetBtn.hidden = false;
    }

    function resetAll() {
        selectedFile = null;
        form.reset();
        if (previewImg.src) URL.revokeObjectURL(previewImg.src);
        previewImg.removeAttribute("src");
        emptyView.hidden = false;
        previewView.hidden = true;
        analyzeBtn.disabled = true;
        resetBtn.hidden = true;
        clearError();
        resetResult();
    }

    function setLoading(loading) {
        analyzeBtn.disabled = loading || !selectedFile;
        spinner.hidden = !loading;
        btnLabel.textContent = loading ? "Analyzing…" : "Analyze scan";
    }

    function renderResult(data) {
        const isCancer = data.is_cancer;
        resultBadge.classList.toggle("is-cancer", isCancer);
        resultBadge.classList.toggle("is-safe", !isCancer);
        resultLabel.textContent = data.label;
        resultDetail.textContent = isCancer
            ? "The model flagged possible signs of lung cancer in this scan. This is not a diagnosis — please consult a radiologist for confirmation."
            : "The model did not detect signs of lung cancer in this scan. Continue routine screening as advised by your clinician.";
        placeholder.hidden = true;
        resultContent.hidden = false;
    }

    // ---- File input & drag-and-drop ----
    fileInput.addEventListener("change", function () {
        selectFile(fileInput.files[0]);
    });

    ["dragenter", "dragover"].forEach(function (evt) {
        dropZone.addEventListener(evt, function (e) {
            e.preventDefault();
            dropZone.classList.add("dragover");
        });
    });
    ["dragleave", "drop"].forEach(function (evt) {
        dropZone.addEventListener(evt, function (e) {
            e.preventDefault();
            dropZone.classList.remove("dragover");
        });
    });
    dropZone.addEventListener("drop", function (e) {
        const file = e.dataTransfer.files && e.dataTransfer.files[0];
        if (file) {
            fileInput.files = e.dataTransfer.files;
            selectFile(file);
        }
    });
    // Keyboard access: Enter/Space opens the file picker.
    dropZone.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            fileInput.click();
        }
    });

    resetBtn.addEventListener("click", resetAll);

    // ---- Submit ----
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        if (!selectedFile) return;

        clearError();
        setLoading(true);

        const formData = new FormData();
        formData.append("file", selectedFile);

        fetch("/classify", { method: "POST", body: formData })
            .then(function (response) {
                return response.json().then(function (body) {
                    return { ok: response.ok, body: body };
                });
            })
            .then(function (result) {
                if (!result.ok) {
                    throw new Error(result.body.error || "Classification failed.");
                }
                renderResult(result.body);
            })
            .catch(function (err) {
                showError(err.message || "Something went wrong. Please try again.");
                resetResult();
            })
            .finally(function () {
                setLoading(false);
            });
    });
})();
