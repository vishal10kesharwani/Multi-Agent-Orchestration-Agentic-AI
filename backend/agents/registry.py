"""
Agent Registry and Capability Discovery System
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import json
import logging

from backend.database.models import Agent, AgentStatus, ResourceUsage
from backend.database.connection import get_redis_client
from backend.core.config import settings

logger = logging.getLogger(__name__)


class CapabilityMatcher:
    """Matches tasks with agent capabilities"""
    
    @staticmethod
    def calculate_capability_score(agent_capabilities: List[str], required_capabilities: List[str]) -> float:
        """Calculate how well an agent's capabilities match requirements"""
        if not required_capabilities:
            return 1.0
        
        if not agent_capabilities:
            return 0.0
        
        agent_caps = set(cap.lower() for cap in agent_capabilities)
        required_caps = set(cap.lower() for cap in required_capabilities)
        
        # Calculate intersection and union
        intersection = agent_caps.intersection(required_caps)
        union = agent_caps.union(required_caps)
        
        if not union:
            return 0.0
        
        # Jaccard similarity with bonus for exact matches
        jaccard_score = len(intersection) / len(union)
        exact_match_bonus = len(intersection) / len(required_caps) if required_caps else 0
        
        return min(1.0, jaccard_score + (exact_match_bonus * 0.2))
    
    @staticmethod
    def find_best_matches(agents: List[Agent], requirements: Dict[str, Any], top_k: int = 5) -> List[tuple]:
        """Find the best matching agents for given requirements"""
        required_capabilities = requirements.get('capabilities', [])
        priority = requirements.get('priority', 1)
        
        matches = []
        for agent in agents:
            if agent.status != AgentStatus.IDLE.value:
                continue
            
            # Calculate capability score
            capability_score = CapabilityMatcher.calculate_capability_score(
                agent.capabilities or [], required_capabilities
            )
            
            # Calculate performance score
            performance_metrics = agent.performance_metrics or {}
            success_rate = performance_metrics.get('success_rate', 0.5)
            avg_response_time = performance_metrics.get('avg_response_time', 1000)
            
            # Normalize response time (lower is better)
            response_time_score = max(0, 1 - (avg_response_time / 10000))
            
            # Combined score with weights
            total_score = (
                capability_score * 0.6 +
                success_rate * 0.3 +
                response_time_score * 0.1
            )
            
            matches.append((agent, total_score, capability_score))
        
        # Sort by total score (descending)
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:top_k]


class AgentRegistry:
    """Central registry for managing agents and their capabilities"""
    
    def __init__(self):
        self.capability_matcher = CapabilityMatcher()
        self._heartbeat_interval = 30  # seconds
        self._offline_threshold = 120  # seconds
    
    async def register_agent(
        self, 
        session: AsyncSession,
        name: str,
        description: str,
        capabilities: List[str],
        resource_requirements: Dict[str, Any] = None
    ) -> Agent:
        """Register a new agent in the system"""
        
        # Check if agent already exists
        result = await session.execute(
            select(Agent).where(Agent.name == name)
        )
        existing_agent = result.scalar_one_or_none()
        
        if existing_agent:
            # Update existing agent
            existing_agent.description = description
            existing_agent.capabilities = capabilities
            existing_agent.resource_requirements = resource_requirements or {}
            existing_agent.status = AgentStatus.IDLE.value
            existing_agent.last_heartbeat = datetime.utcnow()
            await session.commit()
            logger.info(f"Updated agent: {name}")
            return existing_agent
        
        # Create new agent
        agent = Agent(
            name=name,
            description=description,
            capabilities=capabilities,
            resource_requirements=resource_requirements or {},
            status=AgentStatus.IDLE.value,
            performance_metrics={
                'success_rate': 0.5,
                'avg_response_time': 1000,
                'total_tasks': 0,
                'completed_tasks': 0
            },
            last_heartbeat=datetime.utcnow()
        )
        
        session.add(agent)
        await session.commit()
        await session.refresh(agent)
        
        # Cache agent capabilities in Redis
        # Cache agent capabilities in Redis (optional)
        try:
            redis_client = await get_redis_client()
            if redis_client is not None:
                redis_client.hset(
                    f"agent:{agent.id}:capabilities",
                    mapping={cap: "1" for cap in capabilities}
                )
        except Exception as e:
            logger.warning(f"Skipping Redis capability cache set for agent {agent.id}: {e}")
        
        logger.info(f"Registered new agent: {name} with capabilities: {capabilities}")
        return agent
    
    async def unregister_agent(self, session: AsyncSession, agent_id: int) -> bool:
        """Unregister an agent from the system"""
        result = await session.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            return False
        
        # Update status to offline
        agent.status = AgentStatus.OFFLINE.value
        await session.commit()
        
        # Remove from Redis cache
        try:
            redis_client = await get_redis_client()
            if redis_client is not None:
                redis_client.delete(f"agent:{agent_id}:capabilities")
        except Exception as e:
            logger.warning(f"Skipping Redis capability cache delete for agent {agent_id}: {e}")
        
        logger.info(f"Unregistered agent: {agent.name}")
        return True
    
    async def update_agent_status(
        self, 
        session: AsyncSession, 
        agent_id: int, 
        status: AgentStatus,
        performance_update: Dict[str, Any] = None
    ) -> bool:
        """Update agent status and performance metrics"""
        result = await session.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            return False
        
        agent.status = status.value if hasattr(status, 'value') else status
        agent.last_heartbeat = datetime.utcnow()
        
        if performance_update:
            current_metrics = agent.performance_metrics or {}
            current_metrics.update(performance_update)
            agent.performance_metrics = current_metrics
        
        await session.commit()
        return True
    
    async def heartbeat(self, session: AsyncSession, agent_id: int) -> bool:
        """Update agent heartbeat timestamp"""
        result = await session.execute(
            update(Agent)
            .where(Agent.id == agent_id)
            .values(last_heartbeat=datetime.utcnow())
        )
        await session.commit()
        return result.rowcount > 0
    
    async def get_available_agents(self, session: AsyncSession) -> List[Agent]:
        """Get all available (idle) agents"""
        result = await session.execute(
            select(Agent)
            .where(Agent.status == AgentStatus.IDLE.value)
            .options(selectinload(Agent.tasks))
        )
        return result.scalars().all()
    
    async def find_agents_by_capability(
        self, 
        session: AsyncSession, 
        capabilities: List[str]
    ) -> List[Agent]:
        """Find agents that have specific capabilities"""
        # Try Redis for fast capability lookup; fallback to DB filtering if unavailable
        try:
            redis_client = await get_redis_client()
        except Exception:
            redis_client = None

        if redis_client is not None:
            try:
                candidate_agents: Set[int] = set()
                keys = redis_client.keys("agent:*:capabilities")
                for key in keys:
                    for capability in capabilities:
                        if redis_client.hexists(key, capability):
                            agent_id = int(key.split(':')[1])
                            candidate_agents.add(agent_id)
                if candidate_agents:
                    result = await session.execute(
                        select(Agent)
                        .where(Agent.id.in_(candidate_agents))
                        .where(Agent.status == AgentStatus.IDLE.value)
                    )
                    return result.scalars().all()
            except Exception as e:
                logger.warning(f"Redis capability lookup failed, falling back to DB: {e}")

        # Fallback: fetch idle agents and filter in Python
        result = await session.execute(
            select(Agent).where(Agent.status == AgentStatus.IDLE.value)
        )
        all_idle = result.scalars().all()
        filtered = [
            agent for agent in all_idle
            if agent.capabilities and all(
                cap.lower() in [c.lower() for c in agent.capabilities]
                for cap in capabilities
            )
        ]
        return filtered
    
    async def find_best_agent_for_task(
        self, 
        session: AsyncSession, 
        task_requirements: Dict[str, Any]
    ) -> Optional[Agent]:
        """Find the best agent for a specific task"""
        available_agents = await self.get_available_agents(session)
        
        if not available_agents:
            return None
        
        matches = self.capability_matcher.find_best_matches(
            available_agents, task_requirements, top_k=1
        )
        
        if matches and matches[0][1] > 0.3:  # Minimum score threshold
            return matches[0][0]
        
        return None
    
    async def get_agent_workload(self, session: AsyncSession, agent_id: int) -> Dict[str, Any]:
        """Get current workload information for an agent"""
        # Get recent resource usage
        result = await session.execute(
            select(ResourceUsage)
            .where(ResourceUsage.agent_id == agent_id)
            .order_by(ResourceUsage.recorded_at.desc())
            .limit(1)
        )
        latest_usage = result.scalar_one_or_none()
        
        if not latest_usage:
            return {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'active_tasks': 0,
                'queue_length': 0
            }
        
        return {
            'cpu_usage': latest_usage.cpu_usage or 0.0,
            'memory_usage': latest_usage.memory_usage or 0.0,
            'active_tasks': latest_usage.active_tasks or 0,
            'queue_length': latest_usage.queue_length or 0
        }
    
    async def cleanup_offline_agents(self, session: AsyncSession) -> int:
        """Mark agents as offline if they haven't sent heartbeat recently"""
        threshold = datetime.utcnow() - timedelta(seconds=self._offline_threshold)
        
        result = await session.execute(
            update(Agent)
            .where(Agent.last_heartbeat < threshold)
            .where(Agent.status != AgentStatus.OFFLINE.value)
            .values(status=AgentStatus.OFFLINE.value)
        )
        
        await session.commit()
        offline_count = result.rowcount
        
        if offline_count > 0:
            logger.warning(f"Marked {offline_count} agents as offline due to missing heartbeat")
        
        return offline_count
    
    async def get_capability_statistics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get statistics about available capabilities in the system"""
        result = await session.execute(select(Agent))
        agents = result.scalars().all()
        
        capability_counts = {}
        status_counts = {}
        
        for agent in agents:
            # Count capabilities
            for capability in (agent.capabilities or []):
                capability_counts[capability] = capability_counts.get(capability, 0) + 1
            
            # Count statuses
            status_counts[agent.status] = status_counts.get(agent.status, 0) + 1
        
        return {
            'total_agents': len(agents),
            'capability_distribution': capability_counts,
            'status_distribution': status_counts,
            'unique_capabilities': len(capability_counts)
        }
