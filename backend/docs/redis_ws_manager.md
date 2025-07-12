# redis_ws_manager.py

This module manages WebSocket connections and broadcasts messages across multiple FastAPI backend instances using Redis pub/sub for synchronization. It also supports fallback broadcasting locally in memory if Redis is unavailable.

### Core Class: `RedisWebSocketManager`

- Maintains a list of active WebSocket connections (`active_connections`) **in memory**.
- Handles connecting and disconnecting WebSocket clients.
- Supports two broadcast modes:
  - **Redis-based broadcasting:** Publishes messages to a Redis channel (`ws_broadcast`), enabling multiple backend instances to sync messages across servers.
  - **Local-only broadcasting:** Falls back to broadcasting messages only to WebSocket clients connected to the current instance if Redis is disabled or unreachable.

### Redis Integration

- Initializes async Redis client (`redis.asyncio.Redis`) if available.
- Subscribes to the Redis pub/sub channel and listens for messages.
- Upon receiving a message, parses it and broadcasts to all active local WebSocket clients.
- Gracefully falls back to local broadcasting if Redis initialization or publishing fails.

### Key Methods

- `connect(websocket)`: Accepts and stores a new WebSocket connection.
- `disconnect(websocket)`: Removes a WebSocket connection.
- `_redis_listener()`: Async task listening for Redis pub/sub messages to broadcast locally.
- `_broadcast_local(message)`: Sends a JSON message to all locally connected WebSocket clients.
- `broadcast(message)`: Publishes the message via Redis or falls back to local broadcast.

### Module-Level Export

- Exports a singleton instance `manager` for use throughout the application.

### Benefits

- Enables real-time, cross-instance WebSocket message broadcasting in distributed FastAPI apps.
- Provides robust fallback to local-only broadcasting.
- Simplifies WebSocket connection management.
- Minimal dependencies with graceful degradation.

*This design supports scalable, reliable WebSocket communication across multiple backend servers while maintaining functionality if Redis is unavailable.*
