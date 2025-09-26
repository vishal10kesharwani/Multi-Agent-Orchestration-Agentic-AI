#!/usr/bin/env python3
"""
Populate Data and Run Server Persistently
This script will populate the database with sample data and keep the server running
"""
import asyncio
import uvicorn
import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# Add project to path
project_dir = Path("/home/labuser/Desktop/Project/ai-openhack-2025/2792672_AiProject")
sys.path.insert(0, str(project_dir))

from backend.database.connection import init_database, async_session_maker
from backend.database.models import Agent, Task, TaskStatus, AgentStatus
from backend.database.seed import seed_agents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def populate_sample_data():
    """Populate database with comprehensive sample data"""
    print("🔧 Populating database with sample data...")
    
    try:
        # Initialize database
        await init_database()
        
        async with async_session_maker() as session:
            # Seed default agents
            created_agents = await seed_agents(session)
            print(f"✅ Seeded {created_agents} default agents")
            
            # Add more sample agents
            additional_agents = [
                {
                    "name": "WebScraper-Agent",
                    "description": "Specialized in web scraping and data extraction from websites",
                    "capabilities": ["web_scraping", "data_extraction", "content_parsing"],
                    "status": "idle"
                },
                {
                    "name": "CodeAnalyzer-Agent", 
                    "description": "Analyzes code, performs reviews, and suggests improvements",
                    "capabilities": ["code_analysis", "code_review", "debugging"],
                    "status": "idle"
                },
                {
                    "name": "ImageProcessor-Agent",
                    "description": "Processes images, performs OCR, and image analysis",
                    "capabilities": ["image_processing", "ocr", "computer_vision"],
                    "status": "idle"
                }
            ]
            
            agents_created = 0
            for agent_data in additional_agents:
                # Check if agent already exists
                from sqlalchemy import select
                result = await session.execute(
                    select(Agent).where(Agent.name == agent_data["name"])
                )
                existing = result.scalar_one_or_none()
                
                if not existing:
                    agent = Agent(
                        name=agent_data["name"],
                        description=agent_data["description"],
                        capabilities=agent_data["capabilities"],
                        status=agent_data["status"],
                        performance_metrics={"success_rate": 0.95, "tasks_completed": 0},
                        resource_requirements={"cpu": 0.2, "memory": 0.3},
                        last_heartbeat=datetime.utcnow()
                    )
                    session.add(agent)
                    agents_created += 1
            
            # Add sample tasks
            sample_tasks = [
                {
                    "title": "Market Research Analysis",
                    "description": "Conduct comprehensive market research on AI tools and generate insights report",
                    "priority": 4,
                    "requirements": {"capabilities": ["web_research", "data_analysis", "report_generation"]},
                    "status": "pending"
                },
                {
                    "title": "Customer Sentiment Analysis",
                    "description": "Analyze customer feedback from multiple sources and identify sentiment trends",
                    "priority": 3,
                    "requirements": {"capabilities": ["text_analysis", "sentiment_analysis"]},
                    "status": "pending"
                },
                {
                    "title": "Code Quality Assessment",
                    "description": "Review codebase for quality, security issues, and performance optimizations",
                    "priority": 2,
                    "requirements": {"capabilities": ["code_analysis", "code_review"]},
                    "status": "pending"
                },
                {
                    "title": "Data Visualization Dashboard",
                    "description": "Create interactive dashboard with charts and graphs from sales data",
                    "priority": 3,
                    "requirements": {"capabilities": ["data_analysis", "visualization", "report_generation"]},
                    "status": "pending"
                },
                {
                    "title": "Website Content Extraction",
                    "description": "Extract product information from e-commerce websites for price comparison",
                    "priority": 2,
                    "requirements": {"capabilities": ["web_scraping", "data_extraction"]},
                    "status": "pending"
                }
            ]
            
            tasks_created = 0
            for task_data in sample_tasks:
                task = Task(
                    title=task_data["title"],
                    description=task_data["description"],
                    priority=task_data["priority"],
                    requirements=task_data["requirements"],
                    status=task_data["status"],
                    input_data={"created_by": "system", "sample": True},
                    progress=0.0
                )
                session.add(task)
                tasks_created += 1
            
            await session.commit()
            
            print(f"✅ Created {agents_created} additional agents")
            print(f"✅ Created {tasks_created} sample tasks")
            print(f"✅ Database populated successfully!")
            
            # Show summary
            from sqlalchemy import func
            agent_count = await session.execute(select(func.count(Agent.id)))
            task_count = await session.execute(select(func.count(Task.id)))
            
            print(f"📊 Total agents in database: {agent_count.scalar()}")
            print(f"📊 Total tasks in database: {task_count.scalar()}")
            
    except Exception as e:
        print(f"❌ Error populating data: {e}")
        raise

async def start_auto_task_processing():
    """Start background task processing"""
    print("🤖 Starting automatic task processing...")
    
    try:
        from backend.core.orchestrator import OrchestrationEngine
        
        orchestrator = OrchestrationEngine()
        await orchestrator.initialize()
        
        # Process some pending tasks automatically
        async with async_session_maker() as session:
            from sqlalchemy import select
            
            # Get pending tasks
            result = await session.execute(
                select(Task).where(Task.status == TaskStatus.PENDING.value).limit(3)
            )
            pending_tasks = result.scalars().all()
            
            # Get available agents
            agent_result = await session.execute(
                select(Agent).where(Agent.status == AgentStatus.IDLE.value)
            )
            available_agents = agent_result.scalars().all()
            
            if pending_tasks and available_agents:
                print(f"🔄 Processing {len(pending_tasks)} pending tasks...")
                
                for i, task in enumerate(pending_tasks):
                    if i < len(available_agents):
                        agent = available_agents[i]
                        
                        # Assign task to agent
                        task.assigned_agent_id = agent.id
                        task.status = TaskStatus.IN_PROGRESS.value
                        task.started_at = datetime.utcnow()
                        task.progress = 0.5
                        
                        # Update agent status
                        agent.status = AgentStatus.BUSY.value
                        agent.last_heartbeat = datetime.utcnow()
                        
                        print(f"✅ Assigned task '{task.title}' to {agent.name}")
                
                await session.commit()
                print("✅ Task assignments completed!")
        
        await orchestrator.shutdown()
        
    except Exception as e:
        print(f"❌ Error in task processing: {e}")

def run_server():
    """Run the FastAPI server persistently"""
    print("🚀 Starting Multi-Agent Platform Server...")
    print("=" * 60)
    print("🌐 Server will be available at: http://localhost:8000")
    print("📊 Dashboard: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Change to project directory
        os.chdir(project_dir)
        
        # Run the server
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload for stability
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

async def main():
    """Main execution function"""
    print("🎯 MULTI-AGENT PLATFORM - POPULATE & RUN")
    print("=" * 60)
    
    try:
        # Step 1: Populate database
        await populate_sample_data()
        
        # Step 2: Process some initial tasks
        await start_auto_task_processing()
        
        print("\n✅ Data population completed!")
        print("🚀 Starting persistent server...")
        print("\nYour platform now has:")
        print("  • Multiple specialized agents")
        print("  • Sample tasks with various priorities")
        print("  • Active task assignments")
        print("  • Real-time dashboard data")
        
        # Step 3: Start server (this will run indefinitely)
        run_server()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
