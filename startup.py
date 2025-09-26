#!/usr/bin/env python3
"""
Startup script for Multi-Agent Platform
Ensures proper initialization and server startup
"""
import asyncio
import uvicorn
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def initialize_system():
    """Initialize the system components"""
    try:
        print(" Initializing database...")
        from backend.database.connection import init_database
        await init_database()
        print("Database initialized")
        
        print(" Setting up orchestration engine...")
        from backend.core.orchestrator import OrchestrationEngine
        orchestrator = OrchestrationEngine()
        await orchestrator.initialize()
        print("Orchestration engine ready")
        
        return True
    except Exception as e:
        print(f"Initialization failed: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("Starting Multi-Agent Platform Server...")
    print("=" * 50)
    
    # Initialize system first
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    init_success = loop.run_until_complete(initialize_system())
    if not init_success:
        print("Failed to initialize system")
        sys.exit(1)
    
    print("Starting web server on http://localhost:8000")
    print("Dashboard available at http://localhost:8000")
    print("API docs at http://localhost:8000/docs")
    print("=" * 50)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to prevent issues
        log_level="info"
    )

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)
