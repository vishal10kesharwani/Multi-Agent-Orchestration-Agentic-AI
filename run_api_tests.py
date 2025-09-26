#!/usr/bin/env python3
"""
Simple script to run API tests and show results
"""
import subprocess
import sys
import os

def run_api_tests():
    """Run the comprehensive API test suite"""
    try:
        # Change to the project directory
        project_dir = "/home/labuser/Desktop/Project/ai-openhack-2025/2792672_AIProject"
        os.chdir(project_dir)
        
        # Run the test suite
        print("🚀 Starting API Test Suite...")
        print("=" * 60)
        
        result = subprocess.run([
            sys.executable, "test_complete_api.py", "--url", "http://localhost:8000"
        ], capture_output=True, text=True, timeout=120)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        print("=" * 60)
        print(f"Test suite completed with exit code: {result.returncode}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Test suite timed out after 2 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_api_tests()
    sys.exit(0 if success else 1)
