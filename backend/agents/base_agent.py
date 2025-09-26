"""
Base Agent Implementation for the Multi-Agent Orchestration Platform
"""
import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from langchain_openai import ChatOpenAI
import httpx
import logging
from backend.core.llm_client import get_llm_client

from backend.core.config import settings
from backend.database.models import AgentStatus

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(
        self,
        name: str,
        description: str,
        capabilities: List[str],
        resource_requirements: Dict[str, Any] = None
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.resource_requirements = resource_requirements or {}
        self.status = AgentStatus.IDLE
        self.current_task = None
        self.performance_metrics = {
            'success_rate': 0.5,
            'avg_response_time': 1000,
            'total_tasks': 0,
            'completed_tasks': 0
        }
        
        # Initialize LLM client
        self.llm_client = get_llm_client()
        
        # Message handlers
        self.message_handlers = {}
        self.setup_message_handlers()
    
    def setup_message_handlers(self):
        """Setup message handlers for inter-agent communication"""
        pass
    
    @abstractmethod
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task assigned to this agent"""
        pass
    
    async def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming messages from other agents"""
        message_type = message.get('type')
        handler = self.message_handlers.get(message_type)
        
        if handler:
            try:
                return await handler(message)
            except Exception as e:
                logger.error(f"Error processing message {message_type}: {e}")
                return {
                    'type': 'error',
                    'error': str(e),
                    'original_message': message
                }
        else:
            logger.warning(f"No handler for message type: {message_type}")
            return None
    
    async def send_message(
        self, 
        recipient_id: str, 
        message_type: str, 
        content: Dict[str, Any],
        correlation_id: str = None
    ) -> bool:
        """Send a message to another agent"""
        # This will be implemented by the communication system
        pass
    
    def update_performance_metrics(self, task_result: Dict[str, Any]):
        """Update agent performance metrics based on task results"""
        self.performance_metrics['total_tasks'] += 1
        
        if task_result.get('success', False):
            self.performance_metrics['completed_tasks'] += 1
        
        # Update success rate
        self.performance_metrics['success_rate'] = (
            self.performance_metrics['completed_tasks'] / 
            self.performance_metrics['total_tasks']
        )
        
        # Update average response time
        response_time = task_result.get('response_time', 1000)
        current_avg = self.performance_metrics['avg_response_time']
        total_tasks = self.performance_metrics['total_tasks']
        
        self.performance_metrics['avg_response_time'] = (
            (current_avg * (total_tasks - 1) + response_time) / total_tasks
        )
    
    async def heartbeat(self) -> Dict[str, Any]:
        """Send heartbeat with current status"""
        return {
            'agent_id': self.id,
            'name': self.name,
            'status': self.status.value,
            'current_task': self.current_task,
            'performance_metrics': self.performance_metrics,
            'timestamp': datetime.utcnow().isoformat()
        }


class SpecializedAgent(BaseAgent):
    """Specialized agent with domain-specific capabilities"""
    
    def __init__(
        self,
        name: str,
        description: str,
        capabilities: List[str],
        domain: str,
        specialized_tools: List[str] = None,
        **kwargs
    ):
        super().__init__(name, description, capabilities, **kwargs)
        self.domain = domain
        self.specialized_tools = specialized_tools or []
    
    def setup_message_handlers(self):
        """Setup message handlers for specialized agent"""
        self.message_handlers = {
            'task_request': self.handle_task_request,
            'collaboration_request': self.handle_collaboration_request,
            'status_query': self.handle_status_query,
            'capability_query': self.handle_capability_query
        }
    
    async def handle_task_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming task requests"""
        task_data = message.get('content', {})
        
        # Check if we can handle this task
        required_capabilities = task_data.get('required_capabilities', [])
        if not self.can_handle_task(required_capabilities):
            return {
                'type': 'task_rejection',
                'reason': 'Insufficient capabilities',
                'required': required_capabilities,
                'available': self.capabilities
            }
        
        # Accept the task
        self.status = AgentStatus.BUSY
        self.current_task = task_data.get('task_id')
        
        try:
            result = await self.execute_task(task_data)
            self.status = AgentStatus.IDLE
            self.current_task = None
            
            return {
                'type': 'task_completion',
                'result': result,
                'task_id': task_data.get('task_id')
            }
        except Exception as e:
            self.status = AgentStatus.ERROR
            return {
                'type': 'task_error',
                'error': str(e),
                'task_id': task_data.get('task_id')
            }
    
    async def handle_collaboration_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collaboration requests from other agents"""
        request_type = message.get('content', {}).get('request_type')
        
        if request_type == 'expertise_sharing':
            return await self.share_expertise(message.get('content', {}))
        elif request_type == 'joint_task':
            return await self.consider_joint_task(message.get('content', {}))
        else:
            return {
                'type': 'collaboration_response',
                'status': 'unsupported',
                'message': f"Unsupported collaboration type: {request_type}"
            }
    
    async def handle_status_query(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status queries"""
        return {
            'type': 'status_response',
            'status': self.status.value,
            'current_task': self.current_task,
            'capabilities': self.capabilities,
            'performance_metrics': self.performance_metrics
        }
    
    async def handle_capability_query(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle capability queries"""
        return {
            'type': 'capability_response',
            'capabilities': self.capabilities,
            'domain': self.domain,
            'specialized_tools': self.specialized_tools,
            'availability': self.status == AgentStatus.IDLE
        }
    
    def can_handle_task(self, required_capabilities: List[str]) -> bool:
        """Check if agent can handle a task with given requirements"""
        if not required_capabilities:
            return True
        
        agent_caps = set(cap.lower() for cap in self.capabilities)
        required_caps = set(cap.lower() for cap in required_capabilities)
        
        # Check if we have at least 70% of required capabilities
        intersection = agent_caps.intersection(required_caps)
        return len(intersection) >= len(required_caps) * 0.7
    
    async def share_expertise(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Share domain expertise with other agents"""
        topic = request.get('topic')
        
        if not topic:
            return {
                'type': 'expertise_response',
                'status': 'error',
                'message': 'No topic specified'
            }
        
        # Use LLM to generate expertise response
        prompt = f"""
        As a {self.domain} specialist with capabilities in {', '.join(self.capabilities)}, 
        provide expert advice on the following topic: {topic}
        
        Focus on practical insights and actionable recommendations.
        """
        
        try:
            response = await self.llm_client.generate_structured_response(prompt, self.domain)
            return {
                'type': 'expertise_response',
                'status': 'success',
                'topic': topic,
                'advice': response.content,
                'domain': self.domain
            }
        except Exception as e:
            return {
                'type': 'expertise_response',
                'status': 'error',
                'message': f"Failed to generate expertise: {str(e)}"
            }
    
    async def consider_joint_task(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Consider participating in a joint task"""
        task_description = request.get('task_description')
        required_capabilities = request.get('required_capabilities', [])
        
        if self.status != AgentStatus.IDLE:
            return {
                'type': 'collaboration_response',
                'status': 'unavailable',
                'message': 'Currently busy with another task'
            }
        
        if not self.can_handle_task(required_capabilities):
            return {
                'type': 'collaboration_response',
                'status': 'declined',
                'message': 'Insufficient capabilities for this task'
            }
        
        return {
            'type': 'collaboration_response',
            'status': 'accepted',
            'message': 'Ready to collaborate',
            'contribution': self.capabilities
        }
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specialized task using LLM and domain knowledge"""
        start_time = datetime.utcnow()
        
        try:
            task_description = task_data.get('description', '')
            input_data = task_data.get('input_data', {})
            
            # Create domain-specific prompt
            prompt = f"""
            As a {self.domain} specialist with expertise in {', '.join(self.capabilities)}, 
            please complete the following task:
            
            Task: {task_description}
            Input Data: {input_data}
            
            Provide a detailed response with:
            1. Analysis of the task
            2. Step-by-step approach
            3. Final result or recommendation
            4. Confidence level (0-1)
            """
            
            response = await self.llm_client.generate_structured_response(prompt, self.domain)
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            result = {
                'success': True,
                'output': response.content,
                'agent_id': self.id,
                'agent_name': self.name,
                'domain': self.domain,
                'response_time': response_time,
                'timestamp': end_time.isoformat()
            }
            
            self.update_performance_metrics(result)
            return result
            
        except Exception as e:
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            result = {
                'success': False,
                'error': str(e),
                'agent_id': self.id,
                'agent_name': self.name,
                'response_time': response_time,
                'timestamp': end_time.isoformat()
            }
            
            self.update_performance_metrics(result)
            return result
