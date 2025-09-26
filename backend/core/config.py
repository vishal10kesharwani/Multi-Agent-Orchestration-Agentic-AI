"""
Configuration management for the multi-agent orchestration platform
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./multiagent.db",
        env="DATABASE_URL"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    
    # LLM Configuration
    OPENAI_API_BASE: str = Field(
        default="https://genailab.tcs.in",
        env="OPENAI_API_BASE"
    )
    OPENAI_API_KEY: str = Field(
        default="sk-_LvO2D4G66_3VX2yCgot2Q",
        env="OPENAI_API_KEY"
    )
    LLM_MODEL: str = Field(
        default="azure_ai/genailab-maas-DeepSeek-V3-0324",
        env="LLM_MODEL"
    )
    
    # Agent Configuration
    MAX_CONCURRENT_AGENTS: int = Field(default=10, env="MAX_CONCURRENT_AGENTS")
    AGENT_TIMEOUT: int = Field(default=300, env="AGENT_TIMEOUT")
    TASK_RETRY_LIMIT: int = Field(default=3, env="TASK_RETRY_LIMIT")
    
    # Monitoring Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
