import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Test the API key
def test_gemini_api():
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return
    
    print(f"✅ API Key loaded: {api_key[:10]}...")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # First, let's see what models are available
        print("📋 Available models:")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"   - {model.name}")
        
        # Use the correct model name for Gemini 1.5
        model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model name
        response = model.generate_content("Say hello!")
        
        print("✅ Gemini API working!")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error testing Gemini API: {e}")
        
        # If gemini-1.5-flash doesn't work, try alternative
        try:
            print("🔄 Trying alternative model...")
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content("Say hello!")
            print("✅ Alternative model working!")
            print(f"Response: {response.text}")
        except Exception as e2:
            print(f"❌ Alternative model also failed: {e2}")

if __name__ == "__main__":
    test_gemini_api()