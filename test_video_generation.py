#!/usr/bin/env python3
"""
Test script for video generation functionality
"""

import requests
import json
import base64
from PIL import Image
import io

def create_test_image():
    """Create a simple test image"""
    # Create a simple colored image
    img = Image.new('RGB', (1024, 1024), color='red')
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str

def test_video_generation():
    """Test the video generation endpoint"""
    print("Testing video generation functionality...")
    
    # Create test content
    test_content = [
        {
            "text": "This is the first scene of our test video.",
            "image": create_test_image(),
            "audio_url": None
        },
        {
            "text": "This is the second scene with a different color.",
            "image": create_test_image(),
            "audio_url": None
        }
    ]
    
    # Test the endpoint
    try:
        response = requests.post(
            'http://localhost:5001/save-to-video',
            json={'content_items': test_content},
            timeout=60  # 60 second timeout for video generation
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Video generation successful!")
                print(f"Video URL: {data.get('video_url')}")
                print(f"Video filename: {data.get('video_filename')}")
                return True
            else:
                print(f"❌ Video generation failed: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:5001")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Video generation may be taking too long.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Video Generation Test")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5001/', timeout=5)
        print("✅ Server is running")
    except:
        print("❌ Server is not running. Please start the server first:")
        print("   python server.py")
        exit(1)
    
    # Run the test
    success = test_video_generation()
    
    if success:
        print("\n🎉 Video generation test completed successfully!")
    else:
        print("\n💥 Video generation test failed!")
        exit(1) 