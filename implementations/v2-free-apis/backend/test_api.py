"""
Test API endpoint that only tests Gemini without HeyGen video generation
This allows us to test the persona without using HeyGen credits
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from gemini_service import GeminiService
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Gemini service
print("🚀 Initializing AI Avatar services...")
gemini_service = GeminiService()
print("✅ Gemini service ready!")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'AI Avatar API (Gemini only) is running!'
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint that only uses Gemini (no video generation)
    Perfect for testing the persona without using HeyGen credits
    """
    try:
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
        
        # Get AI response from Gemini (this is working!)
        print("🤖 Generating AI response with Gemini...")
        ai_response = gemini_service.get_response(user_message)
        print(f"💬 Jenniel says: {ai_response}")
        
        # Return just the text response (no video for now)
        return jsonify({
            'success': True,
            'ai_response': ai_response,
            'video_url': None,  # No video for testing
            'video_id': 'test-mode',
            'note': 'Running in test mode - no video generation'
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎭 AI AVATAR SERVER (TEST MODE)")
    print("="*60)
    print("Server running at: http://localhost:5001")
    print("Health check: http://localhost:5001/api/health")
    print("Chat endpoint: http://localhost:5001/api/chat")
    print("\n📝 TEST MODE: Gemini responses only (no video generation)")
    print("This saves HeyGen credits while testing the persona!")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)



