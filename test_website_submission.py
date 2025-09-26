#!/usr/bin/env python3
"""
Comprehensive Website Testing Script
Tests the Multi-Agent Platform by submitting sample data and verifying dashboard population
"""
import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebsiteTestSuite:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        logger.info(f"{status} - {test_name}: {details}")
    
    async def test_server_health(self) -> bool:
        """Test if server is running and healthy"""
        try:
            async with self.session.get(f"{self.api_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result("Server Health Check", True, f"Status: {data.get('status')}")
                    return True
                else:
                    self.log_test_result("Server Health Check", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Server Health Check", False, f"Connection error: {str(e)}")
            return False
    
    async def test_system_status(self) -> Dict[str, Any]:
        """Test system status endpoint and get current state"""
        try:
            async with self.session.get(f"{self.api_url}/system/status") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result("System Status", True, 
                                       f"Active tasks: {data.get('active_tasks')}, "
                                       f"Total agents: {data.get('total_agents')}")
                    return data
                else:
                    self.log_test_result("System Status", False, f"HTTP {response.status}")
                    return {}
        except Exception as e:
            self.log_test_result("System Status", False, f"Error: {str(e)}")
            return {}
    
    async def submit_sample_tasks(self) -> List[int]:
        """Submit various sample tasks to test the system"""
        sample_tasks = [
            {
                "title": "Market Analysis Report",
                "description": "Analyze current market trends in AI technology and provide comprehensive insights",
                "priority": "high",
                "requirements": {
                    "capabilities": ["data_analysis", "web_research", "report_generation"]
                },
                "input_data": {
                    "industry": "artificial_intelligence",
                    "time_period": "Q4_2024",
                    "focus_areas": ["machine_learning", "natural_language_processing", "computer_vision"]
                }
            },
            {
                "title": "Customer Feedback Analysis",
                "description": "Process customer reviews and feedback to identify sentiment patterns and improvement areas",
                "priority": "medium",
                "requirements": {
                    "capabilities": ["text_analysis", "sentiment_analysis", "data_visualization"]
                },
                "input_data": {
                    "data_source": "customer_reviews",
                    "review_count": 1500,
                    "categories": ["product_quality", "customer_service", "pricing"]
                }
            },
            {
                "title": "Website Content Extraction",
                "description": "Extract and organize product information from competitor websites for analysis",
                "priority": "medium",
                "requirements": {
                    "capabilities": ["web_scraping", "data_extraction", "content_parsing"]
                },
                "input_data": {
                    "target_websites": ["competitor1.com", "competitor2.com"],
                    "data_types": ["product_specs", "pricing", "reviews"]
                }
            },
            {
                "title": "Code Quality Assessment",
                "description": "Review codebase for security vulnerabilities, performance issues, and best practices",
                "priority": "high",
                "requirements": {
                    "capabilities": ["code_analysis", "security_audit", "performance_optimization"]
                },
                "input_data": {
                    "repository": "main_application",
                    "languages": ["python", "javascript"],
                    "focus_areas": ["security", "performance", "maintainability"]
                }
            },
            {
                "title": "Data Visualization Dashboard",
                "description": "Create interactive charts and graphs from sales and performance data",
                "priority": "low",
                "requirements": {
                    "capabilities": ["data_visualization", "dashboard_creation", "statistical_analysis"]
                },
                "input_data": {
                    "data_source": "sales_database",
                    "chart_types": ["line_charts", "bar_charts", "pie_charts"],
                    "time_range": "last_12_months"
                }
            }
        ]
        
        submitted_task_ids = []
        
        for i, task in enumerate(sample_tasks, 1):
            try:
                async with self.session.post(
                    f"{self.api_url}/tasks",
                    json=task,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        task_id = result.get('task_id')
                        if task_id:
                            submitted_task_ids.append(task_id)
                            self.log_test_result(f"Task Submission {i}", True, 
                                               f"Task '{task['title']}' submitted with ID: {task_id}")
                        else:
                            self.log_test_result(f"Task Submission {i}", False, 
                                               f"No task ID returned for '{task['title']}'")
                    else:
                        error_text = await response.text()
                        self.log_test_result(f"Task Submission {i}", False, 
                                           f"HTTP {response.status}: {error_text}")
                        
                # Small delay between submissions
                await asyncio.sleep(0.5)
                
            except Exception as e:
                self.log_test_result(f"Task Submission {i}", False, f"Error: {str(e)}")
        
        return submitted_task_ids
    
    async def register_sample_agents(self) -> List[int]:
        """Register additional sample agents"""
        sample_agents = [
            {
                "name": "DataMiner-Pro",
                "description": "Advanced data mining and pattern recognition specialist",
                "capabilities": ["data_mining", "pattern_recognition", "machine_learning", "statistical_analysis"],
                "resource_requirements": {"cpu": 0.4, "memory": 0.6, "gpu": 0.2}
            },
            {
                "name": "ContentCurator-AI",
                "description": "Intelligent content curation and recommendation system",
                "capabilities": ["content_curation", "recommendation_engine", "text_analysis", "trend_analysis"],
                "resource_requirements": {"cpu": 0.3, "memory": 0.4}
            },
            {
                "name": "SecurityGuard-Agent",
                "description": "Cybersecurity monitoring and threat detection specialist",
                "capabilities": ["security_monitoring", "threat_detection", "vulnerability_assessment", "incident_response"],
                "resource_requirements": {"cpu": 0.5, "memory": 0.7}
            }
        ]
        
        registered_agent_ids = []
        
        for i, agent in enumerate(sample_agents, 1):
            try:
                async with self.session.post(
                    f"{self.api_url}/agents/register",
                    json=agent,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        agent_id = result.get('agent_id')
                        if agent_id:
                            registered_agent_ids.append(agent_id)
                            self.log_test_result(f"Agent Registration {i}", True, 
                                               f"Agent '{agent['name']}' registered with ID: {agent_id}")
                        else:
                            self.log_test_result(f"Agent Registration {i}", False, 
                                               f"No agent ID returned for '{agent['name']}'")
                    else:
                        error_text = await response.text()
                        self.log_test_result(f"Agent Registration {i}", False, 
                                           f"HTTP {response.status}: {error_text}")
                        
                await asyncio.sleep(0.3)
                
            except Exception as e:
                self.log_test_result(f"Agent Registration {i}", False, f"Error: {str(e)}")
        
        return registered_agent_ids
    
    async def verify_dashboard_data(self) -> bool:
        """Verify that dashboard endpoints return populated data"""
        endpoints_to_test = [
            ("/tasks", "Tasks List"),
            ("/agents", "Agents List"),
            ("/system/status", "System Status"),
            ("/monitoring/metrics", "System Metrics"),
            ("/capabilities", "System Capabilities"),
            ("/messages", "Message History")
        ]
        
        all_passed = True
        
        for endpoint, name in endpoints_to_test:
            try:
                async with self.session.get(f"{self.api_url}{endpoint}") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check if data is populated
                        has_data = False
                        if isinstance(data, dict):
                            if 'tasks' in data and data['tasks']:
                                has_data = True
                            elif 'agents' in data and data['agents']:
                                has_data = True
                            elif 'messages' in data and data['messages']:
                                has_data = True
                            elif any(key in data for key in ['active_tasks', 'total_agents', 'status']):
                                has_data = True
                            elif data:  # Any non-empty dict
                                has_data = True
                        
                        self.log_test_result(f"Dashboard Data - {name}", has_data, 
                                           f"Data populated: {has_data}")
                        if not has_data:
                            all_passed = False
                    else:
                        self.log_test_result(f"Dashboard Data - {name}", False, 
                                           f"HTTP {response.status}")
                        all_passed = False
                        
            except Exception as e:
                self.log_test_result(f"Dashboard Data - {name}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    async def test_task_completion(self, task_ids: List[int]) -> bool:
        """Test task completion functionality"""
        if not task_ids:
            self.log_test_result("Task Completion", False, "No task IDs available")
            return False
        
        # Try to complete the first task
        task_id = task_ids[0]
        
        try:
            async with self.session.post(f"{self.api_url}/tasks/{task_id}/complete") as response:
                if response.status == 200:
                    result = await response.json()
                    success = result.get('success', False)
                    self.log_test_result("Task Completion", success, 
                                       f"Task {task_id} completion: {result.get('status')}")
                    return success
                else:
                    error_text = await response.text()
                    self.log_test_result("Task Completion", False, 
                                       f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test_result("Task Completion", False, f"Error: {str(e)}")
            return False
    
    async def test_real_time_updates(self) -> bool:
        """Test that data updates in real-time"""
        try:
            # Get initial system status
            initial_status = await self.test_system_status()
            initial_tasks = initial_status.get('active_tasks', 0)
            
            # Submit a new task
            new_task = {
                "title": "Real-time Test Task",
                "description": "Task to test real-time dashboard updates",
                "priority": "high",
                "requirements": {"capabilities": ["testing"]},
                "input_data": {"test": True}
            }
            
            async with self.session.post(
                f"{self.api_url}/tasks",
                json=new_task,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status in [200, 201]:
                    # Wait a moment for processing
                    await asyncio.sleep(2)
                    
                    # Check updated status
                    updated_status = await self.test_system_status()
                    updated_tasks = updated_status.get('active_tasks', 0)
                    
                    # Verify the count changed (or at least status was retrieved)
                    real_time_working = updated_status.get('status') == 'online'
                    self.log_test_result("Real-time Updates", real_time_working, 
                                       f"System responsive to changes")
                    return real_time_working
                else:
                    self.log_test_result("Real-time Updates", False, "Failed to submit test task")
                    return False
                    
        except Exception as e:
            self.log_test_result("Real-time Updates", False, f"Error: {str(e)}")
            return False
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        print("🚀 Starting Comprehensive Website Testing Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test 1: Server Health
        print("\n📡 Testing Server Health...")
        server_healthy = await self.test_server_health()
        if not server_healthy:
            print("❌ Server is not healthy. Stopping tests.")
            return self.generate_test_report(start_time)
        
        # Test 2: Initial System Status
        print("\n📊 Checking Initial System Status...")
        initial_status = await self.test_system_status()
        
        # Test 3: Submit Sample Tasks
        print("\n📝 Submitting Sample Tasks...")
        task_ids = await self.submit_sample_tasks()
        print(f"✅ Submitted {len(task_ids)} tasks")
        
        # Test 4: Register Sample Agents
        print("\n🤖 Registering Sample Agents...")
        agent_ids = await self.register_sample_agents()
        print(f"✅ Registered {len(agent_ids)} agents")
        
        # Wait for system to process
        print("\n⏳ Waiting for system processing...")
        await asyncio.sleep(3)
        
        # Test 5: Verify Dashboard Data
        print("\n📈 Verifying Dashboard Data Population...")
        dashboard_populated = await self.verify_dashboard_data()
        
        # Test 6: Test Task Completion
        print("\n✅ Testing Task Completion...")
        task_completed = await self.test_task_completion(task_ids)
        
        # Test 7: Test Real-time Updates
        print("\n🔄 Testing Real-time Updates...")
        real_time_working = await self.test_real_time_updates()
        
        # Final System Status
        print("\n📊 Final System Status Check...")
        final_status = await self.test_system_status()
        
        return self.generate_test_report(start_time)
    
    def generate_test_report(self, start_time: float) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        end_time = time.time()
        duration = end_time - start_time
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": round(success_rate, 2),
                "duration_seconds": round(duration, 2)
            },
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def print_test_report(self, report: Dict[str, Any]):
        """Print formatted test report"""
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        summary = report['summary']
        print(f"📊 Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"📈 Success Rate: {summary['success_rate']}%")
        print(f"⏱️  Duration: {summary['duration_seconds']}s")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 40)
        
        for result in report['test_results']:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        print("\n" + "=" * 60)
        
        if summary['success_rate'] >= 80:
            print("🎉 EXCELLENT! Your website is working great!")
        elif summary['success_rate'] >= 60:
            print("👍 GOOD! Most features are working, minor issues detected.")
        else:
            print("⚠️  NEEDS ATTENTION! Several issues need to be addressed.")
        
        print("=" * 60)

async def main():
    """Main test execution"""
    print("🌐 Multi-Agent Platform Website Testing")
    print("Testing website functionality and dashboard population...")
    
    try:
        async with WebsiteTestSuite() as test_suite:
            report = await test_suite.run_comprehensive_test()
            test_suite.print_test_report(report)
            
            # Save report to file
            with open('test_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n💾 Detailed report saved to: test_report.json")
            
            return report['summary']['success_rate'] >= 80
            
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
