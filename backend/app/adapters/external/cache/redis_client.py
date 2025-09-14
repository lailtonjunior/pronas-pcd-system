"""
Redis Client Adapter
Cliente Redis para cache e sessões
"""

import json
from typing import Any, Optional, Union
import redis.asyncio as redis
from app.core.config.settings import get_settings

settings = get_settings()

# Global Redis connection
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Obter cliente Redis (singleton)"""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
            retry_on_timeout=True,
        )
    
    return _redis_client


async def close_redis_client():
    """Fechar conexão Redis"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


class RedisCache:
    """Wrapper para operações de cache Redis"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Obter valor do cache"""
        value = await self.redis.get(key)
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """Definir valor no cache"""
        if not isinstance(value, str):
            value = json.dumps(value, default=str)
        
        if expire:
            return await self.redis.setex(key, expire, value)
        else:
            return await self.redis.set(key, value)
    
    async def delete(self, key: str) -> bool:
        """Remover chave do cache"""
        return await self.redis.delete(key) > 0
    
    async def exists(self, key: str) -> bool:
        """Verificar se chave existe"""
        return await self.redis.exists(key) > 0
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Incrementar valor numérico"""
        return await self.redis.incr(key, amount)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Definir expiração para chave"""
        return await self.redis.expire(key, seconds)
