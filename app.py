from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import json
import base64
from io import BytesIO

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Your OpenRouter API key
OPENROUTER_API_KEY = "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"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        # Prepare the request to OpenRouter
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "sourceful/riverflow-v2-pro",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "modalities": ["image"]
            }
        )

        result = response.json()
        
        # Extract the generated image
        if result.get("choices"):
            message = result["choices"][0]["message"]
            if message.get("images"):
                # Return the first image URL
                image_url = message["images"][0]["image_url"]["url"]
                return jsonify({'image_url': image_url, 'success': True})
        
        return jsonify({'error': 'No image generated', 'success': False}), 500

    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)