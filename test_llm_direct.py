#!/usr/bin/env python3
"""
Direct test of TCS GenAI Lab API with SSL bypass
"""
import asyncio
import httpx
import json
import ssl
import sys
sys.path.append('.')

from backend.core.config import settings

async def test_llm_direct():
    """Test LLM API directly with custom SSL context"""
    
    print("🧪 Testing TCS GenAI Lab API Direct Connection")
    print("=" * 50)
    print(f"API Base URL: {settings.OPENAI_API_BASE}")
    print(f"Model: {settings.LLM_MODEL}")
    print(f"API Key: {settings.OPENAI_API_KEY[:10]}...")
    print("=" * 50)
    
    # Create SSL context that bypasses certificate verification
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Test payload
    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {
                "role": "user",
                "content": "You are an AI assistant for a multi-agent orchestration platform. Analyze this task: 'Create a market research report with competitor analysis and customer insights'. Provide: 1) Complexity score (1-10), 2) Required capabilities, 3) Estimated time, 4) Recommended approach. Keep response under 200 words."
            }
        ],
        "max_tokens": 300,
        "temperature": 0.7
    }
    
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # Create HTTP client with custom SSL context
        async with httpx.AsyncClient(verify=ssl_context, timeout=30.0) as client:
            print("🔄 Sending request to TCS GenAI Lab API...")
            
            response = await client.post(
                f"{settings.OPENAI_API_BASE}/v1/chat/completions",
                json=payload,
                headers=headers
            )
            
            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n✅ LLM API Response Received!")
                print("=" * 50)
                print("🤖 AI MODEL RESPONSE:")
                print("=" * 50)
                
                if 'choices' in result and len(result['choices']) > 0:
                    ai_response = result['choices'][0]['message']['content']
                    print(ai_response)
                    print("=" * 50)
                    
                    # Show usage stats
                    if 'usage' in result:
                        usage = result['usage']
                        print(f"\n📊 Token Usage:")
                        print(f"   Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
                        print(f"   Completion tokens: {usage.get('completion_tokens', 'N/A')}")
                        print(f"   Total tokens: {usage.get('total_tokens', 'N/A')}")
                    
                    return True, ai_response
                else:
                    print("❌ No response content found")
                    print(f"Raw response: {result}")
                    return False, None
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False, None
                
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False, None

async def test_task_decomposition():
    """Test task decomposition with the LLM"""
    
    print("\n🔄 Testing Task Decomposition...")
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Decompose this complex task into 3-4 smaller subtasks: 'Create a comprehensive business intelligence dashboard with real-time data visualization, automated reporting, and predictive analytics'. Return as JSON array with 'title' and 'description' for each subtask."
            }
        ],
        "max_tokens": 400,
        "temperature": 0.3
    }
    
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(verify=ssl_context, timeout=30.0) as client:
            response = await client.post(
                f"{settings.OPENAI_API_BASE}/v1/chat/completions",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    decomposition = result['choices'][0]['message']['content']
                    print("\n✅ Task Decomposition Response:")
                    print("=" * 50)
                    print(decomposition)
                    print("=" * 50)
                    return True, decomposition
            
            return False, None
            
    except Exception as e:
        print(f"❌ Decomposition test failed: {e}")
        return False, None

if __name__ == "__main__":
    async def main():
        # Test basic LLM functionality
        success1, response1 = await test_llm_direct()
        
        # Test task decomposition
        success2, response2 = await test_task_decomposition()
        
        if success1 and success2:
            print("\n🎉 LLM MODEL TEST: SUCCESS")
            print("✅ Your TCS GenAI Lab API is working perfectly!")
            print("✅ Task analysis and decomposition are functional!")
            return True
        elif success1:
            print("\n⚠️  LLM MODEL TEST: PARTIAL SUCCESS")
            print("✅ Basic API calls work")
            print("❌ Task decomposition needs adjustment")
            return True
        else:
            print("\n💥 LLM MODEL TEST: FAILED")
            print("❌ Unable to connect to TCS GenAI Lab API")
            return False
    
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
