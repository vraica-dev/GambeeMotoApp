"""Tiny in-memory login throttler (no extra dependency).

Blocks a key (client IP) after ``max_attempts`` failures inside ``window``
seconds. Process-local: sufficient for this single-process app; use
Flask-Limiter with shared storage if ever scaled horizontally.
"""

import time
from collections import defaultdict
from typing import Dict, List


class LoginRateLimiter:
    def __init__(self, max_attempts: int = 5, window: int = 300) -> None:
        self.max_attempts = max_attempts
        self.window = window
        self._fails: Dict[str, List[float]] = defaultdict(list)

    def _prune(self, key: str) -> None:
        now = time.time()
        self._fails[key] = [t for t in self._fails[key] if now - t < self.window]

    def blocked(self, key: str) -> bool:
        self._prune(key)
        return len(self._fails[key]) >= self.max_attempts

    def record(self, key: str) -> None:
        self._fails[key].append(time.time())

    def reset(self, key: str) -> None:
        self._fails.pop(key, None)


login_limiter = LoginRateLimiter()
