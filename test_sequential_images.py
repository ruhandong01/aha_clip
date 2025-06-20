#!/usr/bin/env python3
"""
Test script for sequential image generation functionality.
This script demonstrates how to use the new sequential image generation endpoints.
"""

import requests
import json
import base64
from PIL import Image
import io
import os

# Server configuration
BASE_URL = "http://localhost:5001"

def save_image_from_base64(image_data, filename):
    """Save a base64 encoded image to a file"""
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Create images directory if it doesn't exist
        os.makedirs('generated_images', exist_ok=True)
        
        # Save image
        filepath = os.path.join('generated_images', filename)
        image.save(filepath)
        print(f"Saved image: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

def test_sequential_image_generation():
    """Test the sequential image generation functionality"""
    
    print("=== Testing Sequential Image Generation ===\n")
    
    # Step 1: Start a new image sequence
    print("1. Starting new image sequence...")
    start_response = requests.post(f"{BASE_URL}/start-image-sequence", 
                                 json={"prompt": "A cute robot exploring a colorful garden"})
    
    if start_response.status_code != 200:
        print(f"Error starting sequence: {start_response.text}")
        return
    
    start_data = start_response.json()
    session_id = start_data['session_id']
    print(f"Session ID: {session_id}")
    print(f"Initial image generated (count: {start_data['image_count']})")
    
    # Save the first image
    save_image_from_base64(start_data['image'], f"sequence_1_initial.png")
    
    # Step 2: Generate the second image in the sequence
    print("\n2. Generating second image in sequence...")
    seq_response = requests.post(f"{BASE_URL}/generate-sequential-image", 
                               json={
                                   "session_id": session_id,
                                   "prompt": "The robot discovers a mysterious door in the garden"
                               })
    
    if seq_response.status_code != 200:
        print(f"Error generating sequential image: {seq_response.text}")
        return
    
    seq_data = seq_response.json()
    print(f"Second image generated (count: {seq_data['image_count']})")
    
    # Save the second image
    save_image_from_base64(seq_data['image'], f"sequence_2_door.png")
    
    # Step 3: Generate the third image in the sequence
    print("\n3. Generating third image in sequence...")
    seq_response2 = requests.post(f"{BASE_URL}/generate-sequential-image", 
                                json={
                                    "session_id": session_id,
                                    "prompt": "The robot opens the door and sees a magical library inside"
                                })
    
    if seq_response2.status_code != 200:
        print(f"Error generating sequential image: {seq_response2.text}")
        return
    
    seq_data2 = seq_response2.json()
    print(f"Third image generated (count: {seq_data2['image_count']})")
    
    # Save the third image
    save_image_from_base64(seq_data2['image'], f"sequence_3_library.png")
    
    # Step 4: Get session information
    print("\n4. Getting session information...")
    info_response = requests.post(f"{BASE_URL}/get-session-info", 
                                json={"session_id": session_id})
    
    if info_response.status_code == 200:
        info_data = info_response.json()
        print(f"Session info - Total images: {info_data['image_count']}")
        print(f"Initial prompt: {info_data['initial_prompt']}")
    
    # Step 5: End the session
    print("\n5. Ending session...")
    end_response = requests.post(f"{BASE_URL}/end-image-sequence", 
                               json={"session_id": session_id})
    
    if end_response.status_code == 200:
        print("Session ended successfully")
    
    print("\n=== Sequential Image Generation Test Complete ===")
    print("Check the 'generated_images' folder for the saved images.")

def test_standalone_image_generation():
    """Test the original standalone image generation for comparison"""
    
    print("\n=== Testing Standalone Image Generation ===\n")
    
    response = requests.post(f"{BASE_URL}/generate-image", 
                           json={"prompt": "A cute robot exploring a colorful garden"})
    
    if response.status_code == 200:
        data = response.json()
        print("Standalone image generated successfully")
        save_image_from_base64(data['image'], "standalone_robot.png")
    else:
        print(f"Error generating standalone image: {response.text}")

if __name__ == "__main__":
    # Test both sequential and standalone image generation
    test_sequential_image_generation()
    test_standalone_image_generation() 