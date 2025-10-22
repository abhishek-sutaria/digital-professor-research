"""
Quick test script to verify the avatar persona is loaded correctly

Run this to test that Jenniel (Professor Morgan's avatar) is working
without having to generate a full video.

Usage: python test_persona.py
"""

from gemini_service import GeminiService

def test_persona():
    """Test that the avatar persona loads and responds correctly"""
    
    print("\n" + "="*60)
    print("🎭 TESTING AVATAR PERSONA")
    print("="*60)
    
    # Initialize the service
    print("\n1. Initializing Gemini service...")
    service = GeminiService()
    
    # Test questions that should trigger Professor Morgan's expertise
    test_questions = [
        "How should we approach our marketing strategy?",
        "What metrics should we track?",
        "Should we chase market share aggressively?"
    ]
    
    print("\n2. Testing with Professor Morgan-style questions...\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'─'*60}")
        print(f"Test {i}: {question}")
        print('─'*60)
        
        response = service.get_response(question)
        
        print(f"\n✨ Jenniel's Response:")
        print(f"{response}\n")
        
        # Check for Professor Morgan's signature elements
        morgan_indicators = [
            'strategy', 'capabilities', 'value', 'framework', 
            'customer', 'evidence', 'metric', 'alignment'
        ]
        
        found_indicators = [
            word for word in morgan_indicators 
            if word.lower() in response.lower()
        ]
        
        if found_indicators:
            print(f"✅ Morgan-style vocabulary detected: {', '.join(found_indicators)}")
        else:
            print("⚠️  No signature vocabulary found - check if persona is loaded")
    
    print("\n" + "="*60)
    print("✅ PERSONA TEST COMPLETE")
    print("="*60)
    print("\nIf responses sound like a marketing strategy professor,")
    print("your persona is working correctly! 🎓\n")

if __name__ == "__main__":
    test_persona()




