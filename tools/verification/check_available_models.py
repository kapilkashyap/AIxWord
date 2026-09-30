#!/usr/bin/env python3
"""
Check which OpenAI models are available with your API key.
"""
import os
import sys
from openai import OpenAI

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment!")
        print("   Make sure you have a .env file with your API key.")
        sys.exit(1)
    
    print("=" * 60)
    print("Checking Available OpenAI Models")
    print("=" * 60)
    print(f"✓ API key found: {api_key[:10]}...{api_key[-4:]}")
    print()
    
    try:
        client = OpenAI(api_key=api_key)
        
        print("Fetching available models...")
        models = client.models.list()
        
        # Filter for GPT models
        gpt_models = [m for m in models.data if 'gpt' in m.id.lower()]
        gpt_models.sort(key=lambda x: x.id)
        
        print(f"\n✓ Found {len(gpt_models)} GPT models available:\n")
        
        # Categorize models
        gpt4_models = []
        gpt35_models = []
        other_models = []
        
        for model in gpt_models:
            if 'gpt-4' in model.id:
                gpt4_models.append(model.id)
            elif 'gpt-3.5' in model.id:
                gpt35_models.append(model.id)
            else:
                other_models.append(model.id)
        
        if gpt4_models:
            print("GPT-4 Models:")
            for model_id in gpt4_models:
                print(f"  • {model_id}")
            print()
        
        if gpt35_models:
            print("GPT-3.5 Models:")
            for model_id in gpt35_models:
                print(f"  • {model_id}")
            print()
        
        if other_models:
            print("Other GPT Models:")
            for model_id in other_models:
                print(f"  • {model_id}")
            print()
        
        # Recommendations
        print("=" * 60)
        print("Recommendations for AIxWord:")
        print("=" * 60)
        
        recommended = None
        
        # Check for specific models in order of preference
        if 'gpt-4o' in [m.id for m in models.data]:
            recommended = 'gpt-4o'
            print(f"✓ BEST: {recommended} (latest, fastest GPT-4)")
        elif 'gpt-4-turbo' in [m.id for m in models.data]:
            recommended = 'gpt-4-turbo'
            print(f"✓ BEST: {recommended} (fast GPT-4)")
        elif any('gpt-4' in m.id for m in models.data):
            gpt4 = next(m.id for m in models.data if 'gpt-4' in m.id)
            recommended = gpt4
            print(f"✓ GOOD: {recommended} (GPT-4 available)")
        elif 'gpt-3.5-turbo' in [m.id for m in models.data]:
            recommended = 'gpt-3.5-turbo'
            print(f"⚠ OK: {recommended} (cheaper, but less capable)")
        else:
            print("❌ No suitable models found!")
            print("   Your API key may not have access to GPT models.")
            sys.exit(1)
        
        print()
        print("To use this model, update your .env file:")
        print(f"  OPENAI_MODEL={recommended}")
        print()
        
        # Check current setting
        current_model = os.getenv("OPENAI_MODEL", "not set")
        print(f"Current setting in .env: OPENAI_MODEL={current_model}")
        
        if current_model not in [m.id for m in models.data]:
            print(f"❌ WARNING: '{current_model}' is NOT available with your API key!")
            print(f"   Change it to: {recommended}")
        else:
            print(f"✓ Your current model '{current_model}' is available!")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error checking models: {e}")
        print("\nPossible causes:")
        print("  • Invalid API key")
        print("  • Network connectivity issues")
        print("  • OpenAI API is down")
        sys.exit(1)

if __name__ == "__main__":
    main()
