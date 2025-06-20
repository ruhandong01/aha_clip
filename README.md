# aha_clip
make your idea into real editable video

# Production Workflow Design
## Front Page
We have a text input box in the html page to allow users to input their story ideas

# Technical Function Module
1. Sentence Generation: according to the user prompt, we generate story of 6 sentence.
Requirement: The sentence output should be editable by users.
2. Image Generation: after we finished the sentence generation, we generate image for each sentence. In our first use case, generate 6 image out of 6 sentence using openai API.
Requirement: Users can upload their own photo to replace the output photo.
3. Voice Generation: generate a voice-over based on user input text or enriched user input text.
Requirement: for each sentence and image, generate voice based on user text and automatically play it. 
4. Save to Video: One click function to save generated text / image / voice to video.
Requirements: One button to save generated text / image / voice to video. The video will be generated in MP4 format with 1920x1080 resolution, 5 seconds per scene, and include text overlays and audio narration.

# Local Test Set Up

## 1. Install Dependencies
First, install the required Python packages:
```bash
pip install -r requirements.txt
```

## 2. Start Python Web Server
Run the following command in your terminal from the project root directory: 
```python
python server.py
```

## 3. Access the Application
Open your web browser and navigate to `http://localhost:5001`

## 4. Using the Save to Video Feature
1. Enter your story idea in the text input box
2. Click "Generate Video" to create sentences and images
3. Optionally click the 🔊 button next to each sentence to generate voice narration
4. Click the "🎬 Save to Video" button to create a complete video
5. The video will be generated and a download link will appear
6. Click the download link to save your video

## 5. Testing the Video Generation
You can test the video generation functionality using the provided test scripts:

### Quick Test
```bash
python test_video_generation.py
```

### Full Demo
```bash
python demo_video_generation.py
```

## 6. Right click and select inspect to check the browse output
