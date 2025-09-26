#!/usr/bin/env python3
"""
Comprehensive API Test Suite for Multi-Agent Orchestration Platform
Tests all endpoints, features, and workflows end-to-end
"""
import requests
import time
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

class APITestSuite:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.test_results = []
        self.submitted_tasks = []
        self.created_agents = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"      {details}")
        if not success and response_data:
            print(f"      Response: {response_data}")
        print()

    def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else None
            
            self.log_test(
                "Health Check",
                success,
                f"Status: {response.status_code}, Service: {data.get('service', 'Unknown') if data else 'N/A'}",
                data
            )
            return success
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False

    def test_system_status(self):
        """Test system status endpoint with all metrics"""
        try:
            response = requests.get(f"{self.api_url}/system/status", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['status', 'active_tasks', 'total_agents', 'system_load', 'message_rate']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    details = f"Status: {data['status']}, Load: {data['system_load']}%, Tasks: {data['active_tasks']}, Agents: {data['total_agents']}, Messages: {data['message_rate']}/min"
            else:
                data = None
                details = f"HTTP {response.status_code}"
            
            self.log_test("System Status", success, details, data)
            return success, data if success else None
        except Exception as e:
            self.log_test("System Status", False, f"Exception: {str(e)}")
            return False, None

    def test_agents_list(self):
        """Test agents listing endpoint"""
        try:
            response = requests.get(f"{self.api_url}/agents", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                agents_count = len(data.get('agents', []))
                total = data.get('total', 0)
                details = f"Found {agents_count} agents, Total: {total}"
                
                # Validate agent structure
                if agents_count > 0:
                    agent = data['agents'][0]
                    required_fields = ['id', 'name', 'status', 'capabilities']
                    missing_fields = [field for field in required_fields if field not in agent]
                    if missing_fields:
                        success = False
                        details += f", Missing agent fields: {missing_fields}"
            else:
                data = None
                details = f"HTTP {response.status_code}"
            
            self.log_test("Agents List", success, details, data)
            return success, data if success else None
        except Exception as e:
            self.log_test("Agents List", False, f"Exception: {str(e)}")
            return False, None

    def test_tasks_list(self):
        """Test tasks listing endpoint"""
        try:
            response = requests.get(f"{self.api_url}/tasks?limit=20", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                tasks_count = len(data.get('tasks', []))
                total = data.get('total', 0)
                details = f"Found {tasks_count} tasks, Total: {total}"
                
                # Validate task structure
                if tasks_count > 0:
                    task = data['tasks'][0]
                    required_fields = ['id', 'title', 'status', 'priority']
                    missing_fields = [field for field in required_fields if field not in task]
                    if missing_fields:
                        success = False
                        details += f", Missing task fields: {missing_fields}"
            else:
                data = None
                details = f"HTTP {response.status_code}"
            
            self.log_test("Tasks List", success, details, data)
            return success, data if success else None
        except Exception as e:
            self.log_test("Tasks List", False, f"Exception: {str(e)}")
            return False, None

    def test_task_submission(self):
        """Test task submission with various priorities and types"""
        test_tasks = [
            {
                "title": "API Test - High Priority Data Analysis",
                "description": "Test task for comprehensive API validation - analyzing system performance metrics and generating insights.",
                "priority": "high",
                "requirements": {
                    "capabilities": ["data_analysis", "report_generation"],
                    "complexity": "medium"
                }
            },
            {
                "title": "API Test - Medium Priority Text Processing",
                "description": "Test task for text analysis and sentiment processing to validate NLP capabilities.",
                "priority": "medium",
                "requirements": {
                    "capabilities": ["text_analysis", "sentiment_analysis"],
                    "complexity": "low"
                }
            },
            {
                "title": "API Test - Low Priority System Report",
                "description": "Generate comprehensive system status report with current metrics and recommendations.",
                "priority": "low",
                "requirements": {
                    "capabilities": ["report_generation", "system_monitoring"],
                    "complexity": "high"
                }
            }
        ]
        
        successful_submissions = 0
        
        for i, task_data in enumerate(test_tasks, 1):
            try:
                response = requests.post(f"{self.api_url}/tasks", json=task_data, timeout=15)
                success = response.status_code in [200, 201]
                
                if success:
                    data = response.json()
                    if data.get('success'):
                        task_id = data.get('task_id')
                        if task_id:
                            self.submitted_tasks.append(task_id)
                            successful_submissions += 1
                            
                        delegation = data.get('delegation_result', {})
                        agent_info = delegation.get('assigned_agent', {})
                        agent_name = agent_info.get('name', 'Unknown') if agent_info else 'None'
                        
                        details = f"Task {i} submitted (ID: {task_id}), Assigned to: {agent_name}"
                    else:
                        success = False
                        details = f"Task {i} submission failed: {data.get('error', 'Unknown error')}"
                else:
                    details = f"Task {i} HTTP {response.status_code}: {response.text[:100]}"
                    data = None
                
                self.log_test(f"Task Submission {i}", success, details, data if success else None)
                
            except Exception as e:
                self.log_test(f"Task Submission {i}", False, f"Exception: {str(e)}")
        
        overall_success = successful_submissions >= 2
        self.log_test(
            "Task Submission Overall",
            overall_success,
            f"Successfully submitted {successful_submissions}/{len(test_tasks)} tasks"
        )
        
        return overall_success

    def test_task_details(self):
        """Test task details endpoint for submitted tasks"""
        if not self.submitted_tasks:
            self.log_test("Task Details", False, "No submitted tasks to test")
            return False
        
        successful_details = 0
        
        for task_id in self.submitted_tasks[:3]:  # Test first 3 tasks
            try:
                response = requests.get(f"{self.api_url}/tasks/{task_id}", timeout=10)
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    required_fields = ['id', 'title', 'status', 'priority', 'progress']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        success = False
                        details = f"Task {task_id} missing fields: {missing_fields}"
                    else:
                        successful_details += 1
                        details = f"Task {task_id}: {data['status']} ({int(data.get('progress', 0) * 100)}%)"
                        if data.get('ai_response'):
                            details += f", Has AI response ({len(data['ai_response'])} chars)"
                else:
                    data = None
                    details = f"Task {task_id} HTTP {response.status_code}"
                
                self.log_test(f"Task Details {task_id}", success, details, data if success else None)
                
            except Exception as e:
                self.log_test(f"Task Details {task_id}", False, f"Exception: {str(e)}")
        
        overall_success = successful_details > 0
        self.log_test(
            "Task Details Overall",
            overall_success,
            f"Successfully retrieved {successful_details}/{len(self.submitted_tasks[:3])} task details"
        )
        
        return overall_success

    def test_task_status_monitoring(self):
        """Test task status endpoint for monitoring"""
        if not self.submitted_tasks:
            self.log_test("Task Status Monitoring", False, "No submitted tasks to monitor")
            return False
        
        successful_status = 0
        
        for task_id in self.submitted_tasks[:2]:  # Test first 2 tasks
            try:
                response = requests.get(f"{self.api_url}/tasks/{task_id}/status", timeout=10)
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    if data.get('success'):
                        successful_status += 1
                        task_info = data.get('task', {})
                        details = f"Task {task_id}: {task_info.get('status', 'unknown')} ({int(task_info.get('progress', 0) * 100)}%)"
                    else:
                        success = False
                        details = f"Task {task_id} status failed: {data.get('error', 'Unknown')}"
                else:
                    data = None
                    details = f"Task {task_id} HTTP {response.status_code}"
                
                self.log_test(f"Task Status {task_id}", success, details, data if success else None)
                
            except Exception as e:
                self.log_test(f"Task Status {task_id}", False, f"Exception: {str(e)}")
        
        overall_success = successful_status > 0
        self.log_test(
            "Task Status Monitoring Overall",
            overall_success,
            f"Successfully monitored {successful_status}/{len(self.submitted_tasks[:2])} tasks"
        )
        
        return overall_success

    def test_agent_details(self):
        """Test individual agent details endpoint"""
        try:
            # First get agents list
            agents_response = requests.get(f"{self.api_url}/agents", timeout=10)
            if agents_response.status_code != 200:
                self.log_test("Agent Details", False, "Could not get agents list")
                return False
            
            agents_data = agents_response.json()
            agents = agents_data.get('agents', [])
            
            if not agents:
                self.log_test("Agent Details", False, "No agents available to test")
                return False
            
            # Test first agent details
            agent_id = agents[0]['id']
            response = requests.get(f"{self.api_url}/agents/{agent_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['id', 'name', 'status', 'capabilities']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    success = False
                    details = f"Agent {agent_id} missing fields: {missing_fields}"
                else:
                    details = f"Agent {agent_id}: {data['name']} ({data['status']}) - {len(data.get('capabilities', []))} capabilities"
            else:
                data = None
                details = f"Agent {agent_id} HTTP {response.status_code}"
            
            self.log_test("Agent Details", success, details, data if success else None)
            return success
            
        except Exception as e:
            self.log_test("Agent Details", False, f"Exception: {str(e)}")
            return False

    def test_performance_monitoring(self):
        """Test performance monitoring by collecting metrics over time"""
        try:
            metrics_history = []
            
            print("      Collecting performance metrics for 15 seconds...")
            start_time = time.time()
            
            while time.time() - start_time < 15:
                response = requests.get(f"{self.api_url}/system/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    metrics_history.append({
                        'timestamp': time.time(),
                        'system_load': data.get('system_load', 0),
                        'active_tasks': data.get('active_tasks', 0),
                        'message_rate': data.get('message_rate', 0),
                        'total_agents': data.get('total_agents', 0)
                    })
                time.sleep(3)
            
            success = len(metrics_history) >= 3
            
            if success:
                avg_load = sum(m['system_load'] for m in metrics_history) / len(metrics_history)
                max_tasks = max(m['active_tasks'] for m in metrics_history)
                avg_message_rate = sum(m['message_rate'] for m in metrics_history) / len(metrics_history)
                
                details = f"Collected {len(metrics_history)} metrics, Avg Load: {avg_load:.1f}%, Max Tasks: {max_tasks}, Avg Messages: {avg_message_rate:.1f}/min"
            else:
                details = f"Only collected {len(metrics_history)} metrics (expected >= 3)"
            
            self.log_test("Performance Monitoring", success, details, metrics_history[-3:] if len(metrics_history) >= 3 else metrics_history)
            return success
            
        except Exception as e:
            self.log_test("Performance Monitoring", False, f"Exception: {str(e)}")
            return False

    def test_error_handling(self):
        """Test API error handling with invalid requests"""
        error_tests = [
            {
                "name": "Invalid Task ID",
                "url": f"{self.api_url}/tasks/99999",
                "expected_status": 404
            },
            {
                "name": "Invalid Agent ID",
                "url": f"{self.api_url}/agents/99999",
                "expected_status": 404
            },
            {
                "name": "Invalid Task Submission",
                "url": f"{self.api_url}/tasks",
                "method": "POST",
                "data": {"invalid": "data"},
                "expected_status": [400, 422]
            }
        ]
        
        successful_errors = 0
        
        for test in error_tests:
            try:
                if test.get("method") == "POST":
                    response = requests.post(test["url"], json=test["data"], timeout=10)
                else:
                    response = requests.get(test["url"], timeout=10)
                
                expected = test["expected_status"]
                if isinstance(expected, list):
                    success = response.status_code in expected
                else:
                    success = response.status_code == expected
                
                if success:
                    successful_errors += 1
                
                details = f"Expected {expected}, Got {response.status_code}"
                self.log_test(f"Error Handling - {test['name']}", success, details)
                
            except Exception as e:
                self.log_test(f"Error Handling - {test['name']}", False, f"Exception: {str(e)}")
        
        overall_success = successful_errors >= 2
        self.log_test(
            "Error Handling Overall",
            overall_success,
            f"Successfully handled {successful_errors}/{len(error_tests)} error cases"
        )
        
        return overall_success

    def test_data_consistency(self):
        """Test data consistency across different endpoints"""
        try:
            # Get data from multiple endpoints
            status_response = requests.get(f"{self.api_url}/system/status", timeout=10)
            tasks_response = requests.get(f"{self.api_url}/tasks?limit=100", timeout=10)
            agents_response = requests.get(f"{self.api_url}/agents", timeout=10)
            
            if not all(r.status_code == 200 for r in [status_response, tasks_response, agents_response]):
                self.log_test("Data Consistency", False, "Could not fetch all required data")
                return False
            
            status_data = status_response.json()
            tasks_data = tasks_response.json()
            agents_data = agents_response.json()
            
            # Check consistency
            api_active_tasks = status_data.get('active_tasks', 0)
            actual_active_tasks = len([t for t in tasks_data.get('tasks', []) if t.get('status') == 'in_progress'])
            
            api_total_agents = status_data.get('total_agents', 0)
            actual_total_agents = len(agents_data.get('agents', []))
            
            tasks_consistent = abs(api_active_tasks - actual_active_tasks) <= 1  # Allow small variance
            agents_consistent = api_total_agents == actual_total_agents
            
            success = tasks_consistent and agents_consistent
            
            details = f"Tasks: API={api_active_tasks}, Actual={actual_active_tasks} ({'✓' if tasks_consistent else '✗'}), "
            details += f"Agents: API={api_total_agents}, Actual={actual_total_agents} ({'✓' if agents_consistent else '✗'})"
            
            self.log_test("Data Consistency", success, details)
            return success
            
        except Exception as e:
            self.log_test("Data Consistency", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 MULTI-AGENT PLATFORM - COMPREHENSIVE API TEST SUITE")
        print("=" * 80)
        print(f"Testing API at: {self.api_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Core API Tests
        print("📡 CORE API TESTS")
        print("-" * 40)
        health_ok = self.test_health_check()
        status_ok, status_data = self.test_system_status()
        agents_ok, agents_data = self.test_agents_list()
        tasks_ok, tasks_data = self.test_tasks_list()
        
        # Functionality Tests
        print("🔧 FUNCTIONALITY TESTS")
        print("-" * 40)
        submission_ok = self.test_task_submission()
        details_ok = self.test_task_details()
        monitoring_ok = self.test_task_status_monitoring()
        agent_details_ok = self.test_agent_details()
        
        # Performance Tests
        print("📊 PERFORMANCE TESTS")
        print("-" * 40)
        performance_ok = self.test_performance_monitoring()
        
        # Reliability Tests
        print("🛡️ RELIABILITY TESTS")
        print("-" * 40)
        error_handling_ok = self.test_error_handling()
        consistency_ok = self.test_data_consistency()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Summary
        print("=" * 80)
        print("📋 TEST SUMMARY")
        print("=" * 80)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        print("📊 DETAILED RESULTS")
        print("-" * 40)
        
        categories = {
            "Core API": [health_ok, status_ok, agents_ok, tasks_ok],
            "Functionality": [submission_ok, details_ok, monitoring_ok, agent_details_ok],
            "Performance": [performance_ok],
            "Reliability": [error_handling_ok, consistency_ok]
        }
        
        for category, results in categories.items():
            category_success = sum(results)
            category_total = len(results)
            category_rate = (category_success / category_total) * 100 if category_total > 0 else 0
            status = "✅" if category_rate >= 75 else "⚠️" if category_rate >= 50 else "❌"
            print(f"{status} {category}: {category_success}/{category_total} ({category_rate:.0f}%)")
        
        print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🏆 EXCELLENT - API is fully functional and ready for production!")
            print("✅ All core functionality working perfectly")
            print("✅ Task submission and processing operational")
            print("✅ Real-time monitoring and metrics available")
            print("✅ Error handling and data consistency verified")
        elif success_rate >= 75:
            print("👍 GOOD - API is mostly functional with minor issues")
            print("✅ Core functionality working well")
            print("⚠️ Some advanced features may need attention")
        elif success_rate >= 50:
            print("⚠️ FAIR - API has significant issues that need addressing")
            print("⚠️ Basic functionality working but unreliable")
            print("❌ Several critical features failing")
        else:
            print("❌ POOR - API has major issues and is not ready for use")
            print("❌ Critical functionality failing")
            print("❌ Requires immediate attention")
        
        print()
        print(f"🌐 Dashboard URL: {self.base_url}")
        print(f"📊 API Documentation: {self.base_url}/docs")
        print(f"📝 Submitted {len(self.submitted_tasks)} test tasks for processing")
        
        return success_rate >= 75

def main():
    """Main test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive API Test Suite')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL for API testing')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Run tests
    test_suite = APITestSuite(args.url)
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
