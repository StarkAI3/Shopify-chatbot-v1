import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Loads your .env file

HELICONE_API_KEY = os.environ.get("HELICONE_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

url = "https://gateway.helicone.ai/v1beta/models/gemini-2.0-flash:generateContent"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GOOGLE_API_KEY}",
    "helicone-auth": f"Bearer {HELICONE_API_KEY}",
    "helicone-target-url": "https://generativelanguage.googleapis.com"
}
data = {
    "contents": [
        {"role": "user", "parts": [{"text": "Hello from Helicone test!"}]}
    ]
}
response = requests.post(url, headers=headers, json=data)
print("Status code:", response.status_code)
print("Response text:", response.text)
