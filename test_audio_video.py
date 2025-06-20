#!/usr/bin/env python3
"""
Test script to debug audio and video generation issues
"""

import requests
import json
import time

def test_audio_generation():
    """Test audio generation"""
    print("Testing audio generation...")
    
    test_text = "This is a test sentence for audio generation."
    
    try:
        response = requests.post('http://localhost:5001/generate-voice', 
                               json={'text': test_text})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                audio_url = data.get('audio_url')
                print(f"✅ Audio generated successfully: {audio_url}")
                return audio_url
            else:
                print(f"❌ Audio generation failed: {data.get('error')}")
                return None
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_audio_files():
    """Test listing audio files"""
    print("\nTesting audio files listing...")
    
    try:
        response = requests.get('http://localhost:5001/debug/audio-files')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                audio_files = data.get('audio_files', [])
                print(f"✅ Found {len(audio_files)} audio files:")
                for audio_file in audio_files:
                    print(f"   - {audio_file['filename']} ({audio_file['size_mb']} MB)")
                return audio_files
            else:
                print(f"❌ Failed to list audio files: {data.get('error')}")
                return []
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_video_with_audio():
    """Test video generation with audio"""
    print("\nTesting video generation with audio...")
    
    # First generate an audio file
    audio_url = test_audio_generation()
    if not audio_url:
        print("❌ Cannot test video with audio - no audio generated")
        return False
    
    # Create a simple test image (red square)
    import base64
    from PIL import Image
    import io
    
    img = Image.new('RGB', (1024, 1024), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    # Test content with audio
    test_content = [
        {
            "text": "This is a test video with audio narration.",
            "image": img_str,
            "audio_url": audio_url
        }
    ]
    
    try:
        print("Generating video with audio...")
        response = requests.post('http://localhost:5001/save-to-video',
                               json={'content_items': test_content},
                               timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Video with audio generated successfully!")
                print(f"Video URL: {data.get('video_url')}")
                return True
            else:
                print(f"❌ Video generation failed: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Audio and Video Debug Test")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5001/', timeout=5)
        print("✅ Server is running")
    except:
        print("❌ Server is not running. Please start the server first:")
        print("   python server.py")
        exit(1)
    
    # Test audio generation
    audio_url = test_audio_generation()
    
    # Test audio files listing
    audio_files = test_audio_files()
    
    # Test video with audio
    if audio_url:
        success = test_video_with_audio()
        if success:
            print("\n🎉 Audio and video test completed successfully!")
        else:
            print("\n💥 Video with audio test failed!")
    else:
        print("\n💥 Cannot test video with audio - audio generation failed!") 