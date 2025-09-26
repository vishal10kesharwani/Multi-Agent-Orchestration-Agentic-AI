"""
Database seeding utilities
"""
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.database.models import Agent

# Exactly 5 types of AI agents as specified in requirements
DEFAULT_AGENTS: List[Dict[str, Any]] = [
    {
        "name": "Research-Agent",
        "description": "Specialized in information gathering, web research, data collection, and comprehensive reporting with fact verification.",
        "capabilities": ["web_research", "data_collection", "fact_verification", "report_generation", "information_analysis"],
        "status": "idle",
        "agent_type": "research"
    },
    {
        "name": "Data-Analysis-Agent", 
        "description": "Expert in statistical analysis, data processing, trend analysis, and generating quantitative insights from complex datasets.",
        "capabilities": ["data_analysis", "statistical_modeling", "trend_analysis", "data_visualization", "pattern_recognition"],
        "status": "idle",
        "agent_type": "data_analysis"
    },
    {
        "name": "NLP-Agent",
        "description": "Natural Language Processing specialist for text analysis, sentiment detection, entity extraction, and language understanding.",
        "capabilities": ["text_analysis", "sentiment_analysis", "entity_extraction", "text_summarization", "language_understanding"],
        "status": "idle", 
        "agent_type": "nlp"
    },
    {
        "name": "Planning-Agent",
        "description": "Strategic planning and coordination specialist for task decomposition, resource allocation, and workflow optimization.",
        "capabilities": ["task_planning", "resource_allocation", "workflow_optimization", "project_coordination", "strategy_development"],
        "status": "idle",
        "agent_type": "planning"
    },
    {
        "name": "Synthesis-Agent",
        "description": "Integration specialist for combining results from multiple agents, conflict resolution, and creating final deliverables.",
        "capabilities": ["result_synthesis", "conflict_resolution", "report_integration", "quality_assurance", "final_deliverable_creation"],
        "status": "idle",
        "agent_type": "synthesis"
    }
]


async def seed_agents(session: AsyncSession) -> int:
    """Seed exactly 5 types of AI agents if none exist. Returns number of agents created."""
    result = await session.execute(select(func.count(Agent.id)))
    count = int(result.scalar() or 0)
    if count > 0:
        return 0

    created = 0
    for agent_data in DEFAULT_AGENTS:
        agent = Agent(
            name=agent_data["name"],
            description=agent_data["description"],
            capabilities=agent_data["capabilities"],
            status=agent_data["status"],
            performance_metrics={
                "success_rate": 0.95, 
                "tasks_completed": 0,
                "avg_response_time": 2500,
                "specialization_score": 0.9,
                "agent_type": agent_data["agent_type"]
            },
            resource_requirements={
                "cpu": 0.3, 
                "memory": 0.25,
                "priority": "medium",
                "max_concurrent_tasks": 3
            },
            last_heartbeat=datetime.utcnow()
        )
        session.add(agent)
        created += 1

    await session.commit()
    return created
