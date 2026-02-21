document.addEventListener('DOMContentLoaded', function() {
    const promptInput = document.getElementById('promptInput');
    const generateBtn = document.getElementById('generateBtn');
    const imageContainer = document.getElementById('imageContainer');
    const generatedImage = document.getElementById('generatedImage');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');
    const downloadBtn = document.getElementById('downloadBtn');
    const exampleBtns = document.querySelectorAll('.example-btn');
    const btnText = generateBtn.querySelector('.btn-text');
    const loadingSpinner = generateBtn.querySelector('.loading-spinner');

    // Example buttons click handler
    exampleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            promptInput.value = this.textContent;
        });
    });

    // Generate button click handler
    generateBtn.addEventListener('click', generateImage);

    // Download button click handler
    downloadBtn.addEventListener('click', function() {
        const imageUrl = generatedImage.src;
        if (imageUrl) {
            // Create a temporary link to download the image
            const link = document.createElement('a');
            link.href = imageUrl;
            link.download = `ai-generated-image-${Date.now()}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    });

    // Enter key to generate (with Shift+Enter for new line)
    promptInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            generateImage();
        }
    });

    async function generateImage() {
        const prompt = promptInput.value.trim();
        
        if (!prompt) {
            showError('Please enter a prompt');
            return;
        }

        // Clear previous results
        hideImage();
        hideError();
        
        // Show loading state
        setLoading(true);

        try {
            const response = await fetch('/generate-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: prompt })
            });

            const data = await response.json();

            if (data.success && data.image_url) {
                // Display the generated image
                generatedImage.src = data.image_url;
                imageContainer.style.display = 'block';
                loadingIndicator.style.display = 'none';
            } else {
                showError(data.error || 'Failed to generate image');
            }
        } catch (error) {
            console.error('Error:', error);
            showError('An error occurred while generating the image');
        } finally {
            setLoading(false);
        }
    }

    function setLoading(isLoading) {
        if (isLoading) {
            generateBtn.disabled = true;
            btnText.style.display = 'none';
            loadingSpinner.style.display = 'inline';
            loadingIndicator.style.display = 'block';
            imageContainer.style.display = 'none';
        } else {
            generateBtn.disabled = false;
            btnText.style.display = 'inline';
            loadingSpinner.style.display = 'none';
            loadingIndicator.style.display = 'none';
        }
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        loadingIndicator.style.display = 'none';
    }

    function hideError() {
        errorMessage.style.display = 'none';
    }

    function hideImage() {
        imageContainer.style.display = 'none';
    }
});