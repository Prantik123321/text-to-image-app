from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Your OpenRouter API key
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', "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")

# Available models
MODELS = {
    "riverflow": {
        "name": "sourceful/riverflow-v2-fast-preview",
        "display": "Riverflow V2 (Fast)",
        "description": "Fast image generation"
    },
    "seedream": {
        "name": "bytedance-seed/seedream-4.5",
        "display": "Seedream 4.5",
        "description": "High quality image generation"
    }
}

# Mask API key for logging
if OPENROUTER_API_KEY:
    masked_key = OPENROUTER_API_KEY[:10] + "..." + OPENROUTER_API_KEY[-5:]
    logger.info(f"Using API key: {masked_key}")
else:
    logger.error("No API key found!")

@app.route('/')
def index():
    return render_template('index.html', models=MODELS)

@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        model_key = data.get('model', 'riverflow')  # Default to riverflow
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        # Get model name
        model = MODELS.get(model_key, MODELS['riverflow'])
        model_name = model['name']
        
        logger.info(f"Generating image with model {model_name} for prompt: {prompt[:50]}...")

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": request.host_url.rstrip('/'),
            "X-Title": "AI Image Generator"
        }

        # Prepare request body
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "modalities": ["image"]
        }

        # Make the request to OpenRouter
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120  # Increased timeout for image generation
        )

        logger.info(f"OpenRouter API response status: {response.status_code}")

        # Handle error responses
        if response.status_code != 200:
            error_detail = response.text
            logger.error(f"API Error {response.status_code}: {error_detail}")
            
            try:
                error_json = response.json()
                error_message = error_json.get('error', {}).get('message', 'Unknown error')
            except:
                error_message = error_detail[:200]
            
            return jsonify({
                'error': f'API Error {response.status_code}: {error_message}',
                'success': False
            }), response.status_code

        # Parse successful response
        result = response.json()
        
        # Extract the generated image
        if result.get("choices"):
            message = result["choices"][0]["message"]
            if message.get("images") and len(message["images"]) > 0:
                image_data = message["images"][0]
                
                # Handle different image response formats
                if "image_url" in image_data and "url" in image_data["image_url"]:
                    image_url = image_data["image_url"]["url"]
                    logger.info("Successfully generated image")
                    return jsonify({'image_url': image_url, 'success': True})
                elif "image" in image_data:
                    image_url = image_data["image"]
                    logger.info("Successfully generated image (base64)")
                    return jsonify({'image_url': image_url, 'success': True})
        
        logger.error("No image found in the response")
        return jsonify({'error': 'No image generated in response', 'success': False}), 500

    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        return jsonify({'error': 'Request timeout - please try again', 'success': False}), 504
    except requests.exceptions.ConnectionError:
        logger.error("Connection error")
        return jsonify({'error': 'Connection error - please check your internet', 'success': False}), 503
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}', 'success': False}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)