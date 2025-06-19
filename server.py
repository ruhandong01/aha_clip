from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import openai
import os
import base64
from io import BytesIO
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_url_path='')
CORS(app)  # Enable CORS for all routes

# Configure OpenAI API
openai.api_key = "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"

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/generate-sentences', methods=['POST'])
def generate_sentences():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        logger.info(f"Generating sentences for prompt: {prompt}")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative storyteller. Generate 6 independent, engaging sentences based on the given prompt. Each sentence should be complete and meaningful on its own."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=150
        )

        generated_text = response.choices[0].message.content
        # Split sentences while preserving numbered lists
        sentences = re.split(r'(?<!\d)\.(?!\d)', generated_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentences = sentences[:6]  # Always return at most 6
        while len(sentences) < 6:
            sentences.append('')  # Pad to 6 if needed
        logger.info(f"Generated {len(sentences)} sentences: {sentences}")

        return jsonify({
            'success': True,
            'sentences': sentences
        })

    except Exception as e:
        logger.error(f"Error generating sentences: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        logger.info(f"Generating image for prompt: {prompt}")

        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512",
            response_format="b64_json"
        )

        image_data = response['data'][0]['b64_json']
        logger.info(f"Successfully generated image for prompt: {prompt}")
        
        return jsonify({
            'success': True,
            'image': image_data
        })

    except Exception as e:
        logger.error(f"Error generating image: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 