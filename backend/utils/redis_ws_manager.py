"""
WebSocket Manager with optional Redis-based Pub/Sub support.

This module provides a RedisWebSocketManager class that manages WebSocket connections
and supports broadcasting messages across connected clients. If Redis is available,
the manager uses Redis Pub/Sub to support distributed broadcasting across multiple
FastAPI instances. If Redis is unavailable or fails, the system gracefully falls back
to an in-memory list of WebSocket connections for local-only broadcasting.

Key Features:
- Redis-enabled broadcasting when available
- Graceful fallback to in-memory broadcasting
- Centralized WebSocket management
"""

import asyncio
import json
from fastapi import WebSocket
from typing import List
from logger import logger

# Attempt to import Redis support for asyncio.
try:
    from redis.asyncio import Redis
    redis_available = True
except ImportError:
    logger.warning("Redis not available, falling back to in-memory broadcasting.")
    redis_available = False # Fallback to in-memory broadcasting

REDIS_CHANNEL = "ws_broadcast"

class RedisWebSocketManager:
    """
    Manages WebSocket connections and broadcasts messages to connected clients.

    Features:
    - Maintains a list of active WebSocket connections.
    - Supports broadcasting messages locally to all connections.
    - If Redis is available, publishes and subscribes to a Redis channel to enable
      cross-instance WebSocket message broadcasting in distributed environments.
    - Automatically falls back to local broadcasting if Redis is unavailable or errors occur.

    Attributes:
    - active_connections (List[WebSocket]): List of currently connected WebSocket clients.
    - redis_enabled (bool): Flag indicating if Redis-based pub/sub is enabled.
    - redis (Redis | None): Redis client instance, or None if Redis is disabled.
    - pubsub_task (asyncio.Task | None): Background task listening for Redis pub/sub messages.
    """

    def __init__(self):
        # Initialize active connections list and Redis client if available
        self.active_connections: List[WebSocket] = []
        self.redis_enabled = redis_available
        self.redis = None
        self.pubsub_task = None

        if self.redis_enabled:
            try:
                self.redis = Redis() # Initialize Redis client
                # Start background async task to listen for Redis pub/sub messages
                self.pubsub_task = asyncio.create_task(self._redis_listener())
                logger.info("Redis initialized for WebSocket broadcasting.")
            except Exception as e:
                logger.warning(f"Redis initialization failed: {e}")
                self.redis_enabled = False

    async def connect(self, websocket: WebSocket):
        """
        Accept and register a new WebSocket connection.

        Parameters:
        - websocket (WebSocket): The incoming WebSocket connection to accept.

        Returns:
        - None
        """

        await websocket.accept() # Accept incoming WebSocket connection (handshake)
        self.active_connections.append(websocket) # Track active connection
        logger.info("WebSocket connected.")

    async def disconnect(self, websocket: WebSocket):
        """
        Remove and clean up a WebSocket connection.

        Parameters:
        - websocket (WebSocket): The WebSocket connection to remove.

        Returns:
        - None
        """

        if websocket in self.active_connections:
            self.active_connections.remove(websocket) # Remove from active connections
            logger.info("WebSocket disconnected.")

    async def _redis_listener(self):
        """
        Background async task that listens to Redis pub/sub channel messages.

        Behavior:
        - Subscribes to a Redis channel.
        - On receiving messages, parses JSON and broadcasts to local WebSocket clients.
        - Logs warnings and disables Redis if errors occur.

        Returns:
        - None
        """

        try:
            pubsub = self.redis.pubsub() # Create Redis pub/sub interface
            await pubsub.subscribe(REDIS_CHANNEL)  # Subscribe to broadcast channel
            logger.info("Subscribed to Redis channel for WebSocket events.")

            async for message in pubsub.listen():
                # Ignore non-message events (e.g., subscription confirmations)
                if message is None or message["type"] != "message":
                    continue # Skip non-message events
                try:
                    data = json.loads(message["data"])  # Parse JSON payload
                    await self._broadcast_local(data) # Broadcast locally 
                except Exception as e:
                    logger.warning(f"Redis listener error: {e}")
        except Exception as e:
            logger.warning(f"Redis listener stopped: {e}")
            self.redis_enabled = False # Disable Redis fallback on error

    async def _broadcast_local(self, message: dict):
        """
        Send a JSON message to all currently connected WebSocket clients locally.

        Parameters:
        - message (dict): The message payload to send.

        Returns:
        - None
        """

        # Send message to all active WebSocket clients locally
        for conn in self.active_connections:
            try:
                await conn.send_json(message) # Send JSON message to client
            except Exception as e:
                logger.warning(f"WebSocket send failed: {e}")
                await self.disconnect(conn)  # Remove faulty connection

    async def broadcast(self, message: dict):
        """
        Broadcast a message to all clients.

        If Redis is enabled, publishes the message to the Redis channel
        for cross-instance broadcasting. Otherwise, broadcasts locally.

        Parameters:
        - message (dict): The message payload to broadcast.

        Returns:
        - None
        """

        # Publish message to Redis if enabled; else broadcast locally
        if self.redis_enabled and self.redis:
            try:
                # Publish JSON stringified message to Redis channel
                await self.redis.publish(REDIS_CHANNEL, json.dumps(message))
                return
            except Exception as e:
                logger.error(f"Redis publish failed, falling back to local: {e}")
                self.redis_enabled = False  # Disable Redis fallback on failure

        # Fallback: broadcast message locally to active connections
        await self._broadcast_local(message)


# Export a single global instance to be used throughout the app
manager = RedisWebSocketManager()