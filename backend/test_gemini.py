import os
import sys
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

api_key = os.environ.get("GEMINI_API_KEY")
model_name = os.environ.get("GEMINI_EXTRACTION_MODEL", "gemini-3.5-flash-lite")

print(f"GEMINI_API_KEY configured: {bool(api_key)}")
print(f"GEMINI_EXTRACTION_MODEL: {model_name}")

if not api_key:
    print("API key not found in env.")
    sys.exit(1)

try:
    import google.generativeai as genai
    print("Successfully imported google.generativeai")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello, reply with only the word OK")
    print(f"API Connectivity Test Success: {response.text.strip()}")
except Exception as e:
    print(f"API Connectivity Test Failed: {type(e).__name__} - {e}")
    sys.exit(1)
