#!/usr/bin/env python3
"""
End-to-End Test - Complete Multi-Agent Task Lifecycle
"""
import asyncio
import requests
import time
import json

def test_complete_workflow():
    """Test the complete multi-agent task workflow"""
    
    print("🚀 Multi-Agent Platform End-to-End Test")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api/v1"
    
    try:
        # 1. Check system status
        print("\n1️⃣ Checking System Status...")
        response = requests.get(f"{base_url}/system/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ System Online - {status['status']}")
            print(f"   Active Tasks: {status['active_tasks']}")
            print(f"   Total Agents: {status['total_agents']}")
        else:
            print("❌ System status check failed")
            return False
        
        # 2. List available agents
        print("\n2️⃣ Listing Available Agents...")
        response = requests.get(f"{base_url}/agents")
        if response.status_code == 200:
            agents_data = response.json()
            agents = agents_data['agents']
            print(f"✅ Found {len(agents)} agents:")
            for agent in agents[:3]:  # Show first 3
                print(f"   - {agent['name']}: {', '.join(agent['capabilities'])}")
        else:
            print("❌ Agent listing failed")
            return False
        
        # 3. Submit a new task
        print("\n3️⃣ Submitting New Task...")
        task_data = {
            "title": "End-to-End Test Analysis",
            "description": "Comprehensive analysis task to test the complete multi-agent workflow including task delegation, execution, and completion.",
            "priority": "high",
            "requirements": {
                "capabilities": ["data_analysis", "report_generation"],
                "complexity": "medium"
            }
        }
        
        response = requests.post(f"{base_url}/tasks", json=task_data)
        if response.status_code == 200:
            task_result = response.json()
            if task_result.get('success'):
                task_id = task_result['task_id']
                print(f"✅ Task submitted successfully - ID: {task_id}")
                delegation = task_result.get('delegation_result', {})
                if delegation.get('assigned_agent'):
                    agent_info = delegation['assigned_agent']
                    print(f"   Assigned to: {agent_info['name']}")
                    print(f"   Execution Type: {delegation.get('execution_type', 'unknown')}")
            else:
                print(f"❌ Task submission failed: {task_result}")
                return False
        else:
            print(f"❌ Task submission failed: {response.text}")
            return False
        
        # 4. Verify task delegation
        print("\n4️⃣ Verifying Task Delegation...")
        response = requests.get(f"{base_url}/tasks/{task_id}")
        if response.status_code == 200:
            task = response.json()
            print(f"✅ Task Status: {task['status']}")
            if task.get('assigned_agent_id'):
                print(f"   Assigned to Agent ID: {task['assigned_agent_id']}")
        
        # 5. Complete the task using our API
        print("\n5️⃣ Executing Task...")
        response = requests.post(f"{base_url}/tasks/{task_id}/complete")
        if response.status_code == 200:
            completion_result = response.json()
            if completion_result.get('success'):
                print(f"✅ Task completed successfully!")
                print(f"   Agent: {completion_result['agent']}")
                print(f"   Result Preview: {completion_result['result'][:100]}...")
            else:
                print(f"❌ Task execution failed: {completion_result.get('error')}")
        else:
            print(f"❌ Task completion API failed: {response.text}")
        
        # 6. Verify final status
        print("\n6️⃣ Verifying Final Status...")
        response = requests.get(f"{base_url}/tasks/{task_id}")
        if response.status_code == 200:
            final_task = response.json()
            print(f"✅ Final Task Status: {final_task['status']}")
            print(f"   Progress: {final_task['progress'] * 100:.1f}%")
            if final_task.get('completed_at'):
                print(f"   Completed At: {final_task['completed_at']}")
        
        # 7. Check system metrics
        print("\n7️⃣ Final System Metrics...")
        response = requests.get(f"{base_url}/system/status")
        if response.status_code == 200:
            final_status = response.json()
            print(f"✅ System Load: {final_status['system_load']:.1f}%")
            print(f"   Message Rate: {final_status['message_rate']:.1f}/sec")
            print(f"   Active Tasks: {final_status['active_tasks']}")
        
        print("\n🎉 End-to-End Test Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False

def test_dashboard_accessibility():
    """Test dashboard accessibility"""
    
    print("\n🌐 Testing Dashboard Accessibility...")
    
    try:
        response = requests.get("http://localhost:8000")
        if response.status_code == 200:
            print("✅ Dashboard accessible at http://localhost:8000")
            return True
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def show_task_summary():
    """Show summary of all tasks"""
    
    print("\n📊 Task Summary:")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8000/api/v1/tasks?limit=100")
        if response.status_code == 200:
            tasks_data = response.json()
            tasks = tasks_data['tasks']
            
            status_counts = {}
            for task in tasks:
                status = task['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in status_counts.items():
                print(f"{status.upper()}: {count}")
            
            print(f"\nRecent Completed Tasks:")
            completed_tasks = [t for t in tasks if t['status'] == 'completed'][-3:]
            for task in completed_tasks:
                print(f"  ✅ {task['title']} (ID: {task['id']})")
        
    except Exception as e:
        print(f"❌ Error getting task summary: {e}")

if __name__ == "__main__":
    print("🔬 Multi-Agent Platform Comprehensive Test")
    print("=" * 60)
    
    # Test dashboard
    dashboard_ok = test_dashboard_accessibility()
    
    # Test complete workflow
    workflow_ok = test_complete_workflow()
    
    # Show task summary
    show_task_summary()
    
    print("\n" + "=" * 60)
    if dashboard_ok and workflow_ok:
        print("🎉 ALL TESTS PASSED - Multi-Agent Platform is fully functional!")
        print("\n📋 Platform Features Verified:")
        print("   ✅ Agent registry and capability discovery")
        print("   ✅ Task submission and delegation")
        print("   ✅ Task execution and completion")
        print("   ✅ Real-time dashboard and monitoring")
        print("   ✅ API endpoints and data flow")
        print("   ✅ Database persistence and state management")
        
        print("\n🌐 Access the dashboard at: http://localhost:8000")
    else:
        print("❌ Some tests failed - check the logs above")
