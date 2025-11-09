document.addEventListener('DOMContentLoaded', () => {

    const faceInput = document.getElementById('face-input');
    const shirtInput = document.getElementById('shirt-input');
    const pantsInput = document.getElementById('pants-input');
    const shoesInput = document.getElementById('shoes-input');

    const facePreview = document.getElementById('face-preview');
    const shirtPreview = document.getElementById('shirt-preview');
    const pantsPreview = document.getElementById('pants-preview');
    const shoesPreview = document.getElementById('shoes-preview');

    const generateBtn = document.getElementById('generate-btn');
    const resultImage = document.getElementById('result-image');
    const loadingSpinner = document.getElementById('loading');

    const API_URL = 'http://127.0.0.1:8000/generate';

    function setupPreview(input, preview) {
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    preview.src = event.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }
    setupPreview(faceInput, facePreview);
    setupPreview(shirtInput, shirtPreview);
    setupPreview(pantsInput, pantsPreview);
    setupPreview(shoesInput, shoesPreview);

    generateBtn.addEventListener('click', async () => {
        // 1. Get the files
        const faceFile = faceInput.files[0];
        const shirtFile = shirtInput.files[0];
        const pantsFile = pantsInput.files[0];
        const shoesFile = shoesInput.files[0];

        if (!faceFile || !shirtFile || !pantsFile || !shoesFile) {
            alert('Please upload all four images.');
            return;
        }

        loadingSpinner.style.display = 'block';
        resultImage.src = '';
        resultImage.style.display = 'none';
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';

        const formData = new FormData();
        formData.append('face_image', faceFile);
        formData.append('shirt_image', shirtFile);
        formData.append('pants_image', pantsFile);
        formData.append('shoes_image', shoesFile);

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const imageBlob = await response.blob();
            const imageUrl = URL.createObjectURL(imageBlob);

            resultImage.src = imageUrl;
            resultImage.style.display = 'block';

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Check the console (F12) for details.');
        } finally {
            loadingSpinner.style.display = 'none';
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Outfit';
        }
    });
});
