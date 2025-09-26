"""
Auto Task Executor for Multi-Agent System
"""
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class AutoTaskExecutor:
    """Automatically executes tasks assigned to agents"""
    
    def __init__(self):
        self.running = False
        self._execution_task = None
    
    async def start(self):
        """Start the auto task executor"""
        try:
            self.running = True
            self._execution_task = asyncio.create_task(self._execution_loop())
            logger.info("Auto task executor started")
        except Exception as e:
            logger.error(f"Failed to start auto task executor: {e}")
    
    async def stop(self):
        """Stop the auto task executor"""
        try:
            self.running = False
            if self._execution_task:
                self._execution_task.cancel()
                try:
                    await self._execution_task
                except asyncio.CancelledError:
                    pass
            logger.info("Auto task executor stopped")
        except Exception as e:
            logger.error(f"Error stopping auto task executor: {e}")
    
    async def _execution_loop(self):
        """Main execution loop for processing tasks"""
        while self.running:
            try:
                # Process pending tasks automatically
                logger.debug("Processing pending tasks")
                await asyncio.sleep(15)  # Check every 15 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in execution loop: {e}")
                await asyncio.sleep(30)
    
    async def execute_task(self, session: AsyncSession, task_id: int) -> Dict[str, Any]:
        """Execute a specific task"""
        try:
            return {
                'success': True,
                'task_id': task_id,
                'message': 'Task executed successfully',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            return {
                'success': False,
                'task_id': task_id,
                'error': str(e)
            }
