document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const preview = document.getElementById('preview');
    const uploadText = document.getElementById('uploadText');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultSection = document.querySelector('.result-section');
    const prediction = document.getElementById('prediction');
    const confidenceBar = document.getElementById('confidenceBar');
    const confidenceText = document.getElementById('confidenceText');

    // Handle drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#2ecc71';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#3498db';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#3498db';
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    // Handle click upload
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFile(file);
    });

    function handleFile(file) {
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
                uploadText.style.display = 'none';
                analyzeBtn.disabled = false;
            }
            reader.readAsDataURL(file);
        }
    }

    // Handle analysis
    analyzeBtn.addEventListener('click', async () => {
        const formData = new FormData();
        formData.append('image', fileInput.files[0]);

        try {
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = 'Analyzing...';

            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            resultSection.style.display = 'block';
            prediction.textContent = `Prediction: ${result.prediction}`;
            confidenceBar.style.width = `${result.confidence}%`;
            confidenceText.textContent = `Confidence: ${result.confidence}%`;

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during analysis');
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Analyze Image';
        }
    });
}); 