#!/usr/bin/env python3
import asyncio
import base64
import json
import urllib.parse
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from .hashdiveWS import HashdiveWSClient, WSConnectionConfig, create_hashdive_config, WSMessage
from .hashdiveCookies import get_cookies_from_chrome
from .hashdiveConnectionPool import get_connection_pool
from ..parser.hashdive_decoder import decode_frame
from ..parser.hashdive_encoder import encode_frame
import logging

logger = logging.getLogger(__name__)

@dataclass
class HashdiveRequest:
    market_question: str
    page_name: str = "Analyze_Market"
    timezone: str = "Europe/Istanbul"
    timezone_offset: int = -180
    locale: str = "en-US"
    color_scheme: str = "light"
    polymarket_id: Optional[str] = None

@dataclass
class HashdiveResponse:
    success: bool
    messages: List[Dict[str, Any]]
    error: Optional[str] = None

class HashdiveService:
    
    def __init__(self):
        self._pool = None
    
    async def _get_pool(self):
        if self._pool is None:
            self._pool = await get_connection_pool(max_connections=10)
        return self._pool
    
    def create_init_payload(self, request: HashdiveRequest) -> Optional[bytes]:
        try:
            encoded_market = urllib.parse.quote_plus(request.market_question)
            
            payload = {
                "rerunScript": {
                    "queryString": f"market={encoded_market}",
                    "widgetStates": {},
                    "pageScriptHash": "",
                    "pageName": request.page_name,
                    "contextInfo": {
                        "timezone": request.timezone,
                        "timezoneOffset": request.timezone_offset,
                        "locale": request.locale,
                        "url": f"https://hashdive.com/{request.page_name}",
                        "isEmbedded": False,
                        "colorScheme": request.color_scheme
                    }
                }
            }
            
            logger.debug(f"Creating payload for market: {request.market_question}")
            encoded_data = encode_frame(payload_json=payload, schema="BackMsg")
            
            if encoded_data:
                logger.info(f"Payload encoded successfully ({len(encoded_data)} bytes)")
                return encoded_data
            else:
                logger.error("Failed to encode payload")
                return None
                
        except Exception as e:
            logger.error(f"Error creating payload: {e}")
            return None
    
    def decode_message(self, message: WSMessage) -> Optional[Dict[str, Any]]:
        try:
            if message.message_type == 'binary':
                content_bytes = message.content if isinstance(message.content, bytes) else message.content.encode()
                b64_str = base64.b64encode(content_bytes).decode()
                decoded = decode_frame(data=b64_str)
                if decoded:
                    logger.debug(f"Decoded binary message ({message.size} bytes)")
                    return decoded
                else:
                    logger.debug(f"Failed to decode binary message ({message.size} bytes) - continuing...")
                    return None
            else:
                try:
                    decoded = json.loads(message.content)
                    logger.debug("Parsed text message as JSON")
                    return decoded
                except json.JSONDecodeError:
                    logger.debug(f"Text message (not JSON): {message.content}")
                    return {"text": message.content}
        except Exception as e:
            logger.debug(f"Error decoding message: {e} - continuing...")
            return None
    
    
    def get_authentication_config(self) -> Optional[WSConnectionConfig]:
        try:
            cookies = get_cookies_from_chrome(
                domain="hashdive.com", 
                names=["ajs_anonymous_id", "_streamlit_user", "_streamlit_xsrf"],
                show_debug=False
            )
            
            if not cookies:
                logger.error("No cookies found for hashdive.com")
                return None
            
            logger.info(f"Retrieved cookies: {list(cookies.keys())}")
            return create_hashdive_config(cookies)
            
        except Exception as e:
            logger.error(f"Failed to get authentication config: {e}")
            return None

    async def analyze_market(
        self, 
        request: HashdiveRequest,
        max_messages: int = 300,
        timeout_seconds: int = 60,
        message_callback: Optional[Callable] = None,
        use_pool: bool = True
    ) -> HashdiveResponse:
        logger.info(f"Starting market analysis: {request.market_question}")
        
        init_payload = self.create_init_payload(request)
        if not init_payload:
            return HashdiveResponse(
                success=False,
                messages=[],
                error="Failed to create initialization payload"
            )
        
        if not use_pool:
            return await self._analyze_market_direct(request, init_payload, max_messages, timeout_seconds, message_callback)
        
        try:
            pool = await self._get_pool()
            ws_client = await pool.get_connection()
            
            if not ws_client:
                logger.warning("No available connections in pool, falling back to direct connection")
                return await self._analyze_market_direct(request, init_payload, max_messages, timeout_seconds, message_callback)
            
            try:
                if not await ws_client.send_binary(init_payload):
                    return HashdiveResponse(
                        success=False,
                        messages=[],
                        error="Failed to send initialization payload"
                    )
                
                await asyncio.sleep(1)
                
                logger.debug("Waiting for messages...")
                
                messages = []
                message_count = 0
                
                async for ws_message in ws_client.receive_messages(
                    max_messages=max_messages,
                    timeout_per_message=None,
                    total_timeout=timeout_seconds
                ):
                    message_count += 1
                    decoded = self.decode_message(ws_message)
                    if decoded:
                        messages.append(decoded)

                        if message_callback:
                            await message_callback(decoded, message_count)
                        if decoded.get("scriptFinished") == "FINISHED_SUCCESSFULLY":
                            logger.debug(f"Script finished successfully after {message_count} messages")
                            break
                
                return HashdiveResponse(
                    success=True,
                    messages=messages
                )
            
            finally:
                await pool.release_connection(ws_client)
                
        except Exception as e:
            logger.error(f"Error during market analysis: {e}")
            return HashdiveResponse(
                success=False,
                messages=[],
                error=str(e)
            )

    async def _analyze_market_direct(
        self,
        request: HashdiveRequest,
        init_payload: bytes,
        max_messages: int,
        timeout_seconds: int,
        message_callback: Optional[Callable] = None
    ) -> HashdiveResponse:
        config = self.get_authentication_config()
        if not config:
            return HashdiveResponse(
                success=False,
                messages=[],
                error="Failed to get authentication configuration"
            )
        
        try:
            async with HashdiveWSClient(config) as ws_client:
                if not await ws_client.send_binary(init_payload):
                    return HashdiveResponse(
                        success=False,
                        messages=[],
                        error="Failed to send initialization payload"
                    )
                
                await asyncio.sleep(1)
                
                logger.info("Waiting for messages...")
                
                messages = []
                message_count = 0
                
                async for ws_message in ws_client.receive_messages(
                    max_messages=max_messages,
                    timeout_per_message=None,
                    total_timeout=timeout_seconds
                ):
                    message_count += 1
                    decoded = self.decode_message(ws_message)
                    if decoded:
                        messages.append(decoded)

                        if message_callback:
                            await message_callback(decoded, message_count)
                        if decoded.get("scriptFinished") == "FINISHED_SUCCESSFULLY":
                            logger.info(f"Script finished successfully after {message_count} messages")
                            break
                
                return HashdiveResponse(
                    success=True,
                    messages=messages
                )
                
        except Exception as e:
            logger.error(f"Error during market analysis: {e}")
            return HashdiveResponse(
                success=False,
                messages=[],
                error=str(e)
            )
    
    async def analyze_markets_parallel(
        self,
        requests: List[HashdiveRequest],
        max_concurrent: int = 10,
        max_messages: int = 300,
        timeout_seconds: int = 60,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[HashdiveResponse]:
        logger.info(f"Starting parallel analysis of {len(requests)} markets")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        completed_count = 0
        
        async def analyze_with_semaphore(request: HashdiveRequest) -> HashdiveResponse:
            nonlocal completed_count
            async with semaphore:
                result = await self.analyze_market(
                    request=request,
                    max_messages=max_messages,
                    timeout_seconds=timeout_seconds
                )
                completed_count += 1
                if progress_callback:
                    progress_callback(completed_count, len(requests))
                return result
        
        tasks = [analyze_with_semaphore(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Market {i} failed with exception: {result}")
                processed_results.append(HashdiveResponse(
                    success=False,
                    messages=[],
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        logger.info(f"Parallel analysis completed: {sum(1 for r in processed_results if r.success)}/{len(requests)} successful")
        return processed_results
