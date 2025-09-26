#!/usr/bin/env python3
"""
Task Completion Script - Actually completes tasks using LLM
"""
import asyncio
import sys
import json
from datetime import datetime
sys.path.append('.')

from backend.database.connection import init_database, async_session_maker
from backend.database.models import Task, Agent, TaskStatus, AgentStatus
from backend.agents.base_agent import SpecializedAgent
from sqlalchemy import select

async def complete_all_tasks():
    """Complete all in-progress tasks"""
    
    print("🔄 Completing In-Progress Tasks...")
    
    try:
        # Initialize database
        await init_database()
        
        async with async_session_maker() as session:
            # Get all in-progress tasks with assigned agents
            result = await session.execute(
                select(Task, Agent)
                .join(Agent, Task.assigned_agent_id == Agent.id)
                .where(Task.status == TaskStatus.IN_PROGRESS.value)
                .where(Task.assigned_agent_id.isnot(None))
            )
            
            tasks_and_agents = result.all()
            
            if not tasks_and_agents:
                print("❌ No in-progress tasks found")
                return False
            
            print(f"📋 Found {len(tasks_and_agents)} in-progress tasks")
            
            for task, agent in tasks_and_agents:
                try:
                    print(f"\n🤖 Processing Task {task.id}: '{task.title}' with {agent.name}")
                    
                    # Create specialized agent
                    domain = get_agent_domain(agent.capabilities)
                    specialized_agent = SpecializedAgent(
                        name=agent.name,
                        description=agent.description,
                        capabilities=agent.capabilities,
                        domain=domain
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
                    
                    # Execute the task
                    result = await specialized_agent.execute_task(task_data)
                    
                    if result.get('success'):
                        # Mark task as completed
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
                        
                        # Update agent status
                        agent.status = AgentStatus.IDLE.value
                        agent.last_heartbeat = datetime.utcnow()
                        
                        print(f"✅ Task {task.id} completed successfully")
                        print(f"📄 Result preview: {result.get('output', '')[:100]}...")
                        
                    else:
                        # Mark task as failed
                        error_msg = result.get('error', 'Unknown error')
                        task.status = TaskStatus.FAILED.value
                        task.error_message = error_msg
                        task.retry_count += 1
                        
                        # Update agent status
                        agent.status = AgentStatus.IDLE.value
                        agent.last_heartbeat = datetime.utcnow()
                        
                        print(f"❌ Task {task.id} failed: {error_msg}")
                
                except Exception as e:
                    print(f"❌ Error processing task {task.id}: {e}")
                    # Mark as failed
                    task.status = TaskStatus.FAILED.value
                    task.error_message = str(e)
                    agent.status = AgentStatus.IDLE.value
            
            await session.commit()
            print(f"\n✅ Processed {len(tasks_and_agents)} tasks")
            return True
            
    except Exception as e:
        print(f"❌ Error completing tasks: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_agent_domain(capabilities):
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

async def check_task_status():
    """Check current task status"""
    
    print("\n📊 Current Task Status:")
    print("=" * 30)
    
    try:
        await init_database()
        
        async with async_session_maker() as session:
            result = await session.execute(select(Task))
            tasks = result.scalars().all()
            
            status_counts = {}
            for task in tasks:
                status = task.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in status_counts.items():
                print(f"{status.upper()}: {count}")
            
            # Show recent tasks
            print(f"\nRecent Tasks:")
            for task in tasks[-5:]:
                print(f"  ID {task.id}: {task.title} - {task.status}")
                if task.status == TaskStatus.COMPLETED.value and task.output_data:
                    result_preview = task.output_data.get('result', '')[:50]
                    print(f"    Result: {result_preview}...")
            
            return True
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🚀 Task Completion System")
        print("=" * 30)
        
        # Check current status
        await check_task_status()
        
        # Complete tasks
        success = await complete_all_tasks()
        
        # Check status again
        print("\n" + "=" * 30)
        await check_task_status()
        
        if success:
            print("\n🎉 Tasks completed successfully!")
        else:
            print("\n❌ Task completion had issues")
        
        return success
    
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
