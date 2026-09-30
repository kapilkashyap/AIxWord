#!/usr/bin/env python3
"""
Test OpenAI API connectivity.

This script tests if we can reach OpenAI's API, which might be blocked
by corporate firewalls (like Zscaler) or network restrictions.
"""

import os
import sys
from openai import OpenAI
from config import get_settings

def test_openai_connection():
    """Test OpenAI API connectivity."""
    print("=" * 60)
    print("OpenAI API Connectivity Test")
    print("=" * 60)
    
    # Check API key
    settings = get_settings()
    api_key = settings.openai_api_key
    
    if not api_key or api_key == "your-openai-api-key-here":
        print("❌ ERROR: OpenAI API key not configured!")
        print("   Please set OPENAI_API_KEY in backend/.env")
        return False
    
    print(f"✓ API key found: {api_key[:10]}...{api_key[-4:]}")
    print(f"✓ Model: {settings.openai_model}")
    print()
    
    # Test connection
    print("Testing OpenAI API connection...")
    try:
        client = OpenAI(api_key=api_key)
        
        # Simple test request
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello' in one word."}
            ],
            max_tokens=10,
            temperature=0.0
        )
        
        content = response.choices[0].message.content
        print(f"✓ Connection successful!")
        print(f"✓ Response: {content}")
        print(f"✓ Tokens used: {response.usage.total_tokens if response.usage else 'unknown'}")
        print()
        print("=" * 60)
        print("✅ OpenAI API is accessible!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Connection FAILED!")
        print(f"   Error: {type(e).__name__}: {str(e)}")
        print()
        
        # Check for common issues
        error_str = str(e).lower()
        
        if "401" in error_str or "unauthorized" in error_str:
            print("💡 Possible cause: Invalid API key")
            print("   → Check your OPENAI_API_KEY in backend/.env")
        
        elif "403" in error_str or "forbidden" in error_str:
            print("💡 Possible cause: API key doesn't have access to this model")
            print(f"   → Check if your key has access to {settings.openai_model}")
        
        elif "timeout" in error_str or "connection" in error_str:
            print("💡 Possible cause: Network/firewall blocking OpenAI")
            print("   → Check if Zscaler or corporate firewall is blocking api.openai.com")
            print("   → Try: curl -I https://api.openai.com/v1/models")
        
        elif "ssl" in error_str or "certificate" in error_str:
            print("💡 Possible cause: SSL/TLS certificate issue (common with Zscaler)")
            print("   → Corporate proxy might be intercepting HTTPS traffic")
            print("   → You may need to configure SSL certificates or disable SSL verification")
        
        else:
            print("💡 Unknown error - check the error message above")
        
        print()
        print("=" * 60)
        print("❌ OpenAI API is NOT accessible!")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = test_openai_connection()
    sys.exit(0 if success else 1)
