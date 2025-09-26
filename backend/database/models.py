"""
Database models for the multi-agent orchestration platform
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from backend.database.connection import Base


class AgentStatus(PyEnum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class TaskStatus(PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageType(PyEnum):
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    NOTIFICATION = "notification"


class Agent(Base):
    """Agent model for storing agent information and capabilities"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    capabilities = Column(JSON)  # List of capabilities/skills
    status = Column(String(50), default=AgentStatus.IDLE.value)
    performance_metrics = Column(JSON)  # Performance data
    resource_requirements = Column(JSON)  # CPU, memory, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_heartbeat = Column(DateTime(timezone=True))
    
    # Relationships
    tasks = relationship("Task", back_populates="assigned_agent")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")


class Task(Base):
    """Task model for storing task information and execution details"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    requirements = Column(JSON)  # Required capabilities, resources
    priority = Column(Integer, default=1)  # 1=low, 5=high
    status = Column(String(50), default=TaskStatus.PENDING.value)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Task hierarchy
    parent_task_id = Column(Integer, ForeignKey("tasks.id"))
    parent_task = relationship("Task", remote_side=[id], back_populates="subtasks")
    subtasks = relationship("Task", back_populates="parent_task")
    
    # Agent assignment
    assigned_agent_id = Column(Integer, ForeignKey("agents.id"))
    assigned_agent = relationship("Agent", back_populates="tasks")
    
    # Execution details
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    deadline = Column(DateTime(timezone=True))
    
    # Relationships
    messages = relationship("Message", back_populates="task")


class Message(Base):
    """Message model for inter-agent communication"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    message_type = Column(String(50), nullable=False)
    content = Column(JSON)  # Message payload
    
    # Sender and receiver
    sender_id = Column(Integer, ForeignKey("agents.id"))
    sender = relationship("Agent", foreign_keys=[sender_id], back_populates="sent_messages")
    
    receiver_id = Column(Integer, ForeignKey("agents.id"))
    receiver = relationship("Agent", foreign_keys=[receiver_id], back_populates="received_messages")
    
    # Task context
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", back_populates="messages")
    
    # Message metadata
    correlation_id = Column(String(255))  # For request-response correlation
    priority = Column(Integer, default=1)
    is_read = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))


class ExecutionLog(Base):
    """Execution log for monitoring and debugging"""
    __tablename__ = "execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # DEBUG, INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    context = Column(JSON)  # Additional context data
    
    # Related entities
    agent_id = Column(Integer, ForeignKey("agents.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    
    # Add fields that the API expects
    action = Column(String(255))
    details = Column(JSON)
    status = Column(String(50))
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ResourceUsage(Base):
    """Resource usage tracking for load balancing"""
    __tablename__ = "resource_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    
    # Resource metrics
    cpu_usage = Column(Float)  # 0.0 to 1.0
    memory_usage = Column(Float)  # 0.0 to 1.0
    active_tasks = Column(Integer, default=0)
    queue_length = Column(Integer, default=0)
    
    # Performance metrics
    avg_response_time = Column(Float)  # milliseconds
    success_rate = Column(Float)  # 0.0 to 1.0
    
    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
