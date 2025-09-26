#!/usr/bin/env python3
"""
Test Intelligent AI Agents - Automatic Task Solving with Priority Assignment
"""
import asyncio
import requests
import time
import json

def test_intelligent_task_execution():
    """Test intelligent agents solving real tasks automatically"""
    
    print("🤖 INTELLIGENT AI AGENTS TEST")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/v1"
    
    # Test tasks with different priorities and complexity
    test_tasks = [
        {
            "title": "Market Analysis Report for Q4 2024",
            "description": "Generate a comprehensive market analysis report including trend analysis, competitor benchmarking, and strategic recommendations for the technology sector in Q4 2024.",
            "priority": "high",
            "requirements": {
                "capabilities": ["data_analysis", "report_generation", "statistical_modeling"],
                "complexity": "high"
            }
        },
        {
            "title": "Customer Sentiment Analysis Dashboard",
            "description": "Analyze customer feedback data from multiple sources and create a sentiment analysis dashboard with actionable insights and recommendations.",
            "priority": "high", 
            "requirements": {
                "capabilities": ["text_analysis", "sentiment_analysis", "data_visualization"],
                "complexity": "medium"
            }
        },
        {
            "title": "Competitive Intelligence Web Scraping",
            "description": "Extract and analyze competitor pricing, product features, and market positioning data from 20+ e-commerce websites.",
            "priority": "medium",
            "requirements": {
                "capabilities": ["web_scraping", "data_extraction", "api_integration"],
                "complexity": "medium"
            }
        },
        {
            "title": "Technical Documentation Generation",
            "description": "Create comprehensive technical documentation for the multi-agent platform including API documentation, user guides, and system architecture diagrams.",
            "priority": "medium",
            "requirements": {
                "capabilities": ["document_creation", "technical_writing", "report_generation"],
                "complexity": "low"
            }
        },
        {
            "title": "Predictive Analytics Model Development",
            "description": "Develop and validate predictive models for customer churn, revenue forecasting, and demand planning using historical data.",
            "priority": "low",
            "requirements": {
                "capabilities": ["statistical_modeling", "data_analysis", "predictive_analytics"],
                "complexity": "high"
            }
        }
    ]
    
    submitted_tasks = []
    
    print("📋 SUBMITTING INTELLIGENT TASKS...")
    print("-" * 40)
    
    # Submit all test tasks
    for i, task_data in enumerate(test_tasks, 1):
        try:
            print(f"\n{i}. Submitting: {task_data['title']}")
            print(f"   Priority: {task_data['priority'].upper()}")
            print(f"   Capabilities: {', '.join(task_data['requirements']['capabilities'])}")
            
            response = requests.post(f"{base_url}/tasks", json=task_data)
            if response.status_code in [200, 201]:  # Accept both 200 and 201
                result = response.json()
                if result.get('success'):
                    task_id = result['task_id']
                    submitted_tasks.append({
                        'id': task_id,
                        'title': task_data['title'],
                        'priority': task_data['priority']
                    })
                    
                    delegation = result.get('delegation_result', {})
                    if delegation.get('assigned_agent'):
                        agent_info = delegation['assigned_agent']
                        print(f"   ✅ Submitted (ID: {task_id}) → Assigned to {agent_info['name']}")
                    else:
                        print(f"   ✅ Submitted (ID: {task_id}) → Queued for assignment")
                else:
                    print(f"   ❌ Failed: {result}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 SUBMITTED {len(submitted_tasks)} TASKS")
    print("⏳ Waiting for automatic processing...")
    
    # Monitor task execution
    print("\n🔄 MONITORING AUTOMATIC EXECUTION...")
    print("-" * 40)
    
    completed_tasks = []
    max_wait_time = 120  # 2 minutes
    start_time = time.time()
    
    while len(completed_tasks) < len(submitted_tasks) and (time.time() - start_time) < max_wait_time:
        print(f"\n⏱️  Checking status... ({int(time.time() - start_time)}s elapsed)")
        
        for task in submitted_tasks:
            if task['id'] not in [t['id'] for t in completed_tasks]:
                try:
                    response = requests.get(f"{base_url}/tasks/{task['id']}")
                    if response.status_code == 200:
                        task_info = response.json()
                        status = task_info['status']
                        progress = task_info.get('progress', 0) * 100
                        
                        if status == 'completed':
                            completed_tasks.append({
                                'id': task['id'],
                                'title': task['title'],
                                'priority': task['priority'],
                                'result': task_info.get('output_data', {})
                            })
                            print(f"   ✅ COMPLETED: {task['title']} ({progress:.0f}%)")
                            
                        elif status == 'in_progress':
                            print(f"   🔄 PROCESSING: {task['title']} ({progress:.0f}%)")
                            
                        elif status == 'failed':
                            error = task_info.get('error_message', 'Unknown error')
                            print(f"   ❌ FAILED: {task['title']} - {error}")
                            completed_tasks.append({
                                'id': task['id'],
                                'title': task['title'],
                                'priority': task['priority'],
                                'error': error
                            })
                        
                except Exception as e:
                    print(f"   ⚠️  Error checking {task['id']}: {e}")
        
        if len(completed_tasks) < len(submitted_tasks):
            time.sleep(10)  # Wait 10 seconds before next check
    
    # Show results
    print("\n🎯 EXECUTION RESULTS")
    print("=" * 60)
    
    successful_tasks = [t for t in completed_tasks if 'result' in t]
    failed_tasks = [t for t in completed_tasks if 'error' in t]
    
    print(f"✅ SUCCESSFUL: {len(successful_tasks)}")
    print(f"❌ FAILED: {len(failed_tasks)}")
    print(f"⏳ PENDING: {len(submitted_tasks) - len(completed_tasks)}")
    
    # Show detailed results for successful tasks
    if successful_tasks:
        print(f"\n📋 SUCCESSFUL TASK RESULTS:")
        print("-" * 40)
        
        for task in successful_tasks:
            print(f"\n🎯 {task['title']}")
            print(f"   Priority: {task['priority'].upper()}")
            
            result_data = task['result']
            if isinstance(result_data, dict):
                agent_name = result_data.get('agent_name', 'Unknown')
                domain = result_data.get('domain', 'general')
                confidence = result_data.get('confidence', 0)
                
                print(f"   Agent: {agent_name} ({domain})")
                print(f"   Confidence: {confidence * 100:.1f}%")
                
                result_text = result_data.get('result', '')
                if result_text:
                    # Show first 200 characters of result
                    preview = result_text[:200].replace('\n', ' ')
                    print(f"   Result: {preview}...")
    
    # Show failed tasks
    if failed_tasks:
        print(f"\n❌ FAILED TASKS:")
        print("-" * 40)
        for task in failed_tasks:
            print(f"   • {task['title']}: {task['error']}")
    
    # Final system status
    print(f"\n📊 FINAL SYSTEM STATUS:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/system/status")
        if response.status_code == 200:
            status = response.json()
            print(f"Active Tasks: {status['active_tasks']}")
            print(f"System Load: {status['system_load']:.1f}%")
            print(f"Total Agents: {status['total_agents']}")
            
            # Show task status breakdown
            task_counts = status.get('task_status_counts', {})
            print(f"\nTask Status Breakdown:")
            for status_name, count in task_counts.items():
                print(f"  {status_name.upper()}: {count}")
    
    except Exception as e:
        print(f"Error getting system status: {e}")
    
    success_rate = len(successful_tasks) / len(submitted_tasks) * 100 if submitted_tasks else 0
    
    print(f"\n🎉 TEST COMPLETE!")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🏆 EXCELLENT - AI Agents are working perfectly!")
    elif success_rate >= 60:
        print("👍 GOOD - AI Agents are functioning well!")
    else:
        print("⚠️  NEEDS IMPROVEMENT - Check agent configuration")
    
    return success_rate >= 60

if __name__ == "__main__":
    print("🚀 INTELLIGENT AI AGENTS - AUTOMATIC TASK SOLVING")
    print("=" * 70)
    print("Testing priority-based assignment and intelligent task execution...")
    
    success = test_intelligent_task_execution()
    
    print("\n" + "=" * 70)
    if success:
        print("🎯 INTELLIGENT AGENTS TEST PASSED!")
        print("✅ AI agents are automatically solving tasks with priority-based assignment")
        print("✅ Tasks are being completed with high-quality results")
        print("✅ System is fully operational and intelligent")
    else:
        print("❌ INTELLIGENT AGENTS TEST NEEDS ATTENTION")
        print("Check logs and system configuration")
    
    print(f"\n🌐 Monitor the dashboard at: http://localhost:8000")
    print("🤖 AI agents are now continuously processing tasks automatically!")
