"""
Inter-Agent Communication System with Message Bus
"""
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
import redis
import logging
from enum import Enum

from backend.database.models import Message, MessageType, Agent
from backend.database.connection import get_redis_client
from backend.core.config import settings

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class MessageBus:
    """Central message bus for inter-agent communication"""
    
    def __init__(self):
        self.subscribers: Dict[str, Set[Callable]] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.redis_client = None
        self.running = False
        self._subscription_task = None
    
    async def initialize(self):
        """Initialize the message bus"""
        try:
            self.redis_client = await get_redis_client()
            self.running = True
            if self.redis_client:
                self._subscription_task = asyncio.create_task(self._listen_for_messages())
            logger.info("Message bus initialized")
        except Exception as e:
            logger.warning(f"Message bus initialization failed: {e}. Continuing without Redis.")
            self.running = True
    
    async def shutdown(self):
        """Shutdown the message bus"""
        try:
            self.running = False
            if self._subscription_task:
                self._subscription_task.cancel()
                try:
                    await self._subscription_task
                except asyncio.CancelledError:
                    pass
            logger.info("Message bus shut down")
        except Exception as e:
            logger.error(f"Error shutting down message bus: {e}")
    
    async def _listen_for_messages(self):
        """Listen for messages from Redis"""
        if not self.redis_client:
            return
            
        try:
            while self.running:
                # Simple message listening implementation
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in message listener: {e}")
    
    async def send_message(
        self,
        session: AsyncSession,
        sender_id: int,
        receiver_id: int,
        message_type: str,
        content: Dict[str, Any],
        task_id: Optional[int] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: Optional[str] = None
    ) -> str:
        """Send a message between agents"""
        
        # Generate correlation ID if not provided
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Create message in database
        message = Message(
            message_type=message_type,
            content=content,
            sender_id=sender_id,
            receiver_id=receiver_id,
            task_id=task_id,
            priority=priority.value,
            correlation_id=correlation_id
        )
        
        session.add(message)
        await session.commit()
        await session.refresh(message)
        
        # Send via Redis for real-time delivery
        message_data = {
            'id': message.id,
            'type': message_type,
            'content': content,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'task_id': task_id,
            'priority': priority.value,
            'correlation_id': correlation_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Publish to receiver's channel
        await self.redis_client.publish(
            f"agent:{receiver_id}:messages",
            json.dumps(message_data)
        )
        
        # Also publish to global message channel for monitoring
        await self.redis_client.publish(
            "global:messages",
            json.dumps(message_data)
        )
        
        logger.debug(f"Message sent: {sender_id} -> {receiver_id} ({message_type})")
        return correlation_id
    
    async def broadcast_message(
        self,
        session: AsyncSession,
        sender_id: int,
        message_type: str,
        content: Dict[str, Any],
        recipient_filter: Optional[Dict[str, Any]] = None,
        task_id: Optional[int] = None,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> List[str]:
        """Broadcast a message to multiple agents"""
        
        # Get recipient agents based on filter
        query = select(Agent)
        
        if recipient_filter:
            # Apply filters (e.g., capabilities, status)
            if 'capabilities' in recipient_filter:
                required_caps = recipient_filter['capabilities']
                # This would need a more sophisticated query for JSON field matching
                # For now, we'll get all agents and filter in Python
                pass
            
            if 'status' in recipient_filter:
                query = query.where(Agent.status == recipient_filter['status'])
        
        result = await session.execute(query)
        recipients = result.scalars().all()
        
        # Filter by capabilities if specified
        if recipient_filter and 'capabilities' in recipient_filter:
            required_caps = set(recipient_filter['capabilities'])
            recipients = [
                agent for agent in recipients
                if agent.capabilities and set(agent.capabilities).intersection(required_caps)
            ]
        
        # Send to each recipient
        correlation_ids = []
        for recipient in recipients:
            if recipient.id != sender_id:  # Don't send to self
                correlation_id = await self.send_message(
                    session, sender_id, recipient.id, message_type,
                    content, task_id, priority
                )
                correlation_ids.append(correlation_id)
        
        logger.info(f"Broadcast message sent to {len(correlation_ids)} agents")
        return correlation_ids
    
    async def subscribe_to_messages(self, agent_id: int, handler: Callable):
        """Subscribe an agent to receive messages"""
        channel = f"agent:{agent_id}:messages"
        
        if channel not in self.subscribers:
            self.subscribers[channel] = set()
        
        self.subscribers[channel].add(handler)
        
        # Subscribe to Redis channel
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(channel)
        
        logger.debug(f"Agent {agent_id} subscribed to messages")
    
    async def unsubscribe_from_messages(self, agent_id: int, handler: Callable):
        """Unsubscribe an agent from messages"""
        channel = f"agent:{agent_id}:messages"
        
        if channel in self.subscribers:
            self.subscribers[channel].discard(handler)
            
            if not self.subscribers[channel]:
                del self.subscribers[channel]
        
        logger.debug(f"Agent {agent_id} unsubscribed from messages")
    
    async def _handle_redis_message(self, redis_message):
        """Handle incoming Redis messages"""
        try:
            channel = redis_message['channel'].decode('utf-8')
            data = json.loads(redis_message['data'].decode('utf-8'))
            
            # Route to appropriate handlers
            if channel in self.subscribers:
                for handler in self.subscribers[channel]:
                    try:
                        await handler(data)
                    except Exception as e:
                        logger.error(f"Error in message handler: {e}")
        
        except Exception as e:
            logger.error(f"Error handling Redis message: {e}")
    
    async def get_message_history(
        self,
        session: AsyncSession,
        agent_id: int,
        limit: int = 50,
        message_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get message history for an agent"""
        
        query = select(Message).where(
            (Message.sender_id == agent_id) | (Message.receiver_id == agent_id)
        )
        
        if message_type:
            query = query.where(Message.message_type == message_type)
        
        query = query.order_by(Message.created_at.desc()).limit(limit)
        
        result = await session.execute(query)
        messages = result.scalars().all()
        
        return [
            {
                'id': msg.id,
                'type': msg.message_type,
                'content': msg.content,
                'sender_id': msg.sender_id,
                'receiver_id': msg.receiver_id,
                'task_id': msg.task_id,
                'priority': msg.priority,
                'correlation_id': msg.correlation_id,
                'created_at': msg.created_at.isoformat(),
                'is_read': msg.is_read
            }
            for msg in messages
        ]
    
    async def mark_message_as_read(
        self,
        session: AsyncSession,
        message_id: int,
        reader_id: int
    ) -> bool:
        """Mark a message as read"""
        
        result = await session.execute(
            update(Message)
            .where(Message.id == message_id)
            .where(Message.receiver_id == reader_id)
            .values(is_read=True, read_at=datetime.utcnow())
        )
        
        await session.commit()
        return result.rowcount > 0


class CommunicationProtocol:
    """High-level communication protocols for common interaction patterns"""
    
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.pending_requests: Dict[str, asyncio.Future] = {}
    
    async def request_response(
        self,
        session: AsyncSession,
        sender_id: int,
        receiver_id: int,
        request_type: str,
        request_data: Dict[str, Any],
        timeout: float = 30.0,
        task_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send a request and wait for response"""
        
        correlation_id = str(uuid.uuid4())
        
        # Create future for response
        response_future = asyncio.Future()
        self.pending_requests[correlation_id] = response_future
        
        # Send request
        await self.message_bus.send_message(
            session, sender_id, receiver_id, request_type,
            request_data, task_id, MessagePriority.NORMAL, correlation_id
        )
        
        try:
            # Wait for response with timeout
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            return {
                'success': False,
                'error': 'Request timeout',
                'correlation_id': correlation_id
            }
        finally:
            # Clean up
            self.pending_requests.pop(correlation_id, None)
    
    async def handle_response(self, response_message: Dict[str, Any]):
        """Handle incoming response messages"""
        correlation_id = response_message.get('correlation_id')
        
        if correlation_id in self.pending_requests:
            future = self.pending_requests[correlation_id]
            if not future.done():
                future.set_result(response_message)
    
    async def negotiate_task_assignment(
        self,
        session: AsyncSession,
        coordinator_id: int,
        candidate_agents: List[int],
        task_requirements: Dict[str, Any],
        timeout: float = 60.0
    ) -> Dict[str, Any]:
        """Negotiate task assignment among multiple agents"""
        
        # Send capability queries to all candidates
        responses = []
        
        for agent_id in candidate_agents:
            try:
                response = await self.request_response(
                    session, coordinator_id, agent_id,
                    'capability_query', task_requirements, timeout=10.0
                )
                responses.append({
                    'agent_id': agent_id,
                    'response': response
                })
            except Exception as e:
                logger.error(f"Failed to query agent {agent_id}: {e}")
        
        # Evaluate responses and select best agent
        best_agent = None
        best_score = 0
        
        for response_data in responses:
            response = response_data['response']
            if response.get('type') == 'capability_response':
                # Calculate suitability score
                capabilities = response.get('capabilities', [])
                availability = response.get('availability', False)
                
                if availability:
                    # Simple scoring based on capability match
                    required_caps = set(task_requirements.get('capabilities', []))
                    agent_caps = set(capabilities)
                    
                    if required_caps:
                        score = len(required_caps.intersection(agent_caps)) / len(required_caps)
                    else:
                        score = 1.0
                    
                    if score > best_score:
                        best_score = score
                        best_agent = response_data['agent_id']
        
        if best_agent:
            # Send task assignment to selected agent
            assignment_response = await self.request_response(
                session, coordinator_id, best_agent,
                'task_assignment', task_requirements, timeout=timeout
            )
            
            return {
                'success': True,
                'assigned_agent': best_agent,
                'assignment_response': assignment_response,
                'negotiation_score': best_score
            }
        else:
            return {
                'success': False,
                'error': 'No suitable agent found',
                'responses': responses
            }
    
    async def coordinate_multi_agent_task(
        self,
        session: AsyncSession,
        coordinator_id: int,
        participating_agents: List[int],
        coordination_plan: Dict[str, Any],
        timeout: float = 300.0
    ) -> Dict[str, Any]:
        """Coordinate execution of a multi-agent task"""
        
        # Send coordination plan to all participants
        coordination_id = str(uuid.uuid4())
        
        # Broadcast coordination plan
        await self.message_bus.broadcast_message(
            session, coordinator_id, 'coordination_plan',
            {
                'coordination_id': coordination_id,
                'plan': coordination_plan,
                'participants': participating_agents
            },
            recipient_filter={'agent_ids': participating_agents}
        )
        
        # Monitor execution progress
        start_time = datetime.utcnow()
        completed_agents = set()
        failed_agents = set()
        
        while len(completed_agents) + len(failed_agents) < len(participating_agents):
            # Check for timeout
            if (datetime.utcnow() - start_time).total_seconds() > timeout:
                return {
                    'success': False,
                    'error': 'Coordination timeout',
                    'completed_agents': list(completed_agents),
                    'failed_agents': list(failed_agents)
                }
            
            # Wait for status updates (this would be implemented with proper event handling)
            await asyncio.sleep(1)
        
        return {
            'success': len(failed_agents) == 0,
            'completed_agents': list(completed_agents),
            'failed_agents': list(failed_agents),
            'coordination_id': coordination_id
        }
