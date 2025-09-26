#!/usr/bin/env python3
"""
Automated Test Runner
Starts the server, populates data, and runs comprehensive website tests
"""
import asyncio
import subprocess
import time
import sys
import os
import signal
from pathlib import Path

def run_populate_and_server():
    """Run the populate_and_run.py script in background"""
    print("🚀 Starting server with populated data...")

    # Change to current script directory instead of hardcoded path
    project_dir = Path(__file__).resolve().parent
    os.chdir(project_dir)

    # Start the server process
    process = subprocess.Popen(
        [sys.executable, "populate_and_run.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    return process

def wait_for_server(max_wait=30):
    """Wait for server to be ready"""
    print("⏳ Waiting for server to be ready...")

    import requests

    for i in range(max_wait):
        try:
            response = requests.get("http://localhost:8000/api/v1/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except:
            pass

        print(f"   Waiting... ({i+1}/{max_wait})")
        time.sleep(1)

    print("❌ Server failed to start within timeout")
    return False

async def run_tests():
    """Run the comprehensive test suite"""
    print("\n🧪 Running comprehensive test suite...")

    # Import and run the test suite
    from test_website_submission import WebsiteTestSuite

    async with WebsiteTestSuite() as test_suite:
        report = await test_suite.run_comprehensive_test()
        test_suite.print_test_report(report)

        # Save report
        import json
        with open('full_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        return report['summary']['success_rate'] >= 80

def main():
    """Main execution"""
    print("🎯 FULL SYSTEM TEST RUNNER")
    print("=" * 50)
    print("This will:")
    print("1. Start the server with populated data")
    print("2. Wait for server to be ready")
    print("3. Run comprehensive tests")
    print("4. Generate detailed report")
    print("=" * 50)

    server_process = None

    try:
        # Step 1: Start server
        server_process = run_populate_and_server()

        # Step 2: Wait for server
        if not wait_for_server():
            print("❌ Failed to start server")
            return False

        # Step 3: Run tests
        success = asyncio.run(run_tests())

        print(f"\n🎯 FINAL RESULT: {'SUCCESS' if success else 'FAILED'}")
        return success

    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    finally:
        # Clean up server process
        if server_process:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("✅ Server stopped")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
