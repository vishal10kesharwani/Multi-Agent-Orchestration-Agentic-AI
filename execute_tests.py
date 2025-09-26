#!/usr/bin/env python3
"""
Execute API tests and show results
"""
import sys
import os
sys.path.append('/home/labuser/Desktop/Project/ai-openhack-2025/2792672_AIProject')

from test_complete_api import APITestSuite

def main():
    """Execute the API test suite"""
    print("🚀 MULTI-AGENT PLATFORM - API TESTING")
    print("=" * 60)
    
    # Initialize test suite
    test_suite = APITestSuite("http://localhost:8000")
    
    # Run all tests
    success = test_suite.run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ API TEST SUITE COMPLETED SUCCESSFULLY!")
    else:
        print("❌ API TEST SUITE FAILED - CHECK RESULTS ABOVE")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        sys.exit(1)
