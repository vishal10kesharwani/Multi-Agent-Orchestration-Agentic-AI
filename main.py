"""
Multi-Agent Orchestration Platform - Main Entry Point
"""
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api.routes import router as api_router
from backend.core.orchestrator import OrchestrationEngine
from backend.core.config import settings
from backend.database import connection as db
from backend.database.seed import seed_agents


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await db.init_database()
    # Seed default agents if none exist
    try:
        async with db.async_session_maker() as session:
            created = await seed_agents(session)
            if created:
                print(f"Seeded {created} default agents")
    except Exception as e:
        print(f"Warning: seeding default agents failed: {e}")
    orchestrator = OrchestrationEngine()
    await orchestrator.initialize()
    app.state.orchestrator = orchestrator
    
    yield
    
    # Shutdown
    await orchestrator.shutdown()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Multi-Agent Orchestration Platform",
        description="A platform for orchestrating multiple AI agents to solve complex tasks",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Serve static files (frontend)
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
    
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
