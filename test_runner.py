"""
Test Runner for Multi-Agent Orchestration Platform
"""
import asyncio
import sys
import logging
from datetime import datetime

from startup import startup_sequence
from backend.database.connection import async_session_maker
from backend.sample_data.test_scenarios import TestScenarios

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_comprehensive_tests():
    """Run comprehensive test suite"""
    
    print("=" * 60)
    print("Multi-Agent Orchestration Platform - Test Suite")
    print("=" * 60)
    
    try:
        # Initialize platform
        print("\n1. Initializing platform...")
        orchestrator = await startup_sequence()
        
        # Run comprehensive tests
        print("\n2. Running comprehensive test suite...")
        async with async_session_maker() as session:
            test_results = await TestScenarios.run_comprehensive_test_suite(
                orchestrator, session
            )
        
        # Display results
        print("\n" + "=" * 60)
        print("TEST RESULTS")
        print("=" * 60)
        
        print(f"Test Suite: {test_results['test_suite']}")
        print(f"Start Time: {test_results['start_time']}")
        print(f"End Time: {test_results['summary']['end_time']}")
        
        print(f"\nOverall Results:")
        print(f"  Total Tests: {test_results['summary']['total_tests']}")
        print(f"  Successful: {test_results['summary']['successful_tests']}")
        print(f"  Success Rate: {test_results['summary']['success_rate']:.1%}")
        
        print(f"\nDetailed Results:")
        for test_name, result in test_results['tests'].items():
            status = "✅ PASS" if result.get('success') else "❌ FAIL"
            print(f"  {test_name}: {status}")
            if not result.get('success') and result.get('error'):
                print(f"    Error: {result['error']}")
        
        # Shutdown
        await orchestrator.shutdown()
        
        # Exit with appropriate code
        if test_results['summary']['success_rate'] == 1.0:
            print(f"\n🎉 All tests passed!")
            return 0
        else:
            print(f"\n⚠️  Some tests failed!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        logger.exception("Test suite error")
        return 1


async def run_demo_scenario():
    """Run a demonstration scenario"""
    
    print("=" * 60)
    print("Multi-Agent Orchestration Platform - Demo")
    print("=" * 60)
    
    try:
        # Initialize platform
        print("\n1. Initializing platform...")
        orchestrator = await startup_sequence()
        
        print("\n2. Running demonstration scenario...")
        
        # Submit a complex multi-agent task
        demo_task = {
            "title": "Complete Market Analysis Demo",
            "description": "Demonstrate multi-agent coordination for market research",
            "requirements": {
                "capabilities": ["web_scraping", "data_analysis", "report_generation"],
                "priority": 4,
                "multi_agent": True
            },
            "input_data": {
                "market_segment": "AI Tools",
                "analysis_depth": "comprehensive",
                "demo_mode": True
            }
        }
        
        async with async_session_maker() as session:
            # Submit task
            print("\n3. Submitting complex task...")
            result = await orchestrator.submit_task(session, demo_task)
            
            if result.get('success'):
                task_id = result['task_id']
                print(f"   Task submitted successfully! ID: {task_id}")
                
                # Monitor progress
                print("\n4. Monitoring task progress...")
                for i in range(5):
                    await asyncio.sleep(2)
                    status = await orchestrator.get_task_status(session, task_id)
                    print(f"   Progress check {i+1}: {status.get('progress', {}).get('status', 'unknown')}")
                
                # Get system status
                print("\n5. System status:")
                system_status = await orchestrator.get_system_status(session)
                health = system_status.get('system_health', {}).get('current_health', {})
                
                print(f"   Total Agents: {health.get('total_agents', 0)}")
                print(f"   Active Agents: {health.get('active_agents', 0)}")
                print(f"   System Load: {health.get('system_load', 0):.1%}")
                print(f"   Completed Tasks: {health.get('completed_tasks', 0)}")
                
            else:
                print(f"   Task submission failed: {result.get('error')}")
        
        # Shutdown
        await orchestrator.shutdown()
        print(f"\n✅ Demo completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logger.exception("Demo error")
        return 1


def main():
    """Main entry point"""
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = "demo"
    
    if mode == "test":
        exit_code = asyncio.run(run_comprehensive_tests())
    elif mode == "demo":
        exit_code = asyncio.run(run_demo_scenario())
    else:
        print("Usage: python test_runner.py [test|demo]")
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
