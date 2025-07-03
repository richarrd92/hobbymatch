# How `main.py` Works

This is the main entry point for the HobbyMatch FastAPI backend application. It initializes the app with middleware, route registration, and lifecycle event handling.

### Key Features

- **Lifespan handler** using `asynccontextmanager` logs startup and shutdown events for monitoring.
- **CORS Middleware** configured to allow requests from local frontend origins during development.
- **Custom Middleware (`CORPMiddleware`)** sets security headers (`Cross-Origin-Opener-Policy` and `Cross-Origin-Embedder-Policy`) to enable safer cross-origin interactions.
- **Route registration** includes authentication, user, and location APIs imported from modular route files.
- **Health check endpoint (`/`)** logs and confirms the backend server status.
- Supports running with **Uvicorn** and hot-reload for local development.

### Detailed Breakdown

- **Lifespan Context Manager**: Logs informational messages on app startup and shutdown. Enables centralized lifecycle event management.

- **CORS Configuration**: Whitelists specific origins (e.g., `localhost:5173`) to enable safe cross-origin requests. Allows credentials, all methods, and headers.

- **CORP Middleware**: Injects HTTP headers to enforce cross-origin policies (`same-origin` and `require-corp`). Helps prevent security issues related to cross-origin resource sharing and embedding.

- **Route Inclusion**: Imports and attaches routers for `auth`, `users`, and `locations`. Keeps route logic modular and maintainable.

- **Health Check Endpoint**: Simple GET endpoint at root path (`/`) that returns a JSON status message. Logs each root request for observability.

- **Local Development Execution**: Runs app via Uvicorn server on `127.0.0.1:8000`. Enables hot reload with `reload=True` for immediate code updates during development.

### Summary

This setup provides a solid foundation for the backend API with essential middleware, security headers, structured routing, and lifecycle management. It facilitates easy debugging and seamless integration with the frontend.
