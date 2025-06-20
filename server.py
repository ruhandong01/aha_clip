from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import openai
import os
import base64
from io import BytesIO
import logging
import re
from gtts import gTTS
import tempfile
import uuid
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_url_path='')
CORS(app)  # Enable CORS for all routes

# Configure OpenAI API
openai.api_key = "your_api_key"

# Global storage for image sessions
image_sessions = {}

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/start-image-sequence', methods=['POST'])
def start_image_sequence():
    """Start a new image sequence session"""
    try:
        data = request.json
        initial_prompt = data.get('prompt', '')
        logger.info(f"Starting new image sequence with prompt: {initial_prompt}")
        
        # Generate the first image
        enhanced_prompt = f"Create a comic style illustration of: {initial_prompt}. Make it vibrant and cartoon-like with clear outlines and stylized features."
        response = openai.Image.create(
            model="dall-e-3",
            prompt=enhanced_prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json",
            quality="standard"
        )
        
        image_data = response['data'][0]['b64_json']
        
        # Create a new session
        session_id = str(uuid.uuid4())
        image_sessions[session_id] = {
            'current_image': image_data,
            'image_count': 1,
            'initial_prompt': initial_prompt
        }
        
        logger.info(f"Created new image session: {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'image': image_data,
            'image_count': 1
        })
        
    except Exception as e:
        logger.error(f"Error starting image sequence: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate-sequential-image', methods=['POST'])
def generate_sequential_image():
    """Generate the next image in a sequence based on the previous image"""
    try:
        data = request.json
        session_id = data.get('session_id', '')
        new_prompt = data.get('prompt', '')
        
        if not session_id or session_id not in image_sessions:
            return jsonify({
                'success': False,
                'error': 'Invalid or missing session ID'
            }), 400
            
        session = image_sessions[session_id]
        previous_image = session['current_image']
        
        logger.info(f"Generating sequential image for session {session_id} with prompt: {new_prompt}")
        
        # Create a prompt that references the previous image
        enhanced_prompt = f"Create a comic style illustration that continues from the previous image. New scene: {new_prompt}. Maintain the same art style, color palette, and character designs as the previous image. Make it vibrant and cartoon-like with clear outlines and stylized features."
        
        # Use the previous image as a reference
        response = openai.Image.create(
            model="dall-e-3",
            prompt=enhanced_prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json",
            quality="standard"
        )
        
        new_image_data = response['data'][0]['b64_json']
        
        # Update the session with the new image
        session['current_image'] = new_image_data
        session['image_count'] += 1
        
        logger.info(f"Successfully generated sequential image for session {session_id}")
        
        return jsonify({
            'success': True,
            'image': new_image_data,
            'image_count': session['image_count']
        })
        
    except Exception as e:
        logger.error(f"Error generating sequential image: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/get-session-info', methods=['POST'])
def get_session_info():
    """Get information about an image session"""
    try:
        data = request.json
        session_id = data.get('session_id', '')
        
        if not session_id or session_id not in image_sessions:
            return jsonify({
                'success': False,
                'error': 'Invalid or missing session ID'
            }), 400
            
        session = image_sessions[session_id]
        
        return jsonify({
            'success': True,
            'image_count': session['image_count'],
            'initial_prompt': session['initial_prompt']
        })
        
    except Exception as e:
        logger.error(f"Error getting session info: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/end-image-sequence', methods=['POST'])
def end_image_sequence():
    """End an image sequence session"""
    try:
        data = request.json
        session_id = data.get('session_id', '')
        
        if session_id in image_sessions:
            del image_sessions[session_id]
            logger.info(f"Ended image session: {session_id}")
            
        return jsonify({
            'success': True,
            'message': 'Session ended successfully'
        })
        
    except Exception as e:
        logger.error(f"Error ending image sequence: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate-sentences', methods=['POST'])
def generate_sentences():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        logger.info(f"Generating sentences for prompt: {prompt}")

        response = openai.ChatCompletion.create(
            model="gpt-4o",
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
    """
    Original image generation endpoint (maintained for backward compatibility).
    For sequential image generation, use /start-image-sequence and /generate-sequential-image instead.
    """
    try:
        data = request.json
        prompt = data.get('prompt', '')
        logger.info(f"Generating standalone image for prompt: {prompt}")
        prompt = f"Create a comic style illustration of: {prompt}. Make it vibrant and cartoon-like with clear outlines and stylized features."
        response = openai.Image.create(
            model="dall-e-3",  # Use DALL-E 3 model
            prompt=prompt,
            n=1,
            size="1024x1024",  # DALL-E 3 supports higher resolution
            response_format="b64_json",
            quality="standard"  # Can be "standard" or "hd" for higher quality
        )

        image_data = response['data'][0]['b64_json']
        logger.info(f"Successfully generated standalone image for prompt: {prompt}")
        
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

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)

@app.route('/generate-voice', methods=['POST'])
def generate_voice():
    try:
        data = request.json
        text = data.get('text', '')
        logger.info(f"Generating voice for text: {text}")

        if not text.strip():
            return jsonify({
                'success': False,
                'error': 'Text is required for voice generation'
            }), 400

        # Create a unique filename for the audio
        audio_id = str(uuid.uuid4())
        audio_filename = f"audio_{audio_id}.mp3"
        audio_path = os.path.join('static', 'audio', audio_filename)
        
        # Ensure the audio directory exists
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)

        # Generate speech using gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(audio_path)
        
        logger.info(f"Successfully generated voice file: {audio_filename}")
        
        return jsonify({
            'success': True,
            'audio_url': f'/static/audio/{audio_filename}'
        })

    except Exception as e:
        logger.error(f"Error generating voice: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 