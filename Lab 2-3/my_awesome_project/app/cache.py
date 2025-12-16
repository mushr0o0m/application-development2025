"""Async Redis cache helpers.

Provides a small wrapper around `redis.asyncio.Redis` to set/get/delete
JSON-serialised values. The Redis connection is created lazily and
reused for the process lifetime.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Optional
import logging

# `redis.asyncio` may be unavailable in some environments (ModuleNotFoundError).
# Import lazily and provide a clear runtime error if it's missing so callers
# know how to fix their environment (install `redis>=4.6.0`).
try:
    import redis.asyncio as aioredis  # type: ignore
except Exception:  # pragma: no cover - runtime environment may not have redis
    aioredis = None  # type: ignore

_redis: Optional["aioredis.Redis"] = None
_lock = asyncio.Lock()
_log = logging.getLogger(__name__)


async def get_redis() -> "aioredis.Redis":
    global _redis
    if aioredis is None:
        # Fail fast with an actionable message when `redis` package is missing.
        raise RuntimeError(
            "Missing dependency: package 'redis' is not installed.\n"
            "Install it with: pip install 'redis>=4.6.0' or rebuild your Docker image."
        )

    if _redis is None:
        async with _lock:
            if _redis is None:
                host = os.getenv("REDIS_HOST", "localhost")
                port = int(os.getenv("REDIS_PORT", "6379"))
                url = os.getenv("REDIS_URL")
                if url:
                    _redis = aioredis.from_url(url)
                else:
                    _redis = aioredis.Redis(host=host, port=port, decode_responses=True)
    return _redis


async def get_cached(key: str) -> Optional[Any]:
    r = await get_redis()
    raw = await r.get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return raw


async def set_cached(key: str, value: Any, ex: Optional[int] = None) -> None:
    r = await get_redis()
    # always JSON-serialise complex objects
    if isinstance(value, (str, bytes)):
        to_store = value
    else:
        to_store = json.dumps(value, default=str)
    await r.set(key, to_store, ex=ex)


async def delete_cached(key: str) -> None:
    r = await get_redis()
    await r.delete(key)
