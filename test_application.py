#!/usr/bin/env python3
"""
Comprehensive Application Tester
Starts server, runs all tests, and provides complete assessment
"""
import subprocess
import time
import sys
import os
import requests
import signal
from datetime import datetime
from test_complete_api import APITestSuite

class ApplicationTester:
    def __init__(self):
        self.server_process = None
        self.base_url = "http://localhost:8000"
        self.api_url = f"{self.base_url}/api/v1"
        
    def start_server(self):
        """Start the FastAPI server"""
        print("🚀 Starting Multi-Agent Platform Server...")
        print("-" * 50)
        
        try:
            # Start server in background
            self.server_process = subprocess.Popen([
                sys.executable, "main.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait for server to start
            print("⏳ Waiting for server to initialize...")
            max_attempts = 30
            for attempt in range(max_attempts):
                try:
                    response = requests.get(f"{self.api_url}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Server started successfully on {self.base_url}")
                        return True
                except:
                    pass
                time.sleep(2)
                print(f"   Attempt {attempt + 1}/{max_attempts}...")
            
            print("❌ Server failed to start within timeout")
            return False
            
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def stop_server(self):
        """Stop the server"""
        if self.server_process:
            print("\n🛑 Stopping server...")
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.server_process.wait()
            print("✅ Server stopped")
    
    def test_basic_connectivity(self):
        """Test basic server connectivity"""
        print("\n🔍 BASIC CONNECTIVITY TEST")
        print("-" * 40)
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health Check: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Health Check Failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connectivity Test Failed: {e}")
            return False
    
    def test_frontend_dashboard(self):
        """Test frontend dashboard"""
        print("\n🌐 FRONTEND DASHBOARD TEST")
        print("-" * 40)
        
        try:
            # Test main page
            response = requests.get(self.base_url, timeout=5)
            if response.status_code == 200:
                print("✅ Dashboard HTML loads successfully")
                
                # Test dashboard.js
                js_response = requests.get(f"{self.base_url}/dashboard.js", timeout=5)
                if js_response.status_code == 200:
                    print("✅ Dashboard JavaScript loads successfully")
                    return True
                else:
                    print(f"❌ Dashboard JS failed: HTTP {js_response.status_code}")
                    return False
            else:
                print(f"❌ Dashboard failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Frontend test failed: {e}")
            return False
    
    def run_api_tests(self):
        """Run comprehensive API tests"""
        print("\n📡 COMPREHENSIVE API TESTS")
        print("=" * 60)
        
        test_suite = APITestSuite(self.base_url)
        return test_suite.run_all_tests()
    
    def test_database_functionality(self):
        """Test database operations"""
        print("\n💾 DATABASE FUNCTIONALITY TEST")
        print("-" * 40)
        
        try:
            # Test system status (requires database)
            response = requests.get(f"{self.api_url}/system/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Database connectivity: {data.get('status', 'unknown')}")
                print(f"   Active tasks: {data.get('active_tasks', 0)}")
                print(f"   Total agents: {data.get('total_agents', 0)}")
                return True
            else:
                print(f"❌ Database test failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Database test failed: {e}")
            return False
    
    def run_complete_test(self):
        """Run complete application test"""
        print("🧪 COMPLETE APPLICATION TEST SUITE")
        print("=" * 70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        results = {
            'server_start': False,
            'connectivity': False,
            'frontend': False,
            'database': False,
            'api_tests': False
        }
        
        try:
            # 1. Start server
            results['server_start'] = self.start_server()
            if not results['server_start']:
                print("\n❌ CRITICAL: Server failed to start. Cannot proceed with tests.")
                return False
            
            # 2. Test basic connectivity
            results['connectivity'] = self.test_basic_connectivity()
            
            # 3. Test frontend
            results['frontend'] = self.test_frontend_dashboard()
            
            # 4. Test database
            results['database'] = self.test_database_functionality()
            
            # 5. Run comprehensive API tests
            results['api_tests'] = self.run_api_tests()
            
            # Calculate overall success
            total_tests = len(results)
            passed_tests = sum(results.values())
            success_rate = (passed_tests / total_tests) * 100
            
            # Final assessment
            print("\n" + "=" * 70)
            print("📊 FINAL APPLICATION ASSESSMENT")
            print("=" * 70)
            
            print(f"Server Startup: {'✅ PASS' if results['server_start'] else '❌ FAIL'}")
            print(f"Basic Connectivity: {'✅ PASS' if results['connectivity'] else '❌ FAIL'}")
            print(f"Frontend Dashboard: {'✅ PASS' if results['frontend'] else '❌ FAIL'}")
            print(f"Database Operations: {'✅ PASS' if results['database'] else '❌ FAIL'}")
            print(f"API Test Suite: {'✅ PASS' if results['api_tests'] else '❌ FAIL'}")
            
            print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
            
            if success_rate >= 90:
                print("\n🏆 EXCELLENT - Application is fully functional!")
                print("✅ All core systems operational")
                print("✅ Ready for production use")
            elif success_rate >= 70:
                print("\n👍 GOOD - Application is mostly functional")
                print("⚠️ Some minor issues detected")
            elif success_rate >= 50:
                print("\n⚠️ FAIR - Application has significant issues")
                print("❌ Several critical components failing")
            else:
                print("\n❌ POOR - Application has major problems")
                print("❌ Requires immediate attention")
            
            print(f"\n🌐 Application URL: {self.base_url}")
            print(f"📊 API Documentation: {self.base_url}/docs")
            
            return success_rate >= 70
            
        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error during testing: {e}")
            return False
        finally:
            self.stop_server()

def main():
    """Main test execution"""
    tester = ApplicationTester()
    
    try:
        success = tester.run_complete_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted")
        tester.stop_server()
        sys.exit(1)

if __name__ == "__main__":
    main()
