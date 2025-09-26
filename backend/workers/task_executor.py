"""
Task Execution Worker - Actually executes tasks assigned to agents
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.database.connection import async_session_maker, init_database
from backend.database.models import Task, Agent, TaskStatus, AgentStatus
from backend.agents.base_agent import SpecializedAgent
from backend.core.config import settings

logger = logging.getLogger(__name__)


class TaskExecutor:
    """Executes tasks assigned to agents"""
    
    def __init__(self):
        self.running = False
        self.execution_interval = 10  # seconds
        
    async def start(self):
        """Start the task executor"""
        self.running = True
        logger.info("Task executor started")
        
        while self.running:
            try:
                await self.process_pending_tasks()
                await asyncio.sleep(self.execution_interval)
            except Exception as e:
                logger.error(f"Error in task execution loop: {e}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """Stop the task executor"""
        self.running = False
        logger.info("Task executor stopped")
    
    async def process_pending_tasks(self):
        """Process all in-progress tasks"""
        async with async_session_maker() as session:
            try:
                # Get all in-progress tasks with assigned agents
                result = await session.execute(
                    select(Task, Agent)
                    .join(Agent, Task.assigned_agent_id == Agent.id)
                    .where(Task.status == TaskStatus.IN_PROGRESS.value)
                    .where(Task.assigned_agent_id.isnot(None))
                )
                
                tasks_and_agents = result.all()
                
                if tasks_and_agents:
                    logger.info(f"Processing {len(tasks_and_agents)} in-progress tasks")
                
                for task, agent in tasks_and_agents:
                    try:
                        await self.execute_task(session, task, agent)
                    except Exception as e:
                        logger.error(f"Failed to execute task {task.id}: {e}")
                        await self.mark_task_failed(session, task, str(e))
                
                await session.commit()
                
            except Exception as e:
                logger.error(f"Error processing pending tasks: {e}")
                await session.rollback()
    
    async def execute_task(self, session: AsyncSession, task: Task, agent: Agent):
        """Execute a specific task using the assigned agent"""
        
        # Create specialized agent instance
        specialized_agent = SpecializedAgent(
            name=agent.name,
            description=agent.description,
            capabilities=agent.capabilities,
            domain=self.get_agent_domain(agent.capabilities)
        )
        specialized_agent.id = agent.id
        
        # Prepare task data
        task_data = {
            'task_id': task.id,
            'title': task.title,
            'description': task.description,
            'input_data': task.input_data or {},
            'required_capabilities': task.requirements.get('capabilities', []) if task.requirements else []
        }
        
        logger.info(f"Executing task {task.id} '{task.title}' with agent {agent.name}")
        
        # Execute the task
        result = await specialized_agent.execute_task(task_data)
        
        if result.get('success'):
            # Task completed successfully
            await self.mark_task_completed(session, task, result)
            logger.info(f"Task {task.id} completed successfully by {agent.name}")
        else:
            # Task failed
            error_msg = result.get('error', 'Unknown error')
            await self.mark_task_failed(session, task, error_msg)
            logger.error(f"Task {task.id} failed: {error_msg}")
    
    async def mark_task_completed(self, session: AsyncSession, task: Task, result: Dict[str, Any]):
        """Mark a task as completed with results"""
        task.status = TaskStatus.COMPLETED.value
        task.progress = 1.0
        task.completed_at = datetime.utcnow()
        task.output_data = {
            'result': result.get('output', ''),
            'agent_name': result.get('agent_name'),
            'domain': result.get('domain'),
            'response_time': result.get('response_time'),
            'timestamp': result.get('timestamp')
        }
        
        # Update agent status back to idle
        if task.assigned_agent:
            task.assigned_agent.status = AgentStatus.IDLE.value
            task.assigned_agent.last_heartbeat = datetime.utcnow()
    
    async def mark_task_failed(self, session: AsyncSession, task: Task, error_message: str):
        """Mark a task as failed"""
        task.status = TaskStatus.FAILED.value
        task.error_message = error_message
        task.retry_count += 1
        
        # Update agent status back to idle
        if task.assigned_agent:
            task.assigned_agent.status = AgentStatus.IDLE.value
            task.assigned_agent.last_heartbeat = datetime.utcnow()
    
    def get_agent_domain(self, capabilities: List[str]) -> str:
        """Determine agent domain based on capabilities"""
        if not capabilities:
            return "general"
        
        domain_mapping = {
            'data_analysis': 'data_science',
            'statistical_modeling': 'data_science',
            'data_visualization': 'data_science',
            'text_analysis': 'natural_language',
            'sentiment_analysis': 'natural_language',
            'language_translation': 'natural_language',
            'web_scraping': 'web_automation',
            'data_extraction': 'web_automation',
            'api_integration': 'web_automation',
            'report_generation': 'documentation',
            'document_creation': 'documentation'
        }
        
        # Find the most common domain
        domains = [domain_mapping.get(cap, 'general') for cap in capabilities]
        domain_counts = {}
        for domain in domains:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        return max(domain_counts, key=domain_counts.get) if domain_counts else 'general'


class TaskExecutorService:
    """Service to manage task executor"""
    
    def __init__(self):
        self.executor = TaskExecutor()
        self.task = None
    
    async def start(self):
        """Start the task executor service"""
        if not self.task:
            self.task = asyncio.create_task(self.executor.start())
            logger.info("Task executor service started")
    
    async def stop(self):
        """Stop the task executor service"""
        if self.task:
            await self.executor.stop()
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
            logger.info("Task executor service stopped")


# Global task executor service instance
task_executor_service = TaskExecutorService()
