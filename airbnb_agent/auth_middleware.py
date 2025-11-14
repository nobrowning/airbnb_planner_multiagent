# pylint: disable=logging-fstring-interpolation
"""Authentication middleware for Airbnb Agent API."""

import logging
import os

from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


logger = logging.getLogger(__name__)


class BearerTokenAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to authenticate requests using Bearer token."""

    def __init__(self, app, api_key: str | None = None):
        """Initialize the authentication middleware.
        
        Args:
            app: The ASGI application.
            api_key: The API key to validate against. If None, auth is disabled.
        """
        super().__init__(app)
        self.api_key = api_key
        self.auth_enabled = api_key is not None and len(api_key) > 0
        
        if self.auth_enabled:
            logger.info("Bearer token authentication is ENABLED")
        else:
            logger.warning("Bearer token authentication is DISABLED - all requests will be allowed")

    async def dispatch(
        self, request: Request, call_next: Callable
    ):
        """Process the request and validate authentication.
        
        Args:
            request: The incoming request.
            call_next: The next middleware or route handler.
            
        Returns:
            The response from the next handler or an error response.
        """
        # Skip authentication if disabled
        if not self.auth_enabled:
            return await call_next(request)
        
        # Allow health check endpoints without authentication
        if request.url.path in ["/health",]:
            return await call_next(request)
        
        # Extract Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            logger.warning(f"Unauthorized request to {request.url.path}: No Authorization header")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Missing Authorization header"
                }
            )
        
        # Validate Bearer token format
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning(f"Unauthorized request to {request.url.path}: Invalid Authorization format")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Invalid Authorization header format. Expected: Bearer <token>"
                }
            )
        
        token = parts[1]
        
        # Validate token
        if token != self.api_key:
            logger.warning(f"Unauthorized request to {request.url.path}: Invalid token")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Invalid API key"
                }
            )
        
        # Token is valid, proceed with request
        logger.debug(f"Authenticated request to {request.url.path}")
        return await call_next(request)
