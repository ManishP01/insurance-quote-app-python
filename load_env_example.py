"""
Example: How to load environment variables from .env file
Add this to the top of your app.py for automatic .env loading
"""

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file automatically
    print("✅ .env file loaded successfully")
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables.")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

import os

# Now you can use environment variables normally
openai_key = os.getenv('OPENAI_API_KEY')
if openai_key:
    print("✅ OpenAI API key found")
else:
    print("❌ No OpenAI API key found")
