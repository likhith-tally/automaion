"""
FastAPI Main Application
Entry point for the OCI Business Logic Service

This file bundles all routers and services into a single FastAPI application
that can be hosted via uvicorn.
"""
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import email_suppression
from app.logging_config import setup_logging, get_logger, set_request_id, clear_request_id
import time

# Configure logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",      # Swagger UI - Interactive API documentation
    redoc_url="/redoc",    # ReDoc UI - Alternative API documentation
    openapi_url="/openapi.json"  # OpenAPI schema
)

# Add CORS middleware (allows browser-based clients to access the API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all HTTP requests with correlation IDs.
    Adds request_id to context for the duration of the request.
    """
    # Generate unique request ID
    request_id = str(uuid.uuid4())[:8]  # Short ID for readability
    set_request_id(request_id)

    # Log incoming request
    logger.info(
        "Request received",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_host": request.client.host if request.client else None
        }
    )

    # Track request duration
    start_time = time.time()

    try:
        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Log response
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms
            }
        )

        return response

    except Exception as e:
        # Log exception
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(
            f"Request failed: {str(e)}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "duration_ms": duration_ms,
                "error": str(e)
            },
            exc_info=True
        )
        raise

    finally:
        # Clean up request context
        clear_request_id()


# Register routers
app.include_router(email_suppression.router)


# Root endpoint - Basic health check
@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - Basic health check.
    Returns service status and basic information.
    """
    return {
        "status": "healthy",
        "service": settings.api_title,
        "version": settings.api_version,
        "docs": "/docs"
    }


# Detailed health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Detailed health check endpoint.
    Returns service configuration and available endpoints.
    """
    return {
        "status": "ok",
        "service": settings.api_title,
        "version": settings.api_version,
        "region": settings.oci_region,
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": "/health",
            "email_suppression": {
                "check": "GET /api/v1/email-suppression/{email}",
                "remove": "DELETE /api/v1/email-suppression/{email}"
            }
        }
    }


# Startup event - runs when application starts
@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    Runs once when the server starts.
    """
    logger.info(
        "Application starting",
        extra={
            "service": settings.api_title,
            "version": settings.api_version,
            "region": settings.oci_region,
            "log_level": settings.log_level,
            "log_format": settings.log_format
        }
    )


# Shutdown event - runs when application stops
@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event.
    Runs once when the server stops.
    Use this to clean up resources, close connections, etc.
    """
    logger.info("Application shutting down")
