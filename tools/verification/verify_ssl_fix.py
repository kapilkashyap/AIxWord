#!/usr/bin/env python3
"""
Verify that SSL certificate configuration is working correctly.
"""

import os
import sys


def verify_ssl_configuration():
    """Verify SSL certificate configuration."""
    print("🔍 Verifying SSL Certificate Configuration\n")
    print("=" * 60)
    
    # Check 1: certifi installed
    print("\n1. Checking if certifi is installed...")
    try:
        import certifi
        cert_path = certifi.where()
        print(f"   ✅ certifi installed: {cert_path}")
    except ImportError:
        print("   ❌ certifi NOT installed!")
        print("   Run: pip install certifi>=2023.7.22")
        return False
    
    # Check 2: SSL_CERT_FILE environment variable
    print("\n2. Checking SSL_CERT_FILE environment variable...")
    if "SSL_CERT_FILE" in os.environ:
        print(f"   ✅ SSL_CERT_FILE set: {os.environ['SSL_CERT_FILE']}")
    else:
        print("   ⚠️  SSL_CERT_FILE not set (will be auto-configured by config.py)")
    
    # Check 3: config.py has SSL configuration
    print("\n3. Checking config.py for SSL configuration...")
    try:
        with open("config.py", "r") as f:
            config_content = f.read()
            if "SSL_CERT_FILE" in config_content and "certifi" in config_content:
                print("   ✅ config.py has SSL certificate configuration")
            else:
                print("   ❌ config.py missing SSL configuration!")
                return False
    except FileNotFoundError:
        print("   ❌ config.py not found!")
        return False
    
    # Check 4: pyproject.toml has certifi dependency
    print("\n4. Checking pyproject.toml for certifi dependency...")
    try:
        with open("pyproject.toml", "r") as f:
            toml_content = f.read()
            if "certifi" in toml_content:
                print("   ✅ pyproject.toml includes certifi dependency")
            else:
                print("   ❌ pyproject.toml missing certifi dependency!")
                return False
    except FileNotFoundError:
        print("   ❌ pyproject.toml not found!")
        return False
    
    # Check 5: Test importing config (triggers SSL setup)
    print("\n5. Testing config import (triggers SSL auto-configuration)...")
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Import config (this should set SSL_CERT_FILE)
        from config import get_settings
        
        if "SSL_CERT_FILE" in os.environ:
            print(f"   ✅ SSL_CERT_FILE auto-configured: {os.environ['SSL_CERT_FILE']}")
        else:
            print("   ⚠️  SSL_CERT_FILE not auto-configured (might be set externally)")
        
        # Try to get settings
        settings = get_settings()
        print(f"   ✅ Settings loaded successfully")
        
    except Exception as e:
        print(f"   ❌ Error importing config: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("\n✅ SSL Certificate Configuration Verified!\n")
    print("Next steps:")
    print("1. Restart the server: ./install_certifi_and_restart.sh")
    print("2. Test OpenAI connection: python test_openai_connection.py")
    print("3. Try generating a puzzle from the UI")
    print()
    
    return True


if __name__ == "__main__":
    success = verify_ssl_configuration()
    sys.exit(0 if success else 1)
