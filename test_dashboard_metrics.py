#!/usr/bin/env python3
"""
Test Dashboard Metrics Display
"""
import requests
import json
import time

def test_dashboard_metrics():
    """Test all dashboard metrics endpoints and data"""
    
    print("🔍 Testing Dashboard Metrics")
    print("=" * 40)
    
    base_url = "http://localhost:8000/api/v1"
    
    try:
        # Test 1: System Status
        print("\n📊 Test 1: System Status Metrics")
        response = requests.get(f"{base_url}/system/status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            load_balancing = data.get('load_balancing', {})
            agent_capabilities = data.get('agent_capabilities', {})
            
            print(f"✅ Total Agents: {load_balancing.get('total_agents', 0)}")
            print(f"✅ Idle Agents: {load_balancing.get('idle_agents', 0)}")
            print(f"✅ Busy Agents: {load_balancing.get('busy_agents', 0)}")
            print(f"✅ Queue Length: {load_balancing.get('queue_length', 0)}")
            print(f"✅ Average Load: {load_balancing.get('average_load', 0):.2f}")
            print(f"✅ Unique Capabilities: {agent_capabilities.get('unique_capabilities', 0)}")
            print(f"✅ Orchestrator Status: {data.get('orchestrator_status', 'Unknown')}")
        else:
            print(f"❌ System status failed: {response.status_code}")
            return False
        
        # Test 2: Active Tasks Count
        print("\n📋 Test 2: Active Tasks Metrics")
        response = requests.get(f"{base_url}/tasks?status=in_progress&limit=100", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            active_tasks = data.get('total', 0)
            tasks = data.get('tasks', [])
            
            print(f"✅ Active Tasks Count: {active_tasks}")
            
            if tasks:
                print("📝 Active Tasks Details:")
                for task in tasks[:3]:  # Show first 3
                    print(f"   - ID {task['id']}: {task['title']} (Agent: {task.get('assigned_agent_id', 'None')})")
        else:
            print(f"❌ Active tasks failed: {response.status_code}")
            return False
        
        # Test 3: All Tasks Overview
        print("\n📊 Test 3: All Tasks Overview")
        response = requests.get(f"{base_url}/tasks?limit=20", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            all_tasks = data.get('tasks', [])
            
            # Count by status
            status_counts = {}
            for task in all_tasks:
                status = task.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"✅ Total Tasks: {len(all_tasks)}")
            for status, count in status_counts.items():
                print(f"   - {status.title()}: {count}")
        else:
            print(f"❌ All tasks failed: {response.status_code}")
            return False
        
        # Test 4: Agents List
        print("\n🤖 Test 4: Agents Metrics")
        response = requests.get(f"{base_url}/agents", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', [])
            
            print(f"✅ Total Agents: {len(agents)}")
            
            status_counts = {}
            for agent in agents:
                status = agent.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in status_counts.items():
                print(f"   - {status.title()}: {count}")
                
            # Show agent capabilities
            all_capabilities = set()
            for agent in agents:
                capabilities = agent.get('capabilities', [])
                all_capabilities.update(capabilities)
            
            print(f"✅ Unique Capabilities: {len(all_capabilities)}")
            print(f"   Capabilities: {', '.join(sorted(all_capabilities))}")
        else:
            print(f"❌ Agents failed: {response.status_code}")
            return False
        
        # Test 5: Calculate System Load
        print("\n⚡ Test 5: System Load Calculation")
        
        # Get current metrics
        status_response = requests.get(f"{base_url}/system/status", timeout=5)
        tasks_response = requests.get(f"{base_url}/tasks?status=in_progress&limit=100", timeout=5)
        
        if status_response.status_code == 200 and tasks_response.status_code == 200:
            status_data = status_response.json()
            tasks_data = tasks_response.json()
            
            load_balancing = status_data.get('load_balancing', {})
            busy_agents = load_balancing.get('busy_agents', 0)
            total_agents = load_balancing.get('total_agents', 1)
            queue_length = load_balancing.get('queue_length', 0)
            active_tasks = tasks_data.get('total', 0)
            
            # Calculate system load percentage
            system_load_percent = min(((busy_agents + (queue_length * 0.1)) / total_agents) * 100, 100)
            
            print(f"✅ Busy Agents: {busy_agents}")
            print(f"✅ Total Agents: {total_agents}")
            print(f"✅ Queue Length: {queue_length}")
            print(f"✅ Active Tasks: {active_tasks}")
            print(f"✅ Calculated System Load: {system_load_percent:.1f}%")
            
            # Message rate (using queue length as proxy)
            message_rate = queue_length
            print(f"✅ Message Rate (Queue): {message_rate}")
        else:
            print("❌ System load calculation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_dashboard_frontend():
    """Test if dashboard frontend can access the data"""
    
    print("\n🌐 Testing Dashboard Frontend Access")
    print("=" * 40)
    
    try:
        # Test main dashboard page
        response = requests.get("http://localhost:8000/", timeout=5)
        
        if response.status_code == 200:
            print("✅ Dashboard page accessible")
            
            # Check if it contains expected elements
            content = response.text
            if 'totalAgents' in content and 'activeTasks' in content:
                print("✅ Dashboard contains metric elements")
                return True
            else:
                print("⚠️  Dashboard missing some metric elements")
                return False
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Dashboard Metrics Test Suite")
    print("=" * 50)
    
    # Test API metrics
    api_ok = test_dashboard_metrics()
    
    # Test frontend access
    frontend_ok = test_dashboard_frontend()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 DASHBOARD METRICS TEST SUMMARY")
    print("=" * 50)
    print(f"API Metrics: {'✅ WORKING' if api_ok else '❌ FAILED'}")
    print(f"Frontend Access: {'✅ WORKING' if frontend_ok else '❌ FAILED'}")
    
    if api_ok and frontend_ok:
        print("\n🎉 Dashboard Metrics are WORKING!")
        print("✅ Active Tasks display should work")
        print("✅ System Load calculation should work") 
        print("✅ Message Rate (Queue) should work")
        print("\n🌐 Check your dashboard at: http://localhost:8000")
    else:
        print("\n❌ Dashboard Metrics have issues")
    
    exit(0 if (api_ok and frontend_ok) else 1)
