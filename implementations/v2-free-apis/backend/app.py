"""
Flask API Server - The main backend that ties everything together

This is the heart of your application. It:
1. Receives questions from the frontend
2. Gets AI response from Gemini
3. Creates avatar video from HeyGen
4. Returns the video URL to display

Architecture:
Frontend → Flask API → Gemini Service → HeyGen Service → Frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from gemini_service import GeminiService
from heygen_service import HeyGenService
import traceback

# Initialize Flask app
app = Flask(__name__)

# Enable CORS so frontend can call this API
# CORS = Cross-Origin Resource Sharing (allows browser to make requests)
CORS(app)

# Initialize our AI services
print("🚀 Initializing AI Avatar services...")
gemini_service = GeminiService()
heygen_service = HeyGenService()
print("✅ Services ready!")


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint - confirms the server is running.
    
    Test it: http://localhost:5000/api/health
    """
    return jsonify({
        'status': 'healthy',
        'message': 'AI Avatar API is running!'
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint - handles the complete interaction flow.
    
    Flow:
    1. Receive user's question
    2. Generate AI response using Gemini
    3. Create avatar video using HeyGen
    4. Return video URL
    
    Request body:
    {
        "message": "What is artificial intelligence?"
    }
    
    Response:
    {
        "success": true,
        "ai_response": "AI is the simulation of human intelligence...",
        "video_url": "https://heygen.com/video/...",
        "video_id": "abc123"
    }
    """
    try:
        # Step 1: Get the user's message from the request
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        print(f"\n📩 Received question: {user_message}")
        
        # Step 2: Get AI response from Gemini
        print("🤖 Generating AI response with Gemini...")
        ai_response = gemini_service.get_response(user_message)
        print(f"💬 Gemini says: {ai_response}")
        
        # Step 3: Try to create avatar video with HeyGen, fallback to text if it fails
        try:
            print("🎬 Creating avatar video with HeyGen...")
            video_result = heygen_service.create_video(ai_response)
            
            # Step 4: Return everything to the frontend
            return jsonify({
                'success': True,
                'ai_response': ai_response,
                'video_url': video_result['video_url'],
                'video_id': video_result['video_id'],
                'status': 'generating'
            })
            
        except Exception as video_error:
            print(f"❌ Video generation failed: {str(video_error)}")
            print("📝 Falling back to text-only response")
            
            # Return text-only response when video generation fails
            return jsonify({
                'success': True,
                'ai_response': ai_response,
                'video_url': None,
                'video_id': None,
                'status': 'text_only',
                'message': 'Video generation temporarily unavailable, showing text response'
            })
        
    except Exception as e:
        # If anything goes wrong, return a helpful error message
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """
    Clear conversation history to start a fresh conversation.
    
    Optional feature - useful if you want to reset the context.
    """
    try:
        gemini_service.clear_history()
        return jsonify({
            'success': True,
            'message': 'Conversation history cleared'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎭 AI AVATAR SERVER")
    print("="*60)
    print("Server running at: http://localhost:5001")
    print("Health check: http://localhost:5001/api/health")
    print("Chat endpoint: http://localhost:5001/api/chat")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Run the Flask server
    # debug=True enables auto-reload when you change code
    app.run(host='0.0.0.0', port=5001, debug=True)

