from flask import Flask, request, jsonify, send_from_directory
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
openai.api_key = "sk-P8_ugLpBonQCPIaATxF0VTBsUfhQj0O5IxmuiFkKsMT3BlbkFJAeliIKf9Vg0QAFfhNa8jRrORY28BucjmPcHsvJpIAA"

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

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
        # Robustly split sentences, handle numbered lists, extra newlines, etc.
        sentences = re.split(r'\d+\.\s*', generated_text)
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