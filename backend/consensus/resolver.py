"""
Conflict Resolution and Consensus Building System
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from enum import Enum
import json
import logging
from langchain_openai import ChatOpenAI
import httpx

from backend.database.models import Agent, Task, Message
from backend.communication.message_bus import MessageBus, CommunicationProtocol, MessagePriority
from backend.core.config import settings

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    RESOURCE_CONTENTION = "resource_contention"
    CAPABILITY_OVERLAP = "capability_overlap"
    PRIORITY_DISAGREEMENT = "priority_disagreement"
    APPROACH_DISAGREEMENT = "approach_disagreement"
    DATA_INCONSISTENCY = "data_inconsistency"


class ConsensusMethod(Enum):
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_VOTE = "weighted_vote"
    EXPERT_DECISION = "expert_decision"
    NEGOTIATION = "negotiation"
    ARBITRATION = "arbitration"


class ConflictResolver:
    """Handles conflict detection and resolution between agents"""
    
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.communication = CommunicationProtocol(message_bus)
        self.llm = self._initialize_llm()
        self.active_conflicts: Dict[str, Dict[str, Any]] = {}
    
    def _initialize_llm(self):
        """Initialize LLM client for arbitration with SSL bypass"""
        try:
            import httpx
            import ssl
            from langchain_openai import ChatOpenAI
            
            # Create SSL context that bypasses certificate verification
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create HTTP client with custom SSL context
            http_client = httpx.Client(verify=ssl_context, timeout=30.0)
            
            return ChatOpenAI(
                base_url=settings.OPENAI_API_BASE,
                api_key=settings.OPENAI_API_KEY,
                model=settings.LLM_MODEL,
                temperature=0.3,
                max_tokens=2000,
                http_client=http_client
            )
        except Exception as e:
            logger.warning(f"Failed to initialize LLM client: {e}. Using mock client.")
            return None
    
    async def detect_conflict(
        self,
        session: AsyncSession,
        agents: List[Agent],
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Detect potential conflicts between agents"""
        
        conflicts = []
        
        # Check for resource contention
        resource_conflicts = await self._detect_resource_conflicts(session, agents, context)
        conflicts.extend(resource_conflicts)
        
        # Check for capability overlaps that might cause confusion
        capability_conflicts = await self._detect_capability_conflicts(agents, context)
        conflicts.extend(capability_conflicts)
        
        # Check for priority disagreements
        priority_conflicts = await self._detect_priority_conflicts(session, agents, context)
        conflicts.extend(priority_conflicts)
        
        if conflicts:
            conflict_id = f"conflict_{datetime.utcnow().timestamp()}"
            conflict_data = {
                'id': conflict_id,
                'type': 'multi_conflict',
                'conflicts': conflicts,
                'involved_agents': [agent.id for agent in agents],
                'context': context,
                'detected_at': datetime.utcnow().isoformat(),
                'status': 'detected'
            }
            
            self.active_conflicts[conflict_id] = conflict_data
            logger.warning(f"Conflict detected: {conflict_id} with {len(conflicts)} issues")
            return conflict_data
        
        return None
    
    async def _detect_resource_conflicts(
        self,
        session: AsyncSession,
        agents: List[Agent],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect resource contention conflicts"""
        conflicts = []
        
        # Check if multiple agents are trying to access the same resources
        resource_usage = {}
        
        for agent in agents:
            agent_resources = agent.resource_requirements or {}
            for resource_type, requirement in agent_resources.items():
                if resource_type not in resource_usage:
                    resource_usage[resource_type] = []
                resource_usage[resource_type].append({
                    'agent_id': agent.id,
                    'requirement': requirement
                })
        
        # Identify conflicts
        for resource_type, usage_list in resource_usage.items():
            if len(usage_list) > 1:
                total_requirement = sum(
                    usage['requirement'] for usage in usage_list
                    if isinstance(usage['requirement'], (int, float))
                )
                
                # Assume conflict if total requirement exceeds 100% (for percentage-based resources)
                if total_requirement > 1.0:
                    conflicts.append({
                        'type': ConflictType.RESOURCE_CONTENTION.value,
                        'resource_type': resource_type,
                        'involved_agents': [usage['agent_id'] for usage in usage_list],
                        'total_requirement': total_requirement,
                        'severity': 'high' if total_requirement > 1.5 else 'medium'
                    })
        
        return conflicts
    
    async def _detect_capability_conflicts(
        self,
        agents: List[Agent],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect capability overlap conflicts"""
        conflicts = []
        
        # Group agents by similar capabilities
        capability_groups = {}
        
        for agent in agents:
            agent_caps = set(agent.capabilities or [])
            
            for existing_group_key, group_agents in capability_groups.items():
                existing_caps = set(existing_group_key.split(','))
                
                # Check for significant overlap (>70%)
                intersection = agent_caps.intersection(existing_caps)
                union = agent_caps.union(existing_caps)
                
                if union and len(intersection) / len(union) > 0.7:
                    group_agents.append(agent.id)
                    break
            else:
                # Create new group
                capability_groups[','.join(sorted(agent_caps))] = [agent.id]
        
        # Identify conflicts in groups with multiple agents
        for capabilities, agent_ids in capability_groups.items():
            if len(agent_ids) > 1:
                conflicts.append({
                    'type': ConflictType.CAPABILITY_OVERLAP.value,
                    'capabilities': capabilities.split(','),
                    'involved_agents': agent_ids,
                    'severity': 'low'  # Usually not critical
                })
        
        return conflicts
    
    async def _detect_priority_conflicts(
        self,
        session: AsyncSession,
        agents: List[Agent],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect priority disagreement conflicts"""
        conflicts = []
        
        # This would involve analyzing task priorities and agent preferences
        # For now, we'll implement a basic version
        
        task_id = context.get('task_id')
        if task_id:
            # Get task details
            result = await session.execute(
                select(Task).where(Task.id == task_id)
            )
            task = result.scalar_one_or_none()
            
            if task and task.priority >= 4:  # High priority task
                # Check if any agents are currently working on lower priority tasks
                busy_agents = [agent for agent in agents if agent.status == 'busy']
                
                if busy_agents:
                    conflicts.append({
                        'type': ConflictType.PRIORITY_DISAGREEMENT.value,
                        'high_priority_task': task_id,
                        'busy_agents': [agent.id for agent in busy_agents],
                        'severity': 'medium'
                    })
        
        return conflicts
    
    async def resolve_conflict(
        self,
        session: AsyncSession,
        conflict_id: str,
        resolution_method: ConsensusMethod = ConsensusMethod.NEGOTIATION
    ) -> Dict[str, Any]:
        """Resolve a detected conflict"""
        
        if conflict_id not in self.active_conflicts:
            return {'success': False, 'error': 'Conflict not found'}
        
        conflict_data = self.active_conflicts[conflict_id]
        
        try:
            if resolution_method == ConsensusMethod.NEGOTIATION:
                result = await self._resolve_by_negotiation(session, conflict_data)
            elif resolution_method == ConsensusMethod.MAJORITY_VOTE:
                result = await self._resolve_by_voting(session, conflict_data, weighted=False)
            elif resolution_method == ConsensusMethod.WEIGHTED_VOTE:
                result = await self._resolve_by_voting(session, conflict_data, weighted=True)
            elif resolution_method == ConsensusMethod.EXPERT_DECISION:
                result = await self._resolve_by_expert_decision(session, conflict_data)
            elif resolution_method == ConsensusMethod.ARBITRATION:
                result = await self._resolve_by_arbitration(session, conflict_data)
            else:
                result = {'success': False, 'error': 'Unknown resolution method'}
            
            # Update conflict status
            if result.get('success'):
                conflict_data['status'] = 'resolved'
                conflict_data['resolution'] = result
                conflict_data['resolved_at'] = datetime.utcnow().isoformat()
            else:
                conflict_data['status'] = 'failed'
                conflict_data['resolution_error'] = result.get('error')
            
            return result
            
        except Exception as e:
            logger.error(f"Error resolving conflict {conflict_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _resolve_by_negotiation(
        self,
        session: AsyncSession,
        conflict_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict through agent negotiation"""
        
        involved_agents = conflict_data['involved_agents']
        conflicts = conflict_data['conflicts']
        
        # Create negotiation session
        negotiation_id = f"negotiation_{datetime.utcnow().timestamp()}"
        
        # Send negotiation request to all involved agents
        negotiation_data = {
            'negotiation_id': negotiation_id,
            'conflicts': conflicts,
            'context': conflict_data['context'],
            'participants': involved_agents
        }
        
        responses = []
        for agent_id in involved_agents:
            try:
                response = await self.communication.request_response(
                    session, 0, agent_id,  # 0 as system coordinator
                    'negotiation_request', negotiation_data,
                    timeout=60.0
                )
                responses.append({
                    'agent_id': agent_id,
                    'response': response
                })
            except Exception as e:
                logger.error(f"Failed to get negotiation response from agent {agent_id}: {e}")
        
        # Analyze responses and find common ground
        return await self._analyze_negotiation_responses(responses, conflicts)
    
    async def _analyze_negotiation_responses(
        self,
        responses: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze negotiation responses using LLM"""
        
        prompt = f"""
        Analyze the following negotiation responses to resolve conflicts:
        
        Conflicts: {json.dumps(conflicts, indent=2)}
        Agent Responses: {json.dumps(responses, indent=2)}
        
        Provide a resolution plan in JSON format:
        {{
            "success": true/false,
            "resolution_plan": {{
                "resource_allocation": {{}},
                "task_assignments": {{}},
                "priority_adjustments": {{}},
                "compromise_agreements": []
            }},
            "rationale": "explanation of the resolution",
            "implementation_steps": []
        }}
        
        Focus on finding win-win solutions and fair compromises.
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            resolution = json.loads(response.content.strip())
            return resolution
        except Exception as e:
            logger.error(f"Failed to analyze negotiation responses: {e}")
            return {
                'success': False,
                'error': 'Failed to analyze negotiation responses'
            }
    
    async def _resolve_by_voting(
        self,
        session: AsyncSession,
        conflict_data: Dict[str, Any],
        weighted: bool = False
    ) -> Dict[str, Any]:
        """Resolve conflict through voting"""
        
        involved_agents = conflict_data['involved_agents']
        
        # Get agent details for weighting if needed
        if weighted:
            result = await session.execute(
                select(Agent).where(Agent.id.in_(involved_agents))
            )
            agents = result.scalars().all()
            agent_weights = {
                agent.id: self._calculate_agent_weight(agent)
                for agent in agents
            }
        else:
            agent_weights = {agent_id: 1.0 for agent_id in involved_agents}
        
        # Create voting options based on conflicts
        voting_options = self._generate_voting_options(conflict_data['conflicts'])
        
        # Conduct voting
        votes = {}
        for agent_id in involved_agents:
            try:
                response = await self.communication.request_response(
                    session, 0, agent_id,
                    'voting_request', {
                        'options': voting_options,
                        'conflict_context': conflict_data['context']
                    },
                    timeout=30.0
                )
                
                if response.get('type') == 'vote_response':
                    votes[agent_id] = response.get('selected_option')
            except Exception as e:
                logger.error(f"Failed to get vote from agent {agent_id}: {e}")
        
        # Tally votes
        vote_counts = {}
        for agent_id, option in votes.items():
            weight = agent_weights.get(agent_id, 1.0)
            vote_counts[option] = vote_counts.get(option, 0) + weight
        
        # Determine winner
        if vote_counts:
            winning_option = max(vote_counts, key=vote_counts.get)
            return {
                'success': True,
                'winning_option': winning_option,
                'vote_counts': vote_counts,
                'total_votes': len(votes),
                'method': 'weighted_vote' if weighted else 'majority_vote'
            }
        else:
            return {
                'success': False,
                'error': 'No votes received'
            }
    
    def _calculate_agent_weight(self, agent: Agent) -> float:
        """Calculate voting weight for an agent based on performance"""
        metrics = agent.performance_metrics or {}
        success_rate = metrics.get('success_rate', 0.5)
        total_tasks = metrics.get('total_tasks', 0)
        
        # Weight based on success rate and experience
        experience_factor = min(1.0, total_tasks / 100.0)  # Cap at 100 tasks
        weight = (success_rate * 0.7) + (experience_factor * 0.3)
        
        return max(0.1, weight)  # Minimum weight of 0.1
    
    def _generate_voting_options(self, conflicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate voting options based on conflicts"""
        options = []
        
        for i, conflict in enumerate(conflicts):
            if conflict['type'] == ConflictType.RESOURCE_CONTENTION.value:
                options.extend([
                    {
                        'id': f'resource_option_{i}_1',
                        'description': 'Allocate resources based on task priority',
                        'type': 'resource_allocation'
                    },
                    {
                        'id': f'resource_option_{i}_2',
                        'description': 'Allocate resources equally among agents',
                        'type': 'resource_allocation'
                    },
                    {
                        'id': f'resource_option_{i}_3',
                        'description': 'Queue tasks and allocate resources sequentially',
                        'type': 'resource_allocation'
                    }
                ])
            elif conflict['type'] == ConflictType.CAPABILITY_OVERLAP.value:
                options.extend([
                    {
                        'id': f'capability_option_{i}_1',
                        'description': 'Assign based on agent performance history',
                        'type': 'capability_assignment'
                    },
                    {
                        'id': f'capability_option_{i}_2',
                        'description': 'Collaborate on the task together',
                        'type': 'capability_assignment'
                    }
                ])
        
        return options
    
    async def _resolve_by_expert_decision(
        self,
        session: AsyncSession,
        conflict_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict by consulting the most expert agent"""
        
        involved_agents = conflict_data['involved_agents']
        
        # Get agent details
        result = await session.execute(
            select(Agent).where(Agent.id.in_(involved_agents))
        )
        agents = result.scalars().all()
        
        # Find the most expert agent (highest success rate + most experience)
        expert_agent = max(
            agents,
            key=lambda a: self._calculate_expertise_score(a, conflict_data['conflicts'])
        )
        
        # Ask expert for decision
        try:
            response = await self.communication.request_response(
                session, 0, expert_agent.id,
                'expert_decision_request', {
                    'conflicts': conflict_data['conflicts'],
                    'context': conflict_data['context'],
                    'involved_agents': involved_agents
                },
                timeout=60.0
            )
            
            return {
                'success': True,
                'expert_agent': expert_agent.id,
                'decision': response,
                'method': 'expert_decision'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get expert decision: {str(e)}'
            }
    
    def _calculate_expertise_score(self, agent: Agent, conflicts: List[Dict[str, Any]]) -> float:
        """Calculate expertise score for conflict resolution"""
        metrics = agent.performance_metrics or {}
        success_rate = metrics.get('success_rate', 0.5)
        total_tasks = metrics.get('total_tasks', 0)
        
        # Check if agent has relevant capabilities for the conflicts
        agent_caps = set(agent.capabilities or [])
        relevant_score = 0
        
        for conflict in conflicts:
            if conflict['type'] == ConflictType.CAPABILITY_OVERLAP.value:
                conflict_caps = set(conflict.get('capabilities', []))
                if agent_caps.intersection(conflict_caps):
                    relevant_score += 1
        
        # Combine factors
        experience_score = min(1.0, total_tasks / 100.0)
        relevance_score = relevant_score / max(1, len(conflicts))
        
        return (success_rate * 0.4) + (experience_score * 0.3) + (relevance_score * 0.3)
    
    async def _resolve_by_arbitration(
        self,
        session: AsyncSession,
        conflict_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict through AI arbitration"""
        
        prompt = f"""
        As an AI arbitrator, resolve the following conflict between agents:
        
        Conflict Details: {json.dumps(conflict_data, indent=2)}
        
        Provide a fair and efficient resolution in JSON format:
        {{
            "success": true,
            "arbitration_decision": {{
                "resource_allocation": {{}},
                "task_assignments": {{}},
                "priority_order": [],
                "compensation": {{}}
            }},
            "reasoning": "detailed explanation of the decision",
            "implementation_timeline": [],
            "monitoring_requirements": []
        }}
        
        Consider:
        - Fairness to all parties
        - Efficiency of resource utilization
        - System-wide optimization
        - Precedent for future conflicts
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            decision = json.loads(response.content.strip())
            return decision
        except Exception as e:
            logger.error(f"Failed to generate arbitration decision: {e}")
            return {
                'success': False,
                'error': 'Failed to generate arbitration decision'
            }
    
    async def get_conflict_history(
        self,
        session: AsyncSession,
        agent_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get history of conflicts and their resolutions"""
        
        conflicts = []
        for conflict_id, conflict_data in self.active_conflicts.items():
            if agent_id is None or agent_id in conflict_data.get('involved_agents', []):
                conflicts.append(conflict_data)
        
        # Sort by detection time
        conflicts.sort(key=lambda x: x.get('detected_at', ''), reverse=True)
        
        return conflicts[:limit]
