"""
Gemini Service - Handles AI conversational responses

This service connects to Google's Gemini API to generate intelligent,
context-aware responses to user questions. It's the "brain" of your avatar.

How it works:
1. Takes a user's question as input
2. Sends it to Gemini API with conversation context
3. Returns a natural, conversational response
4. This response will be used to generate the avatar video
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class GeminiService:
    def __init__(self):
        """
        Initialize the Gemini API client with your API key.
        This sets up the connection to Google's AI.
        """
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Use gemini-2.0-flash model - it's free and works great for conversations
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Load custom system prompt from environment variable
        # This defines the avatar's personality, expertise, and behavior
        self.system_prompt = os.getenv('AVATAR_SYSTEM_PROMPT')
        
        # Fallback to default prompt if not configured
        if not self.system_prompt:
            self.system_prompt = """You are a friendly, knowledgeable AI avatar assistant. 
            Keep your responses conversational, warm, and concise (2-3 sentences max) 
            since they will be spoken by a video avatar. Be helpful and engaging."""
            print("⚠️ Using default system prompt. Set AVATAR_SYSTEM_PROMPT in .env to customize.")
        else:
            print("✅ Loaded custom avatar persona from AVATAR_SYSTEM_PROMPT")
        
        # Store conversation history for context-aware responses
        self.chat_history = []
    
    def get_response(self, user_message: str) -> str:
        """
        Get an AI response from Gemini for the user's message.
        
        Args:
            user_message: The question or statement from the user
            
        Returns:
            A natural, conversational response from Gemini
            
        How it works:
        - Sends the user's message to Gemini
        - Gemini processes it with context from previous messages
        - Returns a thoughtful, relevant response
        """
        try:
            # Use the configured system prompt (loaded from .env)
            # This gives the avatar its personality and expertise
            
            # Combine system prompt with user message
            full_prompt = f"{self.system_prompt}\n\nUser: {user_message}\nAssistant:"
            
            # Generate response from Gemini
            response = self.model.generate_content(full_prompt)
            
            # Extract the text from the response
            ai_response = response.text
            
            # Store in history for future context (optional enhancement)
            self.chat_history.append({
                'user': user_message,
                'assistant': ai_response
            })
            
            return ai_response
            
        except Exception as e:
            print(f"Error getting Gemini response: {str(e)}")
            # Fallback response if Gemini fails
            return "I apologize, but I'm having trouble processing that right now. Could you please try again?"
    
    def clear_history(self):
        """Clear conversation history to start fresh."""
        self.chat_history = []


# Example usage (for testing)
if __name__ == "__main__":
    service = GeminiService()
    response = service.get_response("Hello! Who are you?")
    print(f"Gemini Response: {response}")

