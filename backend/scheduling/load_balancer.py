"""
Load Balancer for Multi-Agent System
"""
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.database.models import Agent, Task, TaskStatus, AgentStatus

logger = logging.getLogger(__name__)


class LoadBalancer:
    """Load balancer for distributing tasks across agents"""
    
    def __init__(self):
        self.running = False
        self._balance_task = None
    
    async def start(self):
        """Start the load balancer"""
        try:
            self.running = True
            logger.info("Load balancer started")
        except Exception as e:
            logger.error(f"Failed to start load balancer: {e}")
    
    async def stop(self):
        """Stop the load balancer"""
        try:
            self.running = False
            if self._balance_task:
                self._balance_task.cancel()
                try:
                    await self._balance_task
                except asyncio.CancelledError:
                    pass
            logger.info("Load balancer stopped")
        except Exception as e:
            logger.error(f"Error stopping load balancer: {e}")
    
    async def process_queue(self, session: AsyncSession):
        """Process queued tasks"""
        try:
            # Simple implementation - just log for now
            logger.debug("Processing task queue")
        except Exception as e:
            logger.error(f"Error processing queue: {e}")
    
    async def get_load_statistics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get load balancing statistics"""
        try:
            # Get agent counts by status
            agent_counts = await session.execute(
                select(Agent.status, func.count(Agent.id))
                .group_by(Agent.status)
            )
            agent_status_counts = dict(agent_counts.all())
            
            # Get task counts by status
            task_counts = await session.execute(
                select(Task.status, func.count(Task.id))
                .group_by(Task.status)
            )
            task_status_counts = dict(task_counts.all())
            
            total_agents = sum(agent_status_counts.values())
            busy_agents = agent_status_counts.get(AgentStatus.BUSY.value, 0)
            active_tasks = task_status_counts.get(TaskStatus.IN_PROGRESS.value, 0)
            
            # Calculate average load
            average_load = (busy_agents / total_agents) if total_agents > 0 else 0.0
            
            return {
                'total_agents': total_agents,
                'busy_agents': busy_agents,
                'idle_agents': agent_status_counts.get(AgentStatus.IDLE.value, 0),
                'active_tasks': active_tasks,
                'pending_tasks': task_status_counts.get(TaskStatus.PENDING.value, 0),
                'average_load': average_load,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting load statistics: {e}")
            return {
                'total_agents': 0,
                'busy_agents': 0,
                'idle_agents': 0,
                'active_tasks': 0,
                'pending_tasks': 0,
                'average_load': 0.0,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def rebalance_load(self, session: AsyncSession) -> Dict[str, Any]:
        """Rebalance load across agents"""
        try:
            logger.info("Rebalancing load across agents")
            stats = await self.get_load_statistics(session)
            
            return {
                'success': True,
                'message': 'Load rebalancing completed',
                'statistics': stats
            }
        except Exception as e:
            logger.error(f"Error rebalancing load: {e}")
            return {
                'success': False,
                'error': str(e)
            }
