import asyncio
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from .hashdiveWS import HashdiveWSClient, WSConnectionConfig
from .hashdiveCookies import get_cookies_from_chrome

logger = logging.getLogger(__name__)

@dataclass
class PooledConnection:
    client: HashdiveWSClient
    in_use: bool = False
    created_at: float = 0.0
    last_used: float = 0.0

class HashdiveConnectionPool:
    def __init__(self, max_connections: int = 10, connection_timeout: int = 300):
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.connections: List[PooledConnection] = []
        self.config: Optional[WSConnectionConfig] = None
        self._lock = asyncio.Lock()
        
    async def initialize(self) -> bool:
        try:
            cookies = get_cookies_from_chrome(
                domain="hashdive.com", 
                names=["ajs_anonymous_id", "_streamlit_user", "_streamlit_xsrf"],
                show_debug=False
            )
            
            if not cookies:
                logger.error("No cookies found for hashdive.com")
                return False
            
            from .hashdiveWS import create_hashdive_config
            self.config = create_hashdive_config(cookies)
            logger.info(f"Connection pool initialized with max {self.max_connections} connections")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            return False
    
    async def get_connection(self) -> Optional[HashdiveWSClient]:
        async with self._lock:
            current_time = asyncio.get_event_loop().time()
            
            for conn in self.connections:
                if not conn.in_use and conn.client.is_connected:
                    if current_time - conn.last_used < self.connection_timeout:
                        conn.in_use = True
                        conn.last_used = current_time
                        logger.debug("Reusing existing connection")
                        return conn.client
                    else:
                        await self._cleanup_connection(conn)
            
            if len(self.connections) < self.max_connections:
                new_conn = await self._create_connection()
                if new_conn:
                    logger.debug(f"Created new connection ({len(self.connections)}/{self.max_connections})")
                    return new_conn.client
            
            logger.warning("No available connections in pool")
            return None
    
    async def release_connection(self, client: HashdiveWSClient):
        async with self._lock:
            for conn in self.connections:
                if conn.client == client:
                    conn.in_use = False
                    conn.last_used = asyncio.get_event_loop().time()
                    logger.debug("Released connection back to pool")
                    return
            
            logger.warning("Attempted to release unknown connection")
    
    async def _create_connection(self) -> Optional[PooledConnection]:
        if not self.config:
            logger.error("Connection pool not initialized")
            return None
        
        try:
            client = HashdiveWSClient(self.config)
            if await client.connect():
                current_time = asyncio.get_event_loop().time()
                pooled_conn = PooledConnection(
                    client=client,
                    in_use=True,
                    created_at=current_time,
                    last_used=current_time
                )
                self.connections.append(pooled_conn)
                return pooled_conn
            else:
                logger.error("Failed to establish websocket connection")
                return None
                
        except Exception as e:
            logger.error(f"Error creating connection: {e}")
            return None
    
    async def _cleanup_connection(self, conn: PooledConnection):
        try:
            await conn.client.disconnect()
            self.connections.remove(conn)
            logger.debug("Cleaned up expired connection")
        except Exception as e:
            logger.error(f"Error cleaning up connection: {e}")
    
    async def cleanup_expired_connections(self):
        async with self._lock:
            current_time = asyncio.get_event_loop().time()
            expired_connections = []
            
            for conn in self.connections:
                if not conn.in_use and (current_time - conn.last_used > self.connection_timeout):
                    expired_connections.append(conn)
            
            for conn in expired_connections:
                await self._cleanup_connection(conn)
            
            if expired_connections:
                logger.info(f"Cleaned up {len(expired_connections)} expired connections")
    
    async def close_all(self):
        async with self._lock:
            for conn in self.connections:
                try:
                    await conn.client.disconnect()
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
            
            self.connections.clear()
            logger.info("All connections closed")

_global_pool: Optional[HashdiveConnectionPool] = None

async def get_connection_pool(max_connections: int = 10) -> HashdiveConnectionPool:
    global _global_pool
    if _global_pool is None:
        _global_pool = HashdiveConnectionPool(max_connections=max_connections)
        if not await _global_pool.initialize():
            raise RuntimeError("Failed to initialize connection pool")
    return _global_pool
