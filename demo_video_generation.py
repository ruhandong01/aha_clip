#!/usr/bin/env python3
"""
Demo script showing how to use the video generation feature
"""

import requests
import json
import time

def demo_video_generation():
    """Demonstrate the complete workflow: sentences -> images -> voice -> video"""
    
    print("🎬 AHA Clip Video Generation Demo")
    print("=" * 50)
    
    # Step 1: Generate sentences
    print("\n1. Generating sentences...")
    story_prompt = "A brave knight goes on an adventure to find a magical treasure"
    
    response = requests.post('http://localhost:5001/generate-sentences', 
                           json={'prompt': story_prompt})
    
    if response.status_code != 200:
        print("❌ Failed to generate sentences")
        return False
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ Error: {data.get('error')}")
        return False
    
    sentences = data.get('sentences', [])
    print(f"✅ Generated {len(sentences)} sentences")
    
    # Step 2: Generate images for each sentence
    print("\n2. Generating images...")
    images = []
    
    for i, sentence in enumerate(sentences):
        if sentence.strip():
            print(f"   Generating image {i+1}/{len(sentences)}...")
            response = requests.post('http://localhost:5001/generate-image', 
                                   json={'prompt': sentence})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    images.append(data.get('image'))
                    print(f"   ✅ Image {i+1} generated")
                else:
                    print(f"   ❌ Failed to generate image {i+1}")
                    images.append(None)
            else:
                print(f"   ❌ HTTP error for image {i+1}")
                images.append(None)
        else:
            images.append(None)
    
    # Step 3: Generate voice for each sentence
    print("\n3. Generating voice narration...")
    audio_urls = []
    
    for i, sentence in enumerate(sentences):
        if sentence.strip():
            print(f"   Generating voice {i+1}/{len(sentences)}...")
            response = requests.post('http://localhost:5001/generate-voice', 
                                   json={'text': sentence})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    audio_urls.append(data.get('audio_url'))
                    print(f"   ✅ Voice {i+1} generated")
                else:
                    print(f"   ❌ Failed to generate voice {i+1}")
                    audio_urls.append(None)
            else:
                print(f"   ❌ HTTP error for voice {i+1}")
                audio_urls.append(None)
        else:
            audio_urls.append(None)
    
    # Step 4: Prepare content for video generation
    print("\n4. Preparing content for video...")
    content_items = []
    
    for i in range(len(sentences)):
        if sentences[i].strip() and images[i]:
            content_items.append({
                'text': sentences[i],
                'image': images[i],
                'audio_url': audio_urls[i]
            })
    
    print(f"✅ Prepared {len(content_items)} content items for video")
    
    # Step 5: Generate the final video
    print("\n5. Generating final video...")
    print("   This may take a few minutes...")
    
    response = requests.post('http://localhost:5001/save-to-video', 
                           json={'content_items': content_items},
                           timeout=300)  # 5 minute timeout
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Video generated successfully!")
            print(f"📹 Video URL: {data.get('video_url')}")
            print(f"📁 Video filename: {data.get('video_filename')}")
            print("\n🎉 Demo completed successfully!")
            return True
        else:
            print(f"❌ Video generation failed: {data.get('error')}")
            return False
    else:
        print(f"❌ HTTP error: {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get('http://localhost:5001/', timeout=5)
        print("✅ Server is running")
    except:
        print("❌ Server is not running. Please start the server first:")
        print("   python server.py")
        exit(1)
    
    # Run the demo
    success = demo_video_generation()
    
    if not success:
        print("\n💥 Demo failed!")
        exit(1) 