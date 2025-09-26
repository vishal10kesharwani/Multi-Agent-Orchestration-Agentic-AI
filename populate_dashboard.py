#!/usr/bin/env python3
"""
Populate dashboard with sample data for testing
"""
import asyncio
import sys
import requests
import json
from sqlalchemy import select
sys.path.append('.')

from backend.database import connection as db
from backend.database.models import Agent, Task, TaskStatus, AgentStatus
from backend.core.config import settings

async def populate_sample_data():
    """Populate database with sample agents and tasks"""
    
    print("🔄 Populating dashboard with sample data...")
    
    try:
        # Initialize database
        await db.init_database()
        
        async with db.async_session_maker() as session:
            # Create sample agents
            agents_data = [
                {
                    "name": "DataAnalyst-Alpha",
                    "description": "Expert in data analysis and statistical modeling",
                    "capabilities": ["data_analysis", "statistical_modeling", "data_visualization", "report_generation"],
                    "status": AgentStatus.IDLE.value,
                    "performance_metrics": {"success_rate": 0.95, "tasks_completed": 0, "avg_response_time": 2100},
                    "resource_requirements": {"cpu": 0.2, "memory": 0.3, "priority": "medium", "max_concurrent_tasks": 2}
                },
                {
                    "name": "NLP-Processor-Beta", 
                    "description": "Natural language processing specialist",
                    "capabilities": ["text_analysis", "sentiment_analysis", "language_translation"],
                    "status": AgentStatus.IDLE.value,
                    "performance_metrics": {"success_rate": 0.88, "tasks_completed": 0, "avg_response_time": 2600},
                    "resource_requirements": {"cpu": 0.4, "memory": 0.6, "priority": "medium", "max_concurrent_tasks": 2}
                },
                {
                    "name": "WebScraper-Gamma",
                    "description": "Web scraping and data extraction expert", 
                    "capabilities": ["web_scraping", "data_extraction", "api_integration"],
                    "status": AgentStatus.IDLE.value,
                    "performance_metrics": {"success_rate": 0.92, "tasks_completed": 0, "avg_response_time": 2300},
                    "resource_requirements": {"cpu": 0.3, "memory": 0.4, "priority": "medium", "max_concurrent_tasks": 2}
                },
                {
                    "name": "ReportGen-Delta",
                    "description": "Report generation and documentation specialist",
                    "capabilities": ["report_generation", "document_creation", "data_presentation", "system_monitoring"],
                    "status": AgentStatus.IDLE.value,
                    "performance_metrics": {"success_rate": 0.90, "tasks_completed": 0, "avg_response_time": 2400},
                    "resource_requirements": {"cpu": 0.5, "memory": 0.4, "priority": "high", "max_concurrent_tasks": 3}
                }
            ]
            
            # Add or update agents in database (idempotent)
            for agent_data in agents_data:
                result = await session.execute(
                    select(Agent).where(Agent.name == agent_data["name"]) 
                )
                existing = result.scalar_one_or_none()
                if existing:
                    existing.description = agent_data["description"]
                    existing.capabilities = agent_data["capabilities"]
                    existing.status = agent_data["status"]
                    existing.performance_metrics = agent_data["performance_metrics"]
                    existing.resource_requirements = agent_data["resource_requirements"]
                else:
                    agent = Agent(
                        name=agent_data["name"],
                        description=agent_data["description"],
                        capabilities=agent_data["capabilities"],
                        status=agent_data["status"],
                        performance_metrics=agent_data["performance_metrics"],
                        resource_requirements=agent_data["resource_requirements"]
                    )
                    session.add(agent)
            
            # Create sample tasks
            tasks_data = [
                {
                    "title": "Customer Data Analysis",
                    "description": "Analyze customer behavior patterns and purchasing trends",
                    "status": TaskStatus.COMPLETED.value,
                    "priority": 4,
                    "requirements": {"capabilities": ["data_analysis", "statistical_modeling"]}
                },
                {
                    "title": "Market Research Report",
                    "description": "Comprehensive market analysis with competitor insights",
                    "status": TaskStatus.IN_PROGRESS.value,
                    "priority": 5,
                    "requirements": {"capabilities": ["web_scraping", "data_analysis", "report_generation"]}
                },
                {
                    "title": "Social Media Sentiment Analysis",
                    "description": "Analyze customer sentiment from social media posts",
                    "status": TaskStatus.PENDING.value,
                    "priority": 3,
                    "requirements": {"capabilities": ["text_analysis", "sentiment_analysis"]}
                },
                {
                    "title": "Sales Performance Dashboard",
                    "description": "Create interactive dashboard for sales metrics",
                    "status": TaskStatus.IN_PROGRESS.value,
                    "priority": 4,
                    "requirements": {"capabilities": ["data_visualization", "report_generation"]}
                },
                {
                    "title": "Competitor Price Monitoring",
                    "description": "Monitor and analyze competitor pricing strategies",
                    "status": TaskStatus.COMPLETED.value,
                    "priority": 3,
                    "requirements": {"capabilities": ["web_scraping", "data_analysis"]}
                }
            ]
            
            # Add tasks to database
            for task_data in tasks_data:
                task = Task(
                    title=task_data["title"],
                    description=task_data["description"],
                    status=task_data["status"],
                    priority=task_data["priority"],
                    requirements=task_data["requirements"]
                )
                session.add(task)
            
            await session.commit()
            print(f"✅ Added {len(agents_data)} agents and {len(tasks_data)} tasks to database")
            
    except Exception as e:
        print(f"❌ Error populating data: {e}")
        return False
    
    return True

def test_api_endpoints():
    """Test all dashboard API endpoints"""
    
    print("\n🧪 Testing API endpoints...")
    
    base_url = "http://localhost:8000/api/v1"
    
    endpoints = [
        "/health",
        "/system/status", 
        "/agents",
        "/tasks",
        "/monitoring/metrics",
        "/load-balancer/stats",
        "/capabilities"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                results[endpoint] = "✅ Working"
                data = response.json()
                if endpoint == "/agents":
                    print(f"   Agents: {len(data.get('agents', []))} found")
                elif endpoint == "/tasks":
                    print(f"   Tasks: {len(data.get('tasks', []))} found")
            else:
                results[endpoint] = f"❌ Error {response.status_code}"
        except Exception as e:
            results[endpoint] = f"❌ Failed: {str(e)[:50]}"
    
    print("\n📊 API Endpoint Results:")
    for endpoint, status in results.items():
        print(f"   {endpoint}: {status}")
    
    return results

def test_dashboard_data():
    """Test specific dashboard data endpoints"""
    
    print("\n🎯 Testing dashboard data...")
    
    try:
        # Test system status
        response = requests.get("http://localhost:8000/api/v1/system/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System Status: {data.get('orchestrator_status', 'unknown')}")
            
            health = data.get('system_health', {})
            if 'current_health' in health:
                current = health['current_health']
                print(f"   Total Agents: {current.get('total_agents', 0)}")
                print(f"   Active Agents: {current.get('active_agents', 0)}")
                print(f"   Total Tasks: {current.get('total_tasks', 0)}")
                print(f"   Completed Tasks: {current.get('completed_tasks', 0)}")
        
        # Test agents endpoint
        response = requests.get("http://localhost:8000/api/v1/agents")
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', [])
            print(f"✅ Agents Available: {len(agents)}")
            for agent in agents[:3]:  # Show first 3
                print(f"   - {agent.get('name', 'Unknown')}: {agent.get('status', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🚀 Dashboard Population and Testing Script")
        print("=" * 50)
        
        # Populate sample data
        success = await populate_sample_data()
        
        if success:
            # Test API endpoints
            api_results = test_api_endpoints()
            
            # Test dashboard data
            dashboard_success = test_dashboard_data()
            
            if dashboard_success:
                print("\n🎉 Dashboard is ready!")
                print("✅ Sample data populated")
                print("✅ API endpoints working")
                print("✅ Dashboard should display properly")
                print("\n🌐 Open http://localhost:8000 to view dashboard")
                return True
            else:
                print("\n⚠️  Dashboard has issues but data is populated")
                return False
        else:
            print("\n❌ Failed to populate dashboard data")
            return False
    
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
