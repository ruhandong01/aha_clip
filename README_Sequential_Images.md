# Sequential Image Generation

This document describes the new sequential image generation functionality that allows you to create a series of related images where each new image builds upon the previous one.

## Overview

The sequential image generation system maintains consistency across multiple images by:
- Storing the previous image as a reference
- Using enhanced prompts that reference the previous image
- Maintaining session state to track the image sequence
- Ensuring visual consistency in style, color palette, and character designs

## API Endpoints

### 1. Start Image Sequence
**Endpoint:** `POST /start-image-sequence`

**Purpose:** Initialize a new image sequence session and generate the first image.

**Request Body:**
```json
{
    "prompt": "A cute robot exploring a colorful garden"
}
```

**Response:**
```json
{
    "success": true,
    "session_id": "uuid-string",
    "image": "base64-encoded-image-data",
    "image_count": 1
}
```

### 2. Generate Sequential Image
**Endpoint:** `POST /generate-sequential-image`

**Purpose:** Generate the next image in the sequence based on the previous image.

**Request Body:**
```json
{
    "session_id": "uuid-string",
    "prompt": "The robot discovers a mysterious door in the garden"
}
```

**Response:**
```json
{
    "success": true,
    "image": "base64-encoded-image-data",
    "image_count": 2
}
```

### 3. Get Session Information
**Endpoint:** `POST /get-session-info`

**Purpose:** Retrieve information about an active image session.

**Request Body:**
```json
{
    "session_id": "uuid-string"
}
```

**Response:**
```json
{
    "success": true,
    "image_count": 3,
    "initial_prompt": "A cute robot exploring a colorful garden"
}
```

### 4. End Image Sequence
**Endpoint:** `POST /end-image-sequence`

**Purpose:** Clean up and end an image sequence session.

**Request Body:**
```json
{
    "session_id": "uuid-string"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Session ended successfully"
}
```

## Usage Example

Here's a complete example of how to use the sequential image generation:

```python
import requests

# 1. Start a new sequence
start_response = requests.post("http://localhost:5001/start-image-sequence", 
                             json={"prompt": "A cute robot exploring a colorful garden"})
session_data = start_response.json()
session_id = session_data['session_id']

# 2. Generate the second image
seq_response = requests.post("http://localhost:5001/generate-sequential-image", 
                           json={
                               "session_id": session_id,
                               "prompt": "The robot discovers a mysterious door in the garden"
                           })

# 3. Generate the third image
seq_response2 = requests.post("http://localhost:5001/generate-sequential-image", 
                            json={
                                "session_id": session_id,
                                "prompt": "The robot opens the door and sees a magical library inside"
                            })

# 4. Get session info
info_response = requests.post("http://localhost:5001/get-session-info", 
                            json={"session_id": session_id})

# 5. End the session
end_response = requests.post("http://localhost:5001/end-image-sequence", 
                           json={"session_id": session_id})
```

## Key Features

### Visual Consistency
- Each sequential image maintains the same art style as the previous image
- Color palettes and character designs are preserved across the sequence
- The system uses enhanced prompts that explicitly reference the previous image

### Session Management
- Each sequence has a unique session ID
- Sessions track the current image, image count, and initial prompt
- Sessions can be ended to free up memory

### Backward Compatibility
- The original `/generate-image` endpoint is still available for standalone images
- Existing code will continue to work without modification

## Technical Details

### Prompt Enhancement
The system automatically enhances prompts for sequential images by adding context about the previous image:

```
"Create a comic style illustration that continues from the previous image. 
New scene: {user_prompt}. Maintain the same art style, color palette, and 
character designs as the previous image. Make it vibrant and cartoon-like 
with clear outlines and stylized features."
```

### Session Storage
Sessions are stored in memory using a global dictionary:
```python
image_sessions = {
    "session_id": {
        "current_image": "base64_data",
        "image_count": 3,
        "initial_prompt": "original_prompt"
    }
}
```

### Error Handling
- Invalid session IDs return appropriate error messages
- Missing session IDs are handled gracefully
- All endpoints include comprehensive error logging

## Testing

Use the provided `test_sequential_images.py` script to test the functionality:

```bash
python test_sequential_images.py
```

This script will:
1. Start a new image sequence
2. Generate multiple sequential images
3. Retrieve session information
4. End the session
5. Save all generated images to a `generated_images` folder

## Requirements

- Flask server running on port 5001
- OpenAI API key configured
- PIL (Pillow) for image processing (in test script)
- requests library for HTTP calls (in test script) 