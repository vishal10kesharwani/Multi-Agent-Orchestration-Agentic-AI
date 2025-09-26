#!/usr/bin/env python3
"""
Test script to verify LLM model is working with TCS GenAI Lab API
"""
import asyncio
import sys
import os
sys.path.append('.')

from backend.core.config import settings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

async def test_llm_model():
    """Test the LLM model with your API key"""
    
    print("🧪 Testing LLM Model with TCS GenAI Lab API")
    print("=" * 50)
    print(f"API Base URL: {settings.OPENAI_API_BASE}")
    print(f"Model: {settings.LLM_MODEL}")
    print(f"API Key: {settings.OPENAI_API_KEY[:10]}...")
    print("=" * 50)
    
    try:
        # Initialize the LLM client
        llm = ChatOpenAI(
            base_url=settings.OPENAI_API_BASE,
            api_key=settings.OPENAI_API_KEY,
            model=settings.LLM_MODEL,
            temperature=0.7,
            max_tokens=500
        )
        
        print("✅ LLM client initialized successfully")
        
        # Test prompt
        test_prompt = """
        You are an AI assistant for a multi-agent orchestration platform. 
        Please analyze this task and provide a brief response:
        
        Task: "Analyze customer data to identify purchasing patterns and recommend marketing strategies"
        
        Provide a structured analysis including:
        1. Task complexity (1-10 scale)
        2. Required capabilities
        3. Estimated time
        4. Recommended approach
        """
        
        print("\n🤖 Sending test prompt to LLM...")
        print(f"Prompt: {test_prompt[:100]}...")
        
        # Make the API call
        messages = [HumanMessage(content=test_prompt)]
        response = await llm.ainvoke(messages)
        
        print("\n✅ LLM Response Received!")
        print("=" * 50)
        print("🤖 AI MODEL RESPONSE:")
        print("=" * 50)
        print(response.content)
        print("=" * 50)
        
        # Test task decomposition specifically
        decomposition_prompt = """
        Decompose this complex task into 3-4 smaller subtasks:
        
        "Create a comprehensive market research report including competitor analysis, customer surveys, data visualization, and strategic recommendations"
        
        Return as a JSON list of subtasks with titles and descriptions.
        """
        
        print("\n🔄 Testing task decomposition...")
        decomp_messages = [HumanMessage(content=decomposition_prompt)]
        decomp_response = await llm.ainvoke(decomp_messages)
        
        print("\n✅ Task Decomposition Response:")
        print("=" * 50)
        print(decomp_response.content)
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ LLM Test Failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_llm_model())
    if result:
        print("\n🎉 LLM Model Test: SUCCESS")
        print("Your AI model is working perfectly with the TCS GenAI Lab API!")
    else:
        print("\n💥 LLM Model Test: FAILED")
        print("There may be an issue with the API configuration.")
    
    sys.exit(0 if result else 1)
