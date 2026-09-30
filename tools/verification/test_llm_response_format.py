"""
Test script to check LLM response format.

This script tests the actual LLM response to see what format it returns.
"""

import json
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from llm.client import LLMClient
from agents.planner_prompts import PlannerPrompts

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_llm_response():
    """Test what the LLM actually returns."""
    print("=" * 80)
    print("Testing LLM Response Format")
    print("=" * 80)
    
    # Initialize client
    client = LLMClient()
    prompts = PlannerPrompts()
    
    # Create simple test messages
    system_prompt = prompts.system_prompt()
    user_prompt = prompts.user_prompt(
        topic="Technology",
        grid_size=8,
        min_words=10,
        max_words=20,
        difficulty="easy",
        grid_analysis={
            "placed_words": [],
            "fill_rate": 0.0,
            "word_count": 0,
            "iteration": 0,
            "available_spaces": 64,
            "intersections": {"count": 0}
        }
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    print("\n📤 Calling LLM...")
    print(f"Model: {client.model}")
    
    try:
        # Get response
        response = client.get_json_response(
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        print("\n✅ LLM Response Received!")
        print(f"Response type: {type(response)}")
        print(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")
        
        print("\n📋 Full Response:")
        print(json.dumps(response, indent=2))
        
        # Check structure
        print("\n🔍 Structure Analysis:")
        
        if isinstance(response, dict):
            print("✅ Response is a dictionary")
            
            if "action" in response:
                print(f"✅ Has 'action': {response['action']}")
            else:
                print("❌ Missing 'action' field")
            
            if "reasoning" in response:
                print(f"✅ Has 'reasoning': {response['reasoning'][:100]}...")
            else:
                print("❌ Missing 'reasoning' field")
            
            if "word_candidates" in response:
                wc = response["word_candidates"]
                print(f"✅ Has 'word_candidates': type={type(wc)}, length={len(wc) if isinstance(wc, list) else 'N/A'}")
                if isinstance(wc, list) and len(wc) > 0:
                    print(f"   First candidate: {wc[0]}")
            else:
                print("❌ Missing 'word_candidates' field")
            
            if "placement_plan" in response:
                pp = response["placement_plan"]
                print(f"✅ Has 'placement_plan': type={type(pp)}, length={len(pp) if isinstance(pp, list) else 'N/A'}")
                if isinstance(pp, list) and len(pp) > 0:
                    print(f"   First placement: {pp[0]}")
            else:
                print("❌ Missing 'placement_plan' field")
        else:
            print(f"❌ Response is NOT a dictionary! Type: {type(response)}")
        
        print("\n" + "=" * 80)
        print("Test Complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_llm_response()
