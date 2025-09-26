"""
Orchestration Engine - Central coordinator for multi-agent system
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.communication.message_bus import MessageBus
from backend.scheduling.load_balancer import LoadBalancer
from backend.monitoring.metrics import MetricsCollector
from backend.workers.auto_task_executor import AutoTaskExecutor
from backend.database.connection import get_db_session
from backend.database.models import Task, Agent, TaskStatus
from backend.tasks.decomposer import TaskDecomposer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.agents.registry import AgentRegistry
logger = logging.getLogger(__name__)


class OrchestrationEngine:
    """Main orchestration engine for coordinating agents and tasks"""
    
    def __init__(self):
        self.message_bus = MessageBus()
        self.load_balancer = LoadBalancer()
        self.metrics_collector = MetricsCollector()
        self.auto_executor = AutoTaskExecutor()
        self.task_decomposer = TaskDecomposer()
        self.agent_registry = AgentRegistry()
        self.running = False
        self._orchestration_task = None
        
    async def initialize(self):
        """Initialize the orchestration engine"""
        try:
            logger.info("Initializing orchestration engine...")
            
            # Initialize message bus
            await self.message_bus.initialize()
            
            # Start load balancer
            await self.load_balancer.start()
            
            # Start auto task executor
            await self.auto_executor.start()
            
            # Start metrics collection
            await self.metrics_collector.start()
            
            # Start main orchestration loop
            self.running = True
            self._orchestration_task = asyncio.create_task(self._orchestration_loop())
            
            logger.info("Orchestration engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestration engine: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the orchestration engine"""
        try:
            logger.info("Shutting down orchestration engine...")
            
            self.running = False
            
            if self._orchestration_task:
                self._orchestration_task.cancel()
                try:
                    await self._orchestration_task
                except asyncio.CancelledError:
                    pass
            
            # Stop auto task executor
            await self.auto_executor.stop()
            
            # Stop other services
            await self.load_balancer.stop()
            await self.metrics_collector.stop()
            await self.message_bus.shutdown()
            
            logger.info("Orchestration engine shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during orchestration engine shutdown: {e}")
    
    async def _orchestration_loop(self):
        """Main orchestration loop"""
        while self.running:
            try:
                # Orchestration logic runs in background
                await asyncio.sleep(10)  # Check every 10 seconds
                
                # The auto executor handles task processing automatically
                # This loop can be used for other orchestration tasks
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in orchestration loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def submit_task(self, session: AsyncSession, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a new task to the system"""
        try:
            # Use task decomposer to handle task submission and delegation
            result = await self.task_decomposer.delegate_task(session, task_data)
            
            if result.get('success'):
                logger.info(f"Task submitted successfully: {result.get('task_id')}")
            else:
                logger.warning(f"Task submission failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error submitting task: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_task_status(self, session: AsyncSession, task_id: int) -> Dict[str, Any]:
        """Get task status and progress"""
        try:
            result = await session.execute(
                select(Task).where(Task.id == task_id)
            )
            task = result.scalar_one_or_none()
            
            if not task:
                return {
                    'success': False,
                    'error': 'Task not found'
                }
            
            return {
                'success': True,
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'status': task.status,
                    'progress': task.progress,
                    'assigned_agent_id': task.assigned_agent_id,
                    'created_at': task.created_at.isoformat() if task.created_at else None,
                    'updated_at': task.updated_at.isoformat() if task.updated_at else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting task status: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def register_agent(self, session: AsyncSession, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new agent via the AgentRegistry (wrapper for API routes)."""
        try:
            agent = await self.agent_registry.register_agent(
                session,
                name=agent_data.get('name', ''),
                description=agent_data.get('description', ''),
                capabilities=agent_data.get('capabilities', []),
                resource_requirements=agent_data.get('resource_requirements', {})
            )
            return {
                'success': True,
                'agent_id': agent.id,
                'agent': {
                    'id': agent.id,
                    'name': agent.name,
                    'capabilities': agent.capabilities,
                    'status': agent.status
                }
            }
        except Exception as e:
            logger.error(f"Error registering agent: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Global orchestrator instance
_orchestrator_instance = None

async def get_orchestrator() -> OrchestrationEngine:
    """Get the global orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = OrchestrationEngine()
    return _orchestrator_instance
