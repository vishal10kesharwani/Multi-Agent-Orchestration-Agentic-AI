"""
Task Decomposition and Delegation System
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
import json
import logging
from langchain_openai import ChatOpenAI
import httpx

from backend.database.models import Task, TaskStatus, Agent
from backend.agents.registry import AgentRegistry
from backend.core.config import settings

logger = logging.getLogger(__name__)


class TaskDecomposer:
    """Intelligent task decomposition using LLM"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.agent_registry = AgentRegistry()
    
    def _initialize_llm(self):
        """Initialize LLM client with SSL bypass for TCS GenAI Lab"""
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
                temperature=0.1,
                max_tokens=3000,
                http_client=http_client
            )
        except Exception as e:
            logger.warning(f"Failed to initialize LLM client: {e}. Using heuristic fallback.")
            return None
    
    async def analyze_task_complexity(self, task_description: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task complexity and determine if decomposition is needed"""
        
        # If LLM is not available, use simple heuristics
        if self.llm is None:
            return self._analyze_complexity_heuristic(task_description, requirements)
        
        prompt = f"""
        Analyze the following task and determine its complexity:
        
        Task Description: {task_description}
        Requirements: {json.dumps(requirements, indent=2)}
        
        Provide analysis in the following JSON format:
        {{
            "complexity_score": <1-10 scale>,
            "requires_decomposition": <true/false>,
            "estimated_duration": <minutes>,
            "required_capabilities": [<list of capabilities>],
            "potential_challenges": [<list of challenges>],
            "decomposition_strategy": "<strategy if decomposition needed>"
        }}
        
        Consider factors like:
        - Number of different skills/domains required
        - Sequential vs parallel execution possibilities
        - Data dependencies between subtasks
        - Resource requirements
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            # Parse JSON response
            analysis = json.loads(response.content.strip())
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing task complexity: {e}")
            return {
                "complexity_score": 5,
                "requires_decomposition": False,
                "reasoning": "Error in analysis",
                "estimated_agents": 1,
                "estimated_time": 300,
                "required_capabilities": requirements.get('capabilities', []),
                "potential_challenges": [],
                "decomposition_strategy": "none"
            }
    
    def _analyze_complexity_heuristic(self, task_description: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Simple heuristic-based complexity analysis when LLM is not available"""
        
        # Simple scoring based on task characteristics
        score = 1
        
        # Check for multiple capabilities required
        capabilities = requirements.get('capabilities', [])
        if len(capabilities) > 1:
            score += 2
        
        # Check for multi-agent flag
        if requirements.get('multi_agent', False):
            score += 3
        
        # Check task description length and complexity keywords
        description_lower = task_description.lower()
        complex_keywords = ['analyze', 'research', 'comprehensive', 'multiple', 'complex', 'detailed']
        score += sum(1 for keyword in complex_keywords if keyword in description_lower)
        
        # Cap at 10
        score = min(score, 10)
        
        return {
            "complexity_score": score,
            "requires_decomposition": score >= 6,
            "reasoning": f"Heuristic analysis based on {len(capabilities)} capabilities and task keywords",
            "estimated_agents": max(1, len(capabilities)),
            "estimated_time": score * 60,
            "required_capabilities": capabilities,
            "potential_challenges": [],
            "decomposition_strategy": "none"
        }
    
    async def decompose_task(self, task_description: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Decompose a complex task into smaller subtasks"""
        
        prompt = f"""
        Decompose the following complex task into smaller, manageable subtasks:
        
        Task Description: {task_description}
        Requirements: {json.dumps(requirements, indent=2)}
        
        Create a list of subtasks in JSON format:
        {{
            "subtasks": [
                {{
                    "title": "<subtask title>",
                    "description": "<detailed description>",
                    "required_capabilities": [<list of capabilities>],
                    "priority": <1-5>,
                    "estimated_duration": <minutes>,
                    "dependencies": [<list of subtask indices this depends on>],
                    "input_requirements": [<what inputs are needed>],
                    "output_deliverables": [<what outputs will be produced>]
                }}
            ],
            "execution_strategy": "<sequential/parallel/hybrid>",
            "integration_requirements": "<how to combine results>"
        }}
        
        Guidelines:
        - Each subtask should be focused on a single capability/domain
        - Consider dependencies between subtasks
        - Ensure subtasks can be executed by different agents
        - Include clear input/output specifications
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            decomposition = json.loads(response.content.strip())
            return decomposition.get('subtasks', [])
        except Exception as e:
            logger.error(f"Failed to decompose task: {e}")
            return []
    
    async def create_execution_plan(
        self, 
        subtasks: List[Dict[str, Any]], 
        available_agents: List[Agent]
    ) -> Dict[str, Any]:
        """Create an execution plan for subtasks with agent assignments"""
        
        agent_info = []
        for agent in available_agents:
            agent_info.append({
                "id": agent.id,
                "name": agent.name,
                "capabilities": agent.capabilities or [],
                "performance_metrics": agent.performance_metrics or {}
            })
        
        prompt = f"""
        Create an execution plan for the following subtasks with available agents:
        
        Subtasks: {json.dumps(subtasks, indent=2)}
        Available Agents: {json.dumps(agent_info, indent=2)}
        
        Provide an execution plan in JSON format:
        {{
            "execution_phases": [
                {{
                    "phase_number": 1,
                    "parallel_tasks": [
                        {{
                            "subtask_index": 0,
                            "assigned_agent_id": <agent_id>,
                            "estimated_start": "<relative time>",
                            "estimated_completion": "<relative time>"
                        }}
                    ]
                }}
            ],
            "critical_path": [<list of subtask indices>],
            "total_estimated_duration": <minutes>,
            "resource_requirements": {{
                "concurrent_agents": <number>,
                "peak_memory": <estimate>,
                "network_intensive": <true/false>
            }}
        }}
        
        Consider:
        - Agent capabilities matching subtask requirements
        - Task dependencies and execution order
        - Load balancing across agents
        - Critical path optimization
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            plan = json.loads(response.content.strip())
            return plan
        except Exception as e:
            logger.error(f"Failed to create execution plan: {e}")
            return {
                "execution_phases": [],
                "critical_path": [],
                "total_estimated_duration": 60,
                "resource_requirements": {}
            }
    
    async def delegate_task(self, session: AsyncSession, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for task delegation - creates task and assigns to agent"""
        try:
            # Create the task in database
            task = Task(
                title=task_data.get('title', 'Untitled Task'),
                description=task_data.get('description', ''),
                requirements=task_data.get('requirements', {}),
                priority=self._convert_priority(task_data.get('priority', 'medium')),
                input_data=task_data.get('input_data', {}),
                status=TaskStatus.PENDING.value
            )
            
            session.add(task)
            await session.flush()  # Get the task ID
            
            # Analyze task complexity
            analysis = await self.analyze_task_complexity(
                task.description, task.requirements or {}
            )
            
            if not analysis.get('requires_decomposition', False):
                # Simple task - assign to single agent
                result = await self._assign_simple_task(session, task, analysis)
            else:
                # Complex task - decompose and delegate
                result = await self._delegate_complex_task(session, task, analysis)
            
            await session.commit()
            return result
                
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to delegate task: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _convert_priority(self, priority_str: str) -> int:
        """Convert string priority to integer"""
        priority_map = {
            'low': 1,
            'medium': 3,
            'high': 5
        }
        return priority_map.get(priority_str.lower(), 3)
    
    async def _assign_simple_task(
        self, 
        session: AsyncSession, 
        task: Task, 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assign a simple task to a single agent"""
        
        # Find best agent for the task
        best_agent = await self.agent_registry.find_best_agent_for_task(
            session, task.requirements or {}
        )
        
        if not best_agent:
            return {
                'success': False,
                'error': 'No suitable agent available',
                'task_id': task.id,
                'required_capabilities': analysis.get('required_capabilities', [])
            }
        
        # Assign task to agent
        task.assigned_agent_id = best_agent.id
        task.status = TaskStatus.IN_PROGRESS.value
        task.started_at = datetime.utcnow()
        
        # Update agent status
        await self.agent_registry.update_agent_status(
            session, best_agent.id, "busy"
        )
        
        return {
            'success': True,
            'task_id': task.id,
            'assigned_agent': {
                'id': best_agent.id,
                'name': best_agent.name,
                'capabilities': best_agent.capabilities
            },
            'execution_type': 'simple',
            'estimated_duration': analysis.get('estimated_duration', 60),
            'delegation_result': {
                'assigned_agent': {
                    'id': best_agent.id,
                    'name': best_agent.name,
                    'capabilities': best_agent.capabilities
                }
            }
        }
    
    async def _delegate_complex_task(
        self, 
        session: AsyncSession, 
        task: Task, 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Delegate a complex task by decomposing it into subtasks"""
        
        # For now, fallback to simple assignment for complex tasks
        # This can be enhanced later with actual decomposition
        return await self._assign_simple_task(session, task, analysis)


class TaskDelegator:
    """Handles task delegation and agent assignment"""
    
    def __init__(self):
        self.agent_registry = AgentRegistry()
        self.task_decomposer = TaskDecomposer()
    
    async def delegate_task(
        self, 
        session: AsyncSession, 
        task: Task
    ) -> Dict[str, Any]:
        """Delegate a task to appropriate agents"""
        
        try:
            # Analyze task complexity
            analysis = await self.task_decomposer.analyze_task_complexity(
                task.description, task.requirements or {}
            )
            
            if not analysis.get('requires_decomposition', False):
                # Simple task - assign to single agent
                return await self._assign_simple_task(session, task, analysis)
            else:
                # Complex task - decompose and delegate
                return await self._delegate_complex_task(session, task, analysis)
                
        except Exception as e:
            logger.error(f"Failed to delegate task {task.id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_id': task.id
            }
    
    async def _assign_simple_task(
        self, 
        session: AsyncSession, 
        task: Task, 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assign a simple task to a single agent"""
        
        # Find best agent for the task
        best_agent = await self.agent_registry.find_best_agent_for_task(
            session, task.requirements or {}
        )
        
        if not best_agent:
            return {
                'success': False,
                'error': 'No suitable agent available',
                'task_id': task.id,
                'required_capabilities': analysis.get('required_capabilities', [])
            }
        
        # Assign task to agent
        task.assigned_agent_id = best_agent.id
        task.status = TaskStatus.IN_PROGRESS.value
        task.started_at = datetime.utcnow()
        
        # Update agent status
        await self.agent_registry.update_agent_status(
            session, best_agent.id, best_agent.status
        )
        
        await session.commit()
        
        return {
            'success': True,
            'task_id': task.id,
            'assigned_agent': {
                'id': best_agent.id,
                'name': best_agent.name,
                'capabilities': best_agent.capabilities
            },
            'execution_type': 'simple',
            'estimated_duration': analysis.get('estimated_duration', 60)
        }
    
    async def _delegate_complex_task(
        self, 
        session: AsyncSession, 
        task: Task, 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Delegate a complex task by decomposing it into subtasks"""
        
        # Decompose the task
        subtasks_data = await self.task_decomposer.decompose_task(
            task.description, task.requirements or {}
        )
        
        if not subtasks_data:
            # Fallback to simple assignment
            return await self._assign_simple_task(session, task, analysis)
        
        # Get available agents
        available_agents = await self.agent_registry.get_available_agents(session)
        
        if len(available_agents) < len(subtasks_data):
            logger.warning(f"Not enough agents for optimal task decomposition. "
                         f"Need {len(subtasks_data)}, have {len(available_agents)}")
        
        # Create execution plan
        execution_plan = await self.task_decomposer.create_execution_plan(
            subtasks_data, available_agents
        )
        
        # Create subtasks in database
        created_subtasks = []
        for i, subtask_data in enumerate(subtasks_data):
            subtask = Task(
                title=subtask_data.get('title', f"Subtask {i+1}"),
                description=subtask_data.get('description', ''),
                requirements={
                    'capabilities': subtask_data.get('required_capabilities', []),
                    'priority': subtask_data.get('priority', 1)
                },
                priority=subtask_data.get('priority', 1),
                parent_task_id=task.id,
                input_data=subtask_data.get('input_requirements', {}),
                status=TaskStatus.PENDING.value
            )
            
            session.add(subtask)
            created_subtasks.append(subtask)
        
        await session.commit()
        
        # Assign agents to subtasks based on execution plan
        assignments = []
        for phase in execution_plan.get('execution_phases', []):
            for parallel_task in phase.get('parallel_tasks', []):
                subtask_index = parallel_task.get('subtask_index')
                agent_id = parallel_task.get('assigned_agent_id')
                
                if subtask_index < len(created_subtasks) and agent_id:
                    subtask = created_subtasks[subtask_index]
                    subtask.assigned_agent_id = agent_id
                    subtask.status = TaskStatus.PENDING.value
                    
                    assignments.append({
                        'subtask_id': subtask.id,
                        'agent_id': agent_id,
                        'estimated_start': parallel_task.get('estimated_start'),
                        'estimated_completion': parallel_task.get('estimated_completion')
                    })
        
        # Update parent task status
        task.status = TaskStatus.IN_PROGRESS.value
        task.started_at = datetime.utcnow()
        
        await session.commit()
        
        return {
            'success': True,
            'task_id': task.id,
            'execution_type': 'complex',
            'subtasks_created': len(created_subtasks),
            'assignments': assignments,
            'execution_plan': execution_plan,
            'estimated_duration': execution_plan.get('total_estimated_duration', 120)
        }
    
    async def reassign_failed_task(
        self, 
        session: AsyncSession, 
        task_id: int,
        failure_reason: str
    ) -> Dict[str, Any]:
        """Reassign a failed task to another agent"""
        
        # Get the failed task
        result = await session.execute(
            select(Task).where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if not task:
            return {'success': False, 'error': 'Task not found'}
        
        # Increment retry count
        task.retry_count += 1
        
        if task.retry_count >= settings.TASK_RETRY_LIMIT:
            task.status = TaskStatus.FAILED.value
            task.error_message = f"Max retries exceeded. Last failure: {failure_reason}"
            await session.commit()
            
            return {
                'success': False,
                'error': 'Max retries exceeded',
                'task_id': task_id,
                'retry_count': task.retry_count
            }
        
        # Find alternative agent (exclude the failed one)
        excluded_agent_id = task.assigned_agent_id
        available_agents = await self.agent_registry.get_available_agents(session)
        
        # Filter out the failed agent
        alternative_agents = [
            agent for agent in available_agents 
            if agent.id != excluded_agent_id
        ]
        
        if not alternative_agents:
            return {
                'success': False,
                'error': 'No alternative agents available',
                'task_id': task_id
            }
        
        # Use capability matcher to find best alternative
        matches = self.agent_registry.capability_matcher.find_best_matches(
            alternative_agents, task.requirements or {}, top_k=1
        )
        
        if not matches or matches[0][1] < 0.3:
            return {
                'success': False,
                'error': 'No suitable alternative agent found',
                'task_id': task_id
            }
        
        # Assign to new agent
        new_agent = matches[0][0]
        task.assigned_agent_id = new_agent.id
        task.status = TaskStatus.PENDING.value
        task.error_message = None
        
        await session.commit()
        
        return {
            'success': True,
            'task_id': task_id,
            'new_agent': {
                'id': new_agent.id,
                'name': new_agent.name,
                'capabilities': new_agent.capabilities
            },
            'retry_count': task.retry_count
        }
    
    async def get_task_progress(self, session: AsyncSession, task_id: int) -> Dict[str, Any]:
        """Get progress information for a task and its subtasks"""
        
        result = await session.execute(
            select(Task)
            .where(Task.id == task_id)
            .options(selectinload(Task.subtasks))
        )
        task = result.scalar_one_or_none()
        
        if not task:
            return {'error': 'Task not found'}
        
        # Calculate progress for complex tasks with subtasks
        if task.subtasks:
            total_subtasks = len(task.subtasks)
            completed_subtasks = sum(
                1 for subtask in task.subtasks 
                if subtask.status == TaskStatus.COMPLETED.value
            )
            in_progress_subtasks = sum(
                1 for subtask in task.subtasks 
                if subtask.status == TaskStatus.IN_PROGRESS.value
            )
            failed_subtasks = sum(
                1 for subtask in task.subtasks 
                if subtask.status == TaskStatus.FAILED.value
            )
            
            overall_progress = completed_subtasks / total_subtasks if total_subtasks > 0 else 0
            
            return {
                'task_id': task_id,
                'status': task.status,
                'overall_progress': overall_progress,
                'subtask_summary': {
                    'total': total_subtasks,
                    'completed': completed_subtasks,
                    'in_progress': in_progress_subtasks,
                    'failed': failed_subtasks,
                    'pending': total_subtasks - completed_subtasks - in_progress_subtasks - failed_subtasks
                },
                'subtasks': [
                    {
                        'id': subtask.id,
                        'title': subtask.title,
                        'status': subtask.status,
                        'progress': subtask.progress,
                        'assigned_agent_id': subtask.assigned_agent_id
                    }
                    for subtask in task.subtasks
                ]
            }
        else:
            # Simple task
            return {
                'task_id': task_id,
                'status': task.status,
                'progress': task.progress,
                'assigned_agent_id': task.assigned_agent_id,
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None
            }
