# Copyright (c) 2026 [Your Name]. All Rights Reserved.
# Unauthorized copying, modification, or distribution is strictly prohibited.

"""
Base Agent class - All specialized agents inherit from this
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import uuid

@dataclass
class AgentResult:
    agent_name: str
    success: bool
    content: Any
    confidence: float = 0.0
    execution_time_ms: float = 0.0
    metadata: Dict = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            "agent": self.agent_name,
            "success": self.success,
            "content": self.content,
            "confidence": self.confidence,
            "execution_time_ms": round(self.execution_time_ms, 2),
            "metadata": self.metadata,
            "error": self.error,
            "timestamp": self.timestamp
        }


class BaseAgent(ABC):
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.id = str(uuid.uuid4())[:8]
        self.active_tasks = 0

    @abstractmethod
    async def execute(self, task: str, context: Dict = None) -> AgentResult:
        pass

    async def run(self, task: str, context: Dict = None) -> AgentResult:
        _start = asyncio.get_event_loop().time()
        self.active_tasks += 1
        try:
            result = await self.execute(task, context or {})
            result.execution_time_ms = (asyncio.get_event_loop().time() - _start) * 1000
            return result
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                success=False,
                content=None,
                error=str(e),
                execution_time_ms=(asyncio.get_event_loop().time() - _start) * 1000
            )
        finally:
            self.active_tasks -= 1
