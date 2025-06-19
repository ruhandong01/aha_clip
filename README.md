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
2. Voice Generation: generate a voice-over based on user input text or enriched user input text.
3. Voice-Photo Match: auto-match voice-over and photos and make it a video. 

# Local Test Set Up

## 1. Start Python Web Server
Run the following command in your terminal from the project root directory: 
```python
python server.py
```


## 2. Right click and select inspect to check the browse output
