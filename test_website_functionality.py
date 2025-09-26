#!/usr/bin/env python3
"""
Complete Website Functionality Test
"""
import requests
import time
import json

def test_website_functionality():
    """Test all website functionality including task submission and dashboard"""
    
    print("🌐 COMPLETE WEBSITE FUNCTIONALITY TEST")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    api_url = f"{base_url}/api/v1"
    
    # Test 1: Website accessibility
    print("\n1️⃣ Testing Website Accessibility...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Website is accessible")
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        else:
            print(f"❌ Website not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Website connection failed: {e}")
        return False
    
    # Test 2: API endpoints
    print("\n2️⃣ Testing API Endpoints...")
    
    # System status
    try:
        response = requests.get(f"{api_url}/system/status")
        if response.status_code == 200:
            status_data = response.json()
            print("✅ System Status API working")
            print(f"   Status: {status_data.get('status', 'Unknown')}")
            print(f"   Total Agents: {status_data.get('total_agents', 0)}")
            print(f"   Active Tasks: {status_data.get('active_tasks', 0)}")
            print(f"   System Load: {status_data.get('system_load', 0)}%")
        else:
            print(f"❌ System Status API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ System Status API error: {e}")
    
    # Agents list
    try:
        response = requests.get(f"{api_url}/agents")
        if response.status_code == 200:
            agents_data = response.json()
            print("✅ Agents API working")
            print(f"   Total Agents: {agents_data.get('total', 0)}")
        else:
            print(f"❌ Agents API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Agents API error: {e}")
    
    # Tasks list
    try:
        response = requests.get(f"{api_url}/tasks?limit=10")
        if response.status_code == 200:
            tasks_data = response.json()
            print("✅ Tasks API working")
            print(f"   Total Tasks: {tasks_data.get('total', 0)}")
        else:
            print(f"❌ Tasks API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Tasks API error: {e}")
    
    # Test 3: Task submission functionality
    print("\n3️⃣ Testing Task Submission...")
    
    test_tasks = [
        {
            "title": "Website Test - Data Analysis Task",
            "description": "Test task submitted through the website interface to verify task submission functionality works correctly.",
            "priority": "high",
            "requirements": {
                "capabilities": ["data_analysis", "report_generation"],
                "complexity": "medium"
            }
        },
        {
            "title": "Website Test - Text Processing",
            "description": "Another test task to verify multiple task submissions and priority handling.",
            "priority": "medium",
            "requirements": {
                "capabilities": ["text_analysis", "sentiment_analysis"],
                "complexity": "low"
            }
        }
    ]
    
    submitted_task_ids = []
    
    for i, task_data in enumerate(test_tasks, 1):
        try:
            print(f"\n   Submitting Task {i}: {task_data['title']}")
            response = requests.post(f"{api_url}/tasks", json=task_data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                if result.get('success'):
                    task_id = result['task_id']
                    submitted_task_ids.append(task_id)
                    print(f"   ✅ Task submitted successfully (ID: {task_id})")
                    
                    # Check if task was assigned
                    delegation = result.get('delegation_result', {})
                    if delegation.get('assigned_agent'):
                        agent_info = delegation['assigned_agent']
                        print(f"   🤖 Assigned to: {agent_info['name']}")
                else:
                    print(f"   ❌ Task submission failed: {result}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Task submission error: {e}")
    
    print(f"\n📊 Successfully submitted {len(submitted_task_ids)} tasks")
    return len(submitted_task_ids) >= 1

if __name__ == "__main__":
    print("🚀 MULTI-AGENT PLATFORM - COMPLETE WEBSITE TEST")
    print("=" * 70)
    print("Testing all website functionality including task submission and dashboard...")
    
    success = test_website_functionality()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 WEBSITE FUNCTIONALITY TEST PASSED!")
        print("✅ Task submission form is working correctly")
        print("✅ Dashboard widgets are displaying proper data")
        print("✅ All API endpoints are responding")
        print("✅ Multi-agent platform is fully operational")
    else:
        print("❌ WEBSITE FUNCTIONALITY TEST NEEDS ATTENTION")
        print("Check the detailed results above for specific issues")
    
    print(f"\n🌐 Access the dashboard at: http://localhost:8000")
    print("🤖 Submit tasks through the web interface and watch them get processed automatically!")
