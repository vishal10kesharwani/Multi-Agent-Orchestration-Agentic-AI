#!/usr/bin/env python3
"""
Utility script to reset all agents to IDLE and clear in-progress tasks.
"""
import asyncio
from datetime import datetime

from backend.database import connection as db
from backend.database.models import Agent, Task, AgentStatus, TaskStatus
from sqlalchemy import update, select


async def main():
    await db.init_database()
    async with db.async_session_maker() as session:
        # Set all agents to IDLE and update heartbeat
        await session.execute(
            update(Agent)
            .values(status=AgentStatus.IDLE.value, last_heartbeat=datetime.utcnow())
        )
        # Move any stuck in-progress tasks back to pending
        await session.execute(
            update(Task)
            .where(Task.status == TaskStatus.IN_PROGRESS.value)
            .values(status=TaskStatus.PENDING.value, progress=0.0, assigned_agent_id=None)
        )
        await session.commit()
        # Return counts for confirmation
        agents = (await session.execute(select(Agent))).scalars().all()
        tasks = (await session.execute(select(Task))).scalars().all()
        idle = sum(1 for a in agents if a.status == AgentStatus.IDLE.value)
        print(f"Reset complete: {idle}/{len(agents)} agents set to IDLE. {len(tasks)} total tasks present.")


if __name__ == "__main__":
    asyncio.run(main())
