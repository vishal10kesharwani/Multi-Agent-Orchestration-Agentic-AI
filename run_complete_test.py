#!/usr/bin/env python3
"""
Execute comprehensive application test
"""
import sys
import os

# Change to project directory
project_dir = "/home/labuser/Desktop/Project/ai-openhack-2025/2792672_AIProject"
os.chdir(project_dir)
sys.path.insert(0, project_dir)

from test_application import ApplicationTester

def main():
    """Run complete application test"""
    tester = ApplicationTester()
    success = tester.run_complete_test()
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
