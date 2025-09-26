"""
LLM Client Configuration for Multi-Agent Orchestration Platform
Uses the specific LangChain ChatOpenAI configuration provided by user
"""
import os
import httpx
import logging
from langchain_openai import ChatOpenAI
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LLMClient:
    """Centralized LLM client for all agents"""
    
    def __init__(self):
        # Configure httpx client with SSL verification disabled as specified
        self.http_client = httpx.Client(verify=False)
        
        # Initialize ChatOpenAI with user's specific configuration
        self.llm = ChatOpenAI(
            base_url="https://genailab.tcs.in",  # User's LiteLLM proxy
            model="azure_ai/genailab-maas-DeepSeek-V3-0324",  # User's specific model
            api_key="sk-_LvO2D4G66_3VX2yCgot2Q",  # User's API key
            http_client=self.http_client,
            temperature=0.7,  # Balanced creativity
            max_tokens=2048,  # Reasonable response length
            timeout=30.0  # 30 second timeout
        )
        
        logger.info("LLM Client initialized with DeepSeek-V3 model")
    
    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate response using the configured LLM"""
        try:
            # Add context to prompt if provided
            if context:
                context_str = f"Context: {context}\n\n"
                full_prompt = context_str + prompt
            else:
                full_prompt = prompt
            
            # Generate response
            response = self.llm.invoke(full_prompt)
            
            # Extract content from response
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            # Return fallback response
            return f"I apologize, but I encountered an error while processing your request. Error: {str(e)}"
    
    async def generate_structured_response(self, prompt: str, agent_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured response for specific agent types"""
        try:
            # Create agent-specific prompt
            agent_prompt = self._create_agent_prompt(prompt, agent_type, task_data)
            
            # Generate response
            response = await self.generate_response(agent_prompt)
            
            return {
                'success': True,
                'response': response,
                'agent_type': agent_type,
                'model': 'azure_ai/genailab-maas-DeepSeek-V3-0324'
            }
            
        except Exception as e:
            logger.error(f"Error generating structured response for {agent_type}: {e}")
            return {
                'success': False,
                'error': str(e),
                'agent_type': agent_type
            }
    
    def _create_agent_prompt(self, base_prompt: str, agent_type: str, task_data: Dict[str, Any]) -> str:
        """Create agent-specific prompts based on their specialization"""
        
        agent_contexts = {
            'research': """You are a Research Agent specialized in information gathering and analysis. 
Your capabilities include web research, data collection, fact verification, and comprehensive reporting.
Focus on providing accurate, well-sourced information with proper citations and analysis.""",
            
            'data_analysis': """You are a Data Analysis Agent specialized in statistical analysis and insights.
Your capabilities include data processing, statistical modeling, trend analysis, and visualization recommendations.
Focus on providing quantitative insights, patterns, and data-driven recommendations.""",
            
            'nlp': """You are a Natural Language Processing Agent specialized in text analysis and understanding.
Your capabilities include sentiment analysis, entity extraction, text summarization, and language understanding.
Focus on extracting meaningful insights from text data and providing linguistic analysis.""",
            
            'planning': """You are a Planning Agent specialized in task coordination and strategy.
Your capabilities include project planning, task decomposition, resource allocation, and workflow optimization.
Focus on creating structured plans and coordinating complex multi-step processes.""",
            
            'synthesis': """You are a Synthesis Agent specialized in combining and integrating results.
Your capabilities include result aggregation, conflict resolution, report generation, and final deliverable creation.
Focus on creating coherent, comprehensive outputs from multiple agent contributions."""
        }
        
        context = agent_contexts.get(agent_type, agent_contexts['research'])
        
        return f"""{context}

Task Details:
- Title: {task_data.get('title', 'Untitled Task')}
- Description: {task_data.get('description', 'No description provided')}
- Requirements: {task_data.get('requirements', {})}

User Request: {base_prompt}

Please provide a comprehensive response based on your specialization and the task requirements."""

    def test_connection(self) -> bool:
        """Test LLM connection"""
        try:
            response = self.llm.invoke("Hi, please respond with 'Connection successful'")
            return "successful" in str(response).lower()
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return False
    
    def __del__(self):
        """Cleanup httpx client"""
        if hasattr(self, 'http_client'):
            self.http_client.close()


# Global LLM client instance
_llm_client = None

def get_llm_client() -> LLMClient:
    """Get global LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
