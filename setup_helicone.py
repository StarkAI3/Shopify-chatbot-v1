#!/usr/bin/env python3
"""
Helicone Setup Script
Helps configure and validate Helicone integration
"""
import os
import sys
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print("❌ .env file not found")
        return False
    
    load_dotenv()
    
    required_vars = ["HELICONE_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    # Check for either GOOGLE_API_KEY or GEMINI_API_KEY
    google_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not google_key:
        missing_vars.append("GOOGLE_API_KEY or GEMINI_API_KEY")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables found")
    return True

def create_env_template():
    """Create a template .env file"""
    template = """# Helicone Configuration
# Get your Helicone API key from: https://www.helicone.ai/
HELICONE_API_KEY=your_helicone_api_key_here

# Google API Key for Gemini
# Get your Google API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key_here

# Shopify Configuration (optional)
SHOPIFY_API_KEY=your_shopify_api_key_here
SHOP_NAME=your_shop_name_here
"""
    
    with open(".env.template", "w") as f:
        f.write(template)
    
    print("📝 Created .env.template file")
    print("📋 Copy .env.template to .env and fill in your API keys")

def validate_setup():
    """Validate the complete setup"""
    print("\n🔍 Validating Helicone Setup...")
    print("=" * 40)
    
    # Check environment variables
    if not check_env_file():
        print("\n💡 To fix this:")
        print("1. Copy .env.template to .env")
        print("2. Add your Helicone API key from https://www.helicone.ai/")
        print("3. Add your Google API key from https://makersuite.google.com/app/apikey")
        return False
    
    # Test imports
    try:
        from helicone_config import HeliconeConfig
        print("✅ Helicone configuration module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import HeliconeConfig: {e}")
        return False
    
    # Validate configuration
    config_errors = HeliconeConfig.validate_config()
    if config_errors:
        print(f"❌ Configuration errors: {config_errors}")
        return False
    
    print("✅ Helicone configuration is valid")
    
    # Test basic functionality
    try:
        headers = HeliconeConfig.get_base_headers("test-id", "test-user", "test-session")
        if "helicone-auth" in headers:
            print("✅ Helicone headers generation working")
        else:
            print("❌ Helicone headers generation failed")
            return False
    except Exception as e:
        print(f"❌ Error testing headers: {e}")
        return False
    
    print("\n🎉 Helicone setup is complete and ready to use!")
    return True

def run_tests():
    """Run the Helicone tests"""
    print("\n🧪 Running Helicone Tests...")
    print("=" * 40)
    
    try:
        from test_helicone import test_helicone_integration
        success = test_helicone_integration()
        if success:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed")
        return success
    except ImportError as e:
        print(f"❌ Could not import test module: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Helicone Setup for LLM Observability")
    print("=" * 50)
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("📝 No .env file found. Creating template...")
        create_env_template()
        print("\n📋 Please:")
        print("1. Copy .env.template to .env")
        print("2. Add your API keys to .env")
        print("3. Run this script again")
        return
    
    # Validate setup
    if validate_setup():
        # Ask if user wants to run tests
        response = input("\n🧪 Would you like to run Helicone tests? (y/n): ").lower()
        if response in ['y', 'yes']:
            run_tests()
    
    print("\n📊 Next Steps:")
    print("1. Start your Flask app: python data/app.py api")
    print("2. Test the chat endpoint with user sessions")
    print("3. Check your Helicone dashboard for request logs")
    print("4. Monitor response times and success rates")

if __name__ == "__main__":
    main() 