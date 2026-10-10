# Copyright (c) 2026 [Your Name]. All Rights Reserved.
# Unauthorized copying, modification, or distribution is strictly prohibited.

"""
Token Bucket Rate Limiter
"""

import asyncio
import time
from collections import defaultdict
from typing import Dict

class RateLimiter:
    def __init__(self, rate_per_minute: int = 60):
        self._rate = rate_per_minute
        self._tokens: Dict[str, float] = defaultdict(lambda: float(rate_per_minute))
        self._last_update: Dict[str, float] = defaultdict(time.time)
        self._lock = asyncio.Lock()

    async def acquire(self, key: str = "global") -> bool:
        async with self._lock:
            now = time.time()
            elapsed = now - self._last_update[key]
            self._tokens[key] = min(
                self._rate,
                self._tokens[key] + elapsed * (self._rate / 60.0)
            )
            self._last_update[key] = now

            if self._tokens[key] >= 1.0:
                self._tokens[key] -= 1.0
                return True
            return False

    async def wait_for_token(self, key: str = "global", timeout: float = 10.0):
        start = time.time()
        while time.time() - start < timeout:
            if await self.acquire(key):
                return True
            await asyncio.sleep(0.1)
        raise TimeoutError(f"Rate limit exceeded for {key}")

global_limiter = RateLimiter(rate_per_minute=60)
agent_limiters: Dict[str, RateLimiter] = defaultdict(lambda: RateLimiter(rate_per_minute=20))
