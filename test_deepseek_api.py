#!/usr/bin/env python3
"""
Test script to verify DeepSeek API connectivity and functionality
"""
import os
import sys
import requests
import json
from datetime import datetime

# Load environment variables
sys.path.append('.')
from backend.core.config import settings

def test_deepseek_api():
    """Test DeepSeek API connectivity and response"""
    print("🧪 Testing DeepSeek API Configuration")
    print("=" * 50)
    
    # Display configuration
    print(f"API Base URL: {settings.OPENAI_API_BASE}")
    print(f"API Key: {settings.OPENAI_API_KEY[:10]}...{settings.OPENAI_API_KEY[-4:]}")
    print(f"Model: {settings.LLM_MODEL}")
    print()
    
    # Test 1: Basic connectivity
    print("1. Testing API connectivity...")
    try:
        # Try to access the base URL
        response = requests.get(settings.OPENAI_API_BASE, timeout=10)
        print(f"   ✅ Base URL accessible (Status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ Base URL not accessible: {e}")
        return False
    
    # Test 2: OpenAI-compatible API test
    print("\n2. Testing OpenAI-compatible API endpoint...")
    try:
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Test data for chat completion
        test_payload = {
            "model": settings.LLM_MODEL,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a helpful AI assistant. Respond briefly."
                },
                {
                    "role": "user", 
                    "content": "Hello! Can you confirm you're working? Just say 'API test successful' if everything is fine."
                }
            ],
            "max_tokens": 50,
            "temperature": 0.1
        }
        
        # Make API call
        api_url = f"{settings.OPENAI_API_BASE}/v1/chat/completions"
        response = requests.post(api_url, headers=headers, json=test_payload, timeout=30)
        
        print(f"   API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                ai_response = result['choices'][0]['message']['content']
                print(f"   ✅ API Response: {ai_response}")
                print(f"   ✅ Model: {result.get('model', 'Unknown')}")
                print(f"   ✅ Usage: {result.get('usage', {})}")
                return True
            else:
                print(f"   ❌ Unexpected response format: {result}")
                return False
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   Error details: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ API Test Failed: {e}")
        return False
    
    # Test 3: Alternative endpoint test
    print("\n3. Testing alternative endpoints...")
    try:
        # Test models endpoint
        models_url = f"{settings.OPENAI_API_BASE}/v1/models"
        response = requests.get(models_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print(f"   ✅ Models endpoint accessible")
            if 'data' in models:
                available_models = [m.get('id', 'Unknown') for m in models['data'][:3]]
                print(f"   Available models: {available_models}")
        else:
            print(f"   ⚠️  Models endpoint returned: {response.status_code}")
            
    except Exception as e:
        print(f"   ⚠️  Models endpoint test failed: {e}")

def test_with_platform_integration():
    """Test DeepSeek API through the platform's LLM client"""
    print("\n4. Testing through platform integration...")
    try:
        from backend.agents.llm_client import LLMClient
        
        client = LLMClient()
        
        # Test simple completion
        test_prompt = "What is 2+2? Answer with just the number."
        response = client.generate_response(test_prompt)
        
        if response and response.strip():
            print(f"   ✅ Platform integration working")
            print(f"   Response: {response[:100]}...")
            return True
        else:
            print(f"   ❌ Platform integration failed - no response")
            return False
            
    except Exception as e:
        print(f"   ❌ Platform integration test failed: {e}")
        return False

if __name__ == "__main__":
    print(f"🚀 DeepSeek API Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run basic API tests
    api_working = test_deepseek_api()
    
    # Run platform integration test
    platform_working = test_with_platform_integration()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"DeepSeek API Direct: {'✅ WORKING' if api_working else '❌ FAILED'}")
    print(f"Platform Integration: {'✅ WORKING' if platform_working else '❌ FAILED'}")
    
    if api_working and platform_working:
        print("\n🎉 DeepSeek API is fully functional!")
        print("Your multi-agent platform can use DeepSeek for AI responses.")
    elif api_working:
        print("\n⚠️  DeepSeek API works but platform integration needs fixing.")
    else:
        print("\n❌ DeepSeek API is not working properly.")
        print("Check your API key, base URL, and network connectivity.")
