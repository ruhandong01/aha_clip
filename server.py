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
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_url_path='')
CORS(app)  # Enable CORS for all routes

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'production')
app.config.from_object(config[config_name])

# Configure OpenAI API from environment variable
openai.api_key = app.config.get('OPENAI_API_KEY')
if not openai.api_key:
    logger.error("OPENAI_API_KEY not found in environment variables")

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

@app.route('/save-to-video', methods=['POST'])
def save_to_video():
    """Generate a video from the provided content (images, text, and audio)"""
    try:
        data = request.json
        content_items = data.get('content_items', [])
        
        if not content_items:
            return jsonify({
                'success': False,
                'error': 'No content items provided'
            }), 400
        
        logger.info(f"Generating video from {len(content_items)} content items")
        
        # Create a unique filename for the video
        video_id = str(uuid.uuid4())
        video_filename = f"video_{video_id}.mp4"
        video_path = os.path.join('static', 'videos', video_filename)
        
        # Ensure the videos directory exists
        os.makedirs(os.path.dirname(video_path), exist_ok=True)
        
        video_clips = []
        temp_files = []  # Track temporary files for cleanup
        
        try:
            for i, item in enumerate(content_items):
                try:
                    # Extract data from the item
                    image_data = item.get('image', '')
                    text = item.get('text', '')
                    audio_url = item.get('audio_url', '')
                    
                    if not image_data:
                        logger.warning(f"No image data for item {i}")
                        continue
                    
                    # Decode base64 image
                    try:
                        image_bytes = base64.b64decode(image_data)
                        image = Image.open(BytesIO(image_bytes))
                    except Exception as decode_error:
                        logger.error(f"Error decoding image for item {i}: {decode_error}")
                        continue
                    
                    # Resize image to standard video dimensions (16:9 aspect ratio)
                    target_width = 1920
                    target_height = 1080
                    image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    
                    # Save image to temporary file
                    temp_image_path = os.path.join(tempfile.gettempdir(), f"temp_image_{video_id}_{i}.png")
                    image.save(temp_image_path)
                    temp_files.append(temp_image_path)
                    
                    # Create image clip
                    image_clip = ImageClip(temp_image_path, duration=5)  # 5 seconds per image
                    
                    # Add text overlay if text is provided
                    if text.strip():
                        try:
                            # Create text clip
                            text_clip = TextClip(
                                text, 
                                fontsize=60, 
                                color='white',
                                font='Arial-Bold',
                                stroke_color='black',
                                stroke_width=2
                            ).set_position(('center', 'bottom')).set_duration(5)
                            
                            # Composite image and text
                            composite_clip = CompositeVideoClip([image_clip, text_clip])
                            video_clips.append(composite_clip)
                        except Exception as text_error:
                            logger.warning(f"Error creating text overlay for item {i}: {text_error}")
                            # Use image clip without text if text creation fails
                            video_clips.append(image_clip)
                    else:
                        video_clips.append(image_clip)
                    
                    # Add audio if available
                    if audio_url:
                        try:
                            # Extract audio file path from URL
                            audio_filename = audio_url.split('/')[-1]
                            audio_path = os.path.join('static', 'audio', audio_filename)
                            
                            logger.info(f"Processing audio for item {i}: {audio_path}")
                            
                            if os.path.exists(audio_path):
                                logger.info(f"Audio file exists: {audio_path}")
                                audio_clip = AudioFileClip(audio_path)
                                
                                # Get the actual duration of the audio
                                audio_duration = audio_clip.duration
                                video_duration = 5  # 5 seconds per video clip
                                
                                logger.info(f"Audio duration: {audio_duration}s, Video duration: {video_duration}s")
                                
                                # If audio is shorter than video, loop it or extend with silence
                                if audio_duration < video_duration:
                                    # Option 1: Loop the audio to fill the video duration
                                    loops_needed = int(video_duration / audio_duration) + 1
                                    audio_clip = audio_clip.loop(loops_needed)
                                    # Trim to exact video duration
                                    audio_clip = audio_clip.subclip(0, video_duration)
                                    logger.info(f"Looped audio {loops_needed} times to fill {video_duration}s")
                                elif audio_duration > video_duration:
                                    # If audio is longer, trim it to video duration
                                    audio_clip = audio_clip.subclip(0, video_duration)
                                    logger.info(f"Trimmed audio from {audio_duration}s to {video_duration}s")
                                # If they're equal, no change needed
                                
                                video_clips[-1] = video_clips[-1].set_audio(audio_clip)
                                logger.info(f"Successfully added audio to video clip {i}")
                            else:
                                logger.warning(f"Audio file not found: {audio_path}")
                        except Exception as audio_error:
                            logger.warning(f"Could not add audio for item {i}: {audio_error}")
                    else:
                        logger.info(f"No audio URL provided for item {i}")
                    
                except Exception as item_error:
                    logger.error(f"Error processing item {i}: {item_error}")
                    continue
            
            if not video_clips:
                return jsonify({
                    'success': False,
                    'error': 'No valid content items to create video'
                }), 400
            
            # Concatenate all video clips
            logger.info(f"Concatenating {len(video_clips)} video clips")
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Write the final video
            logger.info(f"Writing video to {video_path}")
            final_video.write_videofile(
                video_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None  # Suppress MoviePy's verbose output
            )
            
            logger.info(f"Successfully generated video: {video_filename}")
            
            return jsonify({
                'success': True,
                'video_url': f'/static/videos/{video_filename}',
                'video_filename': video_filename
            })
            
        finally:
            # Clean up video clips to free memory
            for clip in video_clips:
                try:
                    clip.close()
                except:
                    pass
            
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
        
    except Exception as e:
        logger.error(f"Error generating video: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/static/videos/<filename>')
def serve_video(filename):
    """Serve video files"""
    return send_from_directory('static/videos', filename)

@app.route('/debug/audio-files', methods=['GET'])
def debug_audio_files():
    """Debug endpoint to list available audio files"""
    try:
        audio_dir = os.path.join('static', 'audio')
        if not os.path.exists(audio_dir):
            return jsonify({
                'success': False,
                'error': 'Audio directory does not exist',
                'audio_dir': audio_dir
            })
        
        audio_files = []
        for filename in os.listdir(audio_dir):
            if filename.endswith('.mp3'):
                file_path = os.path.join(audio_dir, filename)
                file_size = os.path.getsize(file_path)
                audio_files.append({
                    'filename': filename,
                    'url': f'/static/audio/{filename}',
                    'size_bytes': file_size,
                    'size_mb': round(file_size / (1024 * 1024), 2)
                })
        
        return jsonify({
            'success': True,
            'audio_dir': audio_dir,
            'audio_files': audio_files,
            'count': len(audio_files)
        })
        
    except Exception as e:
        logger.error(f"Error listing audio files: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 