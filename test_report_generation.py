#!/usr/bin/env python3
"""
Test Report Generation Functionality
"""
import asyncio
import sys
import requests
import json
import time
sys.path.append('.')

from backend.database.connection import init_database, async_session_maker
from backend.database.models import Agent, Task, TaskStatus, AgentStatus
from backend.core.orchestrator import OrchestrationEngine

async def test_report_generation():
    """Test the complete report generation workflow"""
    
    print("🧪 Testing Report Generation Functionality")
    print("=" * 50)
    
    try:
        # Initialize database
        await init_database()
        
        # Create orchestrator
        orchestrator = OrchestrationEngine()
        await orchestrator.initialize()
        
        async with async_session_maker() as session:
            # Test 1: Submit report generation task
            print("\n📝 Test 1: Submitting Report Generation Task")
            
            task_data = {
                "title": "Generate Comprehensive Test Report",
                "description": "Generate a detailed test report with table of contents, introduction, methodology, analysis, results, and conclusions for the multi-agent platform testing",
                "requirements": {
                    "capabilities": ["report_generation", "data_analysis"],
                    "priority": 5
                }
            }
            
            result = await orchestrator.submit_task(session, task_data)
            print(f"✅ Task submitted: {result}")
            
            if result.get('success'):
                task_id = result['task_id']
                
                # Test 2: Check task status
                print(f"\n📊 Test 2: Checking Task Status (ID: {task_id})")
                
                # Wait a moment for processing
                await asyncio.sleep(1)
                
                status = await orchestrator.task_delegator.get_task_progress(session, task_id)
                print(f"Task Status: {status}")
                
                # Test 3: Check agent assignment
                print(f"\n🤖 Test 3: Checking Agent Assignment")
                
                # Get task details
                from sqlalchemy import select
                result = await session.execute(select(Task).where(Task.id == task_id))
                task = result.scalar_one_or_none()
                
                if task:
                    print(f"Task Status: {task.status}")
                    print(f"Assigned Agent: {task.assigned_agent_id}")
                    print(f"Started At: {task.started_at}")
                    print(f"Progress: {task.progress}")
                    
                    if task.assigned_agent:
                        print(f"Agent Name: {task.assigned_agent.name}")
                        print(f"Agent Capabilities: {task.assigned_agent.capabilities}")
                
                return True
            else:
                print(f"❌ Task submission failed: {result.get('error')}")
                return False
                
        await orchestrator.shutdown()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_report_generation():
    """Test report generation via API"""
    
    print("\n🌐 Testing Report Generation via API")
    print("=" * 40)
    
    try:
        # Test API endpoint
        url = "http://localhost:8000/api/v1/tasks/submit"
        
        payload = {
            "title": "API Test Report",
            "description": "Generate a sample report via API for testing purposes with sections: executive summary, technical analysis, performance metrics, and recommendations",
            "requirements": {
                "capabilities": ["report_generation", "data_analysis"],
                "priority": 4
            }
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                task_id = data.get('task_id')
                
                # Check task status via API
                status_url = f"http://localhost:8000/api/v1/tasks/{task_id}"
                status_response = requests.get(status_url, timeout=5)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"📊 Task Status: {json.dumps(status_data, indent=2)}")
                
                return True
            else:
                print(f"❌ API task submission failed: {data}")
                return False
        else:
            print(f"❌ API request failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def check_agent_capabilities():
    """Check available agents and their capabilities"""
    
    print("\n🔍 Checking Available Agents")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:8000/api/v1/agents", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', [])
            
            print(f"Total Agents: {len(agents)}")
            
            report_agents = []
            for agent in agents:
                capabilities = agent.get('capabilities', [])
                if 'report_generation' in capabilities or 'data_analysis' in capabilities:
                    report_agents.append(agent)
                    print(f"✅ {agent['name']}: {capabilities} (Status: {agent['status']})")
                else:
                    print(f"⚠️  {agent['name']}: {capabilities} (No report capabilities)")
            
            if report_agents:
                print(f"\n✅ Found {len(report_agents)} agents capable of report generation")
                return True
            else:
                print("\n❌ No agents found with report generation capabilities")
                return False
        else:
            print(f"❌ Failed to get agents: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Agent check failed: {e}")
        return False

async def register_report_agent():
    """Register a specialized report generation agent"""
    
    print("\n🤖 Registering Report Generation Agent")
    print("=" * 40)
    
    try:
        url = "http://localhost:8000/api/v1/agents/register"
        
        agent_data = {
            "name": "ReportGenerator-004",
            "description": "Specialized agent for generating comprehensive reports and documentation",
            "capabilities": [
                "report_generation",
                "data_analysis", 
                "document_creation",
                "data_presentation",
                "statistical_analysis"
            ],
            "resource_requirements": {
                "cpu": 0.4,
                "memory": 0.5
            }
        }
        
        response = requests.post(url, json=agent_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent registered: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Agent registration failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Agent registration failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🚀 Report Generation Test Suite")
        print("=" * 50)
        
        # Step 1: Check existing agents
        agents_ok = check_agent_capabilities()
        
        # Step 2: Register report agent if needed
        if not agents_ok:
            await register_report_agent()
            time.sleep(1)  # Wait for registration
        
        # Step 3: Test via API
        api_ok = test_api_report_generation()
        
        # Step 4: Test via direct orchestrator
        direct_ok = await test_report_generation()
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 TEST SUMMARY")
        print("=" * 50)
        print(f"Agent Capabilities: {'✅ PASS' if agents_ok else '❌ FAIL'}")
        print(f"API Report Generation: {'✅ PASS' if api_ok else '❌ FAIL'}")
        print(f"Direct Report Generation: {'✅ PASS' if direct_ok else '❌ FAIL'}")
        
        if api_ok and direct_ok:
            print("\n🎉 Report Generation is WORKING!")
            return True
        else:
            print("\n❌ Report Generation has issues")
            return False
    
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
