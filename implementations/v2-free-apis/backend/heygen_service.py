"""
HeyGen Service - Handles avatar video generation

This service connects to HeyGen's API to create realistic talking avatar videos
using your custom avatar and the AI-generated text responses.

How it works:
1. Takes text (from Gemini response)
2. Sends it to HeyGen with your avatar ID
3. HeyGen generates a video of your avatar speaking that text
4. Returns the video URL once it's ready
"""

import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HeyGenService:
    def __init__(self):
        """
        Initialize HeyGen API client with your credentials.
        
        Sets up:
        - API key for authentication
        - Avatar ID (your custom avatar from the headshot)
        - Base URL for HeyGen API
        """
        self.api_key = os.getenv('HEYGEN_API_KEY')
        self.avatar_id = os.getenv('HEYGEN_AVATAR_ID')
        
        if not self.api_key:
            raise ValueError("HEYGEN_API_KEY not found in environment variables")
        if not self.avatar_id:
            raise ValueError("HEYGEN_AVATAR_ID not found in environment variables")
        
        # HeyGen API base URLs (v2 for video generation, v1 for status)
        self.base_url_v2 = "https://api.heygen.com/v2"
        self.base_url_v1 = "https://api.heygen.com/v1"
        
        # Headers for all API requests
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def create_video(self, text: str) -> dict:
        """
        Create a talking avatar video with the given text.
        
        Args:
            text: The text that the avatar should speak
            
        Returns:
            Dictionary containing:
            - video_url: URL to the generated video
            - video_id: ID of the video for tracking
            
        Process:
        1. Submit video generation request to HeyGen
        2. Poll for completion (videos take 30-60 seconds)
        3. Return the video URL once ready
        """
        try:
            # Step 1: Create the video generation request
            video_data = {
                "video_inputs": [
                    {
                        "character": {
                            "type": "talking_photo",
                            "talking_photo_id": self.avatar_id
                        },
                        "voice": {
                            "type": "text",
                            "input_text": text,
                            "voice_id": "2d5b0e6cf36f460aa7fc47e3eee4ba54",  # Default English voice
                            # You can explore other voices at: https://docs.heygen.com/reference/list-voices-v2
                        },
                        "background": {
                            "type": "color",
                            "value": "#FFFFFF"  # White background
                        }
                    }
                ],
                "dimension": {
                    "width": 1280,
                    "height": 720
                },
                "aspect_ratio": "16:9",
                "test": False  # Set to True for faster test videos (with watermark)
            }
            
            print("📹 Submitting video generation request to HeyGen...")
            
            # Submit the request to v2 endpoint
            response = requests.post(
                f"{self.base_url_v2}/video/generate",
                headers=self.headers,
                json=video_data,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('error'):
                raise Exception(f"HeyGen API error: {result['error']}")
            
            video_id = result.get('data', {}).get('video_id')
            
            if not video_id:
                raise Exception("No video ID returned from HeyGen")
            
            print(f"✅ Video generation started! Video ID: {video_id}")
            print("⏳ Waiting for video to be ready (this takes 30-60 seconds)...")
            
            # Step 2: Poll for video completion
            video_url = self._wait_for_video(video_id)
            
            return {
                'video_url': video_url,
                'video_id': video_id
            }
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error calling HeyGen API: {str(e)}")
            raise Exception(f"Failed to create video: {str(e)}")
        except Exception as e:
            print(f"❌ Error creating video: {str(e)}")
            raise
    
    def _wait_for_video(self, video_id: str, max_wait_time: int = 180) -> str:
        """
        Poll HeyGen API until the video is ready.
        
        Args:
            video_id: The ID of the video being generated
            max_wait_time: Maximum seconds to wait (default: 3 minutes)
            
        Returns:
            The URL of the completed video
            
        Why we need this:
        - Video generation isn't instant (takes 30-60 seconds)
        - We need to check status periodically until it's done
        - This is called "polling" - checking repeatedly until ready
        """
        start_time = time.time()
        
        while True:
            # Check if we've waited too long
            if time.time() - start_time > max_wait_time:
                raise Exception("Video generation timed out")
            
            try:
                # Check video status using v1 endpoint
                response = requests.get(
                    f"{self.base_url_v1}/video_status.get",
                    params={"video_id": video_id},
                    headers=self.headers,
                    timeout=30
                )
                
                response.raise_for_status()
                result = response.json()
                
                status = result.get('data', {}).get('status')
                
                if status == 'completed':
                    video_url = result.get('data', {}).get('video_url')
                    print(f"🎉 Video ready! URL: {video_url}")
                    return video_url
                
                elif status == 'failed':
                    error = result.get('data', {}).get('error', 'Unknown error')
                    raise Exception(f"Video generation failed: {error}")
                
                else:
                    # Still processing, wait and try again
                    print(f"⏳ Status: {status}... waiting 5 seconds")
                    time.sleep(5)
                    
            except requests.exceptions.RequestException as e:
                print(f"Error checking video status: {str(e)}")
                time.sleep(5)


# Example usage (for testing)
if __name__ == "__main__":
    service = HeyGenService()
    result = service.create_video("Hello! I'm your AI avatar. How can I help you today?")
    print(f"Video URL: {result['video_url']}")

