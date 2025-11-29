#!/usr/bin/env python3
import asyncio
import websockets
import websockets.exceptions
from websockets.protocol import State
import ssl
import time
from typing import Optional, Dict, Any, List, AsyncGenerator, Union, cast
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class WSMessage:
    content: Union[bytes, str]
    message_type: str
    size: int
    timestamp: float

@dataclass
class WSConnectionConfig:
    url: str
    headers: Dict[str, str]
    subprotocols: Optional[List[str]]
    max_size: int = 20 * 1024 * 1024
    timeout: int = 30
    ssl_context: Optional[ssl.SSLContext] = None

class HashdiveWSClient:

    def __init__(self, config: WSConnectionConfig):
        self.config = config
        self._connection = None
        
    async def connect(self, max_retries: int = 3, retry_delay: float = 2.0) -> bool:
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt + 1}/{max_retries} connecting to {self.config.url}")
                    await asyncio.sleep(retry_delay * attempt)
                else:
                    logger.info(f"Connecting to {self.config.url}")
                
                logger.debug(f"Subprotocols: {self.config.subprotocols}")
                
                self._connection = await asyncio.wait_for(
                    websockets.connect(
                        self.config.url,
                        ssl=self.config.ssl_context,
                        additional_headers=self.config.headers,
                        subprotocols=cast(Any, self.config.subprotocols),
                        max_size=self.config.max_size,
                        ping_timeout=self.config.timeout,
                        open_timeout=30
                    ),
                    timeout=45
                )
                
                logger.info("WebSocket connection established")
                return True
                
            except asyncio.TimeoutError:
                logger.warning(f"Connection attempt {attempt + 1} timed out")
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} connection attempts failed due to timeout")
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} connection attempts failed")
        
        return False
    
    async def disconnect(self):
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("WebSocket connection closed")
    
    async def send_binary(self, data: bytes) -> bool:
        if not self._connection:
            logger.error("No active connection")
            return False
            
        try:
            await self._connection.send(data)
            logger.debug(f"Sent binary data ({len(data)} bytes)")
            return True
        except Exception as e:
            logger.error(f"Failed to send binary data: {e}")
            return False
    
    async def send_text(self, text: str) -> bool:
        if not self._connection:
            logger.error("No active connection")
            return False
            
        try:
            await self._connection.send(text)
            logger.debug(f"Sent text data ({len(text)} chars)")
            return True
        except Exception as e:
            logger.error(f"Failed to send text data: {e}")
            return False
    
    async def receive_message(self, timeout: Optional[float] = None) -> Optional[WSMessage]:
        if not self._connection:
            logger.error("No active connection")
            return None
            
        try:
            if timeout is None:
                msg = await self._connection.recv()
            else:
                msg = await asyncio.wait_for(
                    self._connection.recv(), 
                    timeout=timeout
                )
            
            timestamp = time.time()
            
            if isinstance(msg, bytes):
                return WSMessage(
                    content=msg,
                    message_type='binary',
                    size=len(msg),
                    timestamp=timestamp
                )
            else:
                return WSMessage(
                    content=msg,
                    message_type='text',
                    size=len(msg),
                    timestamp=timestamp
                )
                
        except asyncio.TimeoutError:
            logger.debug("Receive timeout")
            return None
        except websockets.exceptions.ConnectionClosed as e:
            logger.debug(f"WebSocket connection closed: {e.code} - {e.reason}")
            return None
        except Exception as e:
            if "close frame" in str(e).lower() or "connection" in str(e).lower():
                logger.debug(f"Connection ended: {e}")
            else:
                logger.error(f"Failed to receive message: {e}")
            return None
    
    async def receive_messages(
        self, 
        max_messages: Optional[int] = None,
        timeout_per_message: Optional[float] = None,
        total_timeout: Optional[float] = None
    ) -> AsyncGenerator[WSMessage, None]:
        if not self._connection:
            logger.error("No active connection")
            return
            
        message_count = 0
        start_time = asyncio.get_event_loop().time()
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        while True:
            if max_messages and message_count >= max_messages:
                logger.debug(f"Reached max messages limit: {max_messages}")
                break
                
            if total_timeout:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= total_timeout:
                    logger.debug(f"Reached total timeout: {total_timeout}s")
                    break
            
            if not self.is_connected:
                logger.info("WebSocket connection is closed, stopping message reception")
                break
            
            try:
                message = await self.receive_message(timeout_per_message)
                if message is None:
                    consecutive_failures += 1
                    if consecutive_failures >= max_consecutive_failures:
                        logger.info(f"No messages received after {max_consecutive_failures} attempts, stopping")
                        break
                    
                    if self.is_connected:
                        ping_success = await self.ping()
                        if not ping_success:
                            logger.info("Ping failed, connection likely closed")
                            break
                    continue
                
                consecutive_failures = 0
                message_count += 1
                logger.debug(f"Received message #{message_count} ({message.message_type}, {message.size} bytes)")
                yield message
                
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                break
    
    async def ping(self) -> bool:
        if not self._connection:
            logger.debug("No active connection for ping")
            return False
        
        if not self.is_connected:
            logger.debug("Connection already closed, skipping ping")
            return False
            
        try:
            await self._connection.ping()
            logger.debug("Ping sent successfully")
            return True
        except websockets.exceptions.ConnectionClosed:
            logger.debug("Cannot ping - connection is closed")
            return False
        except Exception as e:
            if "close frame" in str(e).lower() or "connection" in str(e).lower():
                logger.debug(f"Ping failed - connection closed: {e}")
            else:
                logger.warning(f"Ping failed: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        try:
            if self._connection is None:
                return False
            return self._connection.state == State.OPEN
        except Exception:
            return False
    
    async def __aenter__(self):
        if not await self.connect():
            raise ConnectionError("Failed to establish WebSocket connection after retries")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

def create_hashdive_config(
    cookies: Dict[str, str],
    user_agent: Optional[str] = None
) -> WSConnectionConfig:
    if user_agent is None:
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    
    cookie_header = "; ".join(f"{k}={v}" for k, v in cookies.items())
    xsrf_token = cookies.get("_streamlit_xsrf")
    
    headers = {
        "User-Agent": user_agent,
        "Origin": "https://hashdive.com",
        "Cookie": cookie_header,
    }
    
    subprotocols = ["streamlit"]
    if xsrf_token:
        subprotocols.append(xsrf_token)
    
    ssl_context = ssl.create_default_context()
    
    return WSConnectionConfig(
        url="wss://hashdive.com/_stcore/stream",
        headers=headers,
        subprotocols=subprotocols,
        ssl_context=ssl_context
    )
