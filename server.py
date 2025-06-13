from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import openai
import os

app = Flask(__name__, static_url_path='')
CORS(app)  # Enable CORS for all routes

# Configure OpenAI API
openai.api_key = "sk-wzBKfeSRP4DVg91zYCvnK16Xcj89fslocgophqpsOHT3BlbkFJhXmv_ypqhqVTzPizZgsb7bK5GQQu9UGblIrpEiJ1IA"

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
        sentences = [s.strip() for s in generated_text.split('\n') if s.strip()]

        return jsonify({
            'success': True,
            'sentences': sentences
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 