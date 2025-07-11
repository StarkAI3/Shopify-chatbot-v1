"""
Helicone Configuration for LLM Observability
"""
import os
from dotenv import load_dotenv

load_dotenv()

class HeliconeConfig:
    """Configuration class for Helicone integration"""
    
    # API Keys
    HELICONE_API_KEY = os.environ.get("HELICONE_API_KEY")
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    # Helicone Gateway URL (no key yet)
    BASE_GATEWAY_URL = "https://gateway.helicone.ai/v1beta/models/gemini-2.0-flash:generateContent"
    # Target API URL
    TARGET_URL = "https://generativelanguage.googleapis.com"
    # Application settings
    APPLICATION_NAME = "starky-shop-chatbot"
    # Model settings
    MODEL_NAME = "gemini-2.0-flash"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 1000
    # Observability settings
    ENABLE_CACHE = True
    ENABLE_LOGGING = True
    REQUEST_TIMEOUT = 30

    @classmethod
    def get_gateway_url(cls):
        """Return the full Helicone proxy URL with Google API key as query param"""
        return f"{cls.BASE_GATEWAY_URL}?key={cls.GOOGLE_API_KEY}"

    @classmethod
    def get_base_headers(cls, request_id=None, user_id=None, session_id=None):
        """Get base headers for Helicone requests (per docs)"""
        headers = {
            "Content-Type": "application/json",
            "Helicone-Auth": f"Bearer {cls.HELICONE_API_KEY}",
            "Helicone-Target-URL": cls.TARGET_URL,
            "helicone-cache-enabled": str(cls.ENABLE_CACHE).lower(),
            "helicone-property-model": cls.MODEL_NAME,
            "helicone-property-application": cls.APPLICATION_NAME
        }
        if request_id:
            headers["helicone-property-request-id"] = request_id
        if user_id:
            headers["helicone-property-user-id"] = user_id
        if session_id:
            headers["helicone-property-session-id"] = session_id
        return headers

    @classmethod
    def get_generation_config(cls, temperature=None, max_tokens=None):
        return {
            "temperature": temperature or cls.DEFAULT_TEMPERATURE,
            "maxOutputTokens": max_tokens or cls.DEFAULT_MAX_TOKENS
        }
    @classmethod
    def validate_config(cls):
        errors = []
        if not cls.HELICONE_API_KEY:
            errors.append("HELICONE_API_KEY is not set")
        if not cls.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY is not set")
        return errors
    @classmethod
    def is_configured(cls):
        return len(cls.validate_config()) == 0

def get_helicone_headers(request_id=None, user_id=None, session_id=None, prompt_length=None):
    headers = HeliconeConfig.get_base_headers(request_id, user_id, session_id)
    if prompt_length is not None:
        headers["helicone-property-prompt-length"] = str(prompt_length)
    return headers

def get_request_data(prompt, temperature=None, max_tokens=None):
    return {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        "generationConfig": HeliconeConfig.get_generation_config(temperature, max_tokens)
    } 