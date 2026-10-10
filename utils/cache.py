# Copyright (c) 2026 [Your Name]. All Rights Reserved.
# Unauthorized copying, modification, or distribution is strictly prohibited.

"""
High-performance in-memory cache with TTL
"""

from typing import Any, Optional
import hashlib
import json
import asyncio
import time

class AgentCache:
    def __init__(self, maxsize: int = 500, ttl: int = 300):
        self._store = {}
        self._maxsize = maxsize
        self._ttl = ttl
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0

    def _make_key(self, agent: str, task: str, context: dict = None) -> str:
        payload = {"agent": agent, "task": task, "context": context or {}}
        raw = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    def _cleanup(self):
        now = time.time()
        expired = [k for k, (_, exp) in self._store.items() if exp < now]
        for k in expired:
            del self._store[k]
        if len(self._store) > self._maxsize:
            sorted_keys = sorted(self._store.keys(), key=lambda k: self._store[k][1])
            for k in sorted_keys[:len(self._store) - self._maxsize]:
                del self._store[k]

    async def get(self, agent: str, task: str, context: dict = None) -> Optional[Any]:
        key = self._make_key(agent, task, context)
        async with self._lock:
            self._cleanup()
            if key in self._store:
                value, exp = self._store[key]
                if exp >= time.time():
                    self._hits += 1
                    return value
                else:
                    del self._store[key]
            self._misses += 1
            return None

    async def set(self, agent: str, task: str, value: Any, context: dict = None):
        key = self._make_key(agent, task, context)
        async with self._lock:
            self._cleanup()
            self._store[key] = (value, time.time() + self._ttl)

    def stats(self) -> dict:
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "size": len(self._store)
        }

cache = AgentCache(ttl=300)
