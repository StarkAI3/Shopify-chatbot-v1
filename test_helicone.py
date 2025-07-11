import os
import requests
import time
import uuid
import json
from dotenv import load_dotenv

load_dotenv()  # Loads your .env file

HELICONE_API_KEY = os.environ.get("HELICONE_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

def test_helicone_integration():
    """Test Helicone integration with comprehensive observability"""
    if not HELICONE_API_KEY:
        print("❌ HELICONE_API_KEY not found in environment variables")
        return False
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        return False
    print("✅ Environment variables loaded successfully")
    test_prompts = [
        "Hello from Helicone test!",
        "What is the weather like today?",
        "Tell me a short joke"
    ]
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🧪 Test {i}: Testing prompt: '{prompt[:50]}...'")
        request_id = str(uuid.uuid4())
        start_time = time.time()
        url = f"https://gateway.helicone.ai/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_API_KEY}"
        headers = {
            "Content-Type": "application/json",
            "Helicone-Auth": f"Bearer {HELICONE_API_KEY}",
            "Helicone-Target-URL": "https://generativelanguage.googleapis.com",
            "helicone-cache-enabled": "true",
            "helicone-property-request-id": request_id,
            "helicone-property-user-id": "test-user",
            "helicone-property-session-id": "test-session",
            "helicone-property-model": "gemini-2.0-flash",
            "helicone-property-prompt-length": str(len(prompt)),
            "helicone-property-application": "starky-shop-chatbot-test"
        }
        data = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]}
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 500
            }
        }
        try:
            print(f"📤 Sending request to Helicone (ID: {request_id})...")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            end_time = time.time()
            response_time = end_time - start_time
            print(f"📥 Response received in {response_time:.2f}s")
            print(f"📊 Status code: {response.status_code}")
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    response_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"✅ Success! Response: {response_text[:100]}...")
                    print(f"📈 Response length: {len(response_text)} characters")
                except (KeyError, IndexError) as e:
                    print(f"❌ Failed to parse response: {e}")
                    print(f"🔍 Raw response: {response.text[:200]}...")
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"🔍 Error response: {response.text[:200]}...")
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    return True

def test_helicone_headers():
    print("\n🔧 Testing Helicone header configurations...")
    test_headers = [
        {
            "name": "Basic Headers",
            "headers": {
                "Content-Type": "application/json",
                "Helicone-Auth": f"Bearer {HELICONE_API_KEY}",
                "Helicone-Target-URL": "https://generativelanguage.googleapis.com"
            }
        },
        {
            "name": "With Cache",
            "headers": {
                "Content-Type": "application/json",
                "Helicone-Auth": f"Bearer {HELICONE_API_KEY}",
                "Helicone-Target-URL": "https://generativelanguage.googleapis.com",
                "helicone-cache-enabled": "true"
            }
        },
        {
            "name": "With Properties",
            "headers": {
                "Content-Type": "application/json",
                "Helicone-Auth": f"Bearer {HELICONE_API_KEY}",
                "Helicone-Target-URL": "https://generativelanguage.googleapis.com",
                "helicone-property-request-id": str(uuid.uuid4()),
                "helicone-property-user-id": "test-user",
                "helicone-property-application": "starky-shop-chatbot"
            }
        }
    ]
    for config in test_headers:
        print(f"\n📋 Testing: {config['name']}")
        data = {
            "contents": [
                {"role": "user", "parts": [{"text": "Test message"}]}
            ]
        }
        try:
            url = f"https://gateway.helicone.ai/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_API_KEY}"
            response = requests.post(
                url,
                headers=config["headers"],
                json=data,
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ {config['name']}: Success")
            else:
                print(f"❌ {config['name']}: Failed (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {config['name']}: Error - {e}")

if __name__ == "__main__":
    print("🚀 Starting Helicone Integration Tests")
    print("=" * 50)
    success = test_helicone_integration()
    if success:
        test_helicone_headers()
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("\n📊 Next steps:")
        print("1. Check your Helicone dashboard for request logs")
        print("2. Verify that requests are being tracked with proper metadata")
        print("3. Test the enhanced app.py with user sessions")
        print("4. Monitor response times and success rates")
    else:
        print("\n❌ Tests failed. Please check your environment variables.")
