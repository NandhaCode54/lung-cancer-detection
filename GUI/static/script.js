function classifyImage() {
    var formData = new FormData();
    var fileInput = document.getElementById('fileInput');
    formData.append('file', fileInput.files[0]);

    fetch('/classify', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        document.getElementById('prediction').innerText = 'Prediction: ' + data;
    })
    .catch(error => console.error('Error:', error));
}
