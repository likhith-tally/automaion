"""
FastAPI Main Application
Entry point for the OCI Business Logic Service

This file bundles all routers and services into a single FastAPI application
that can be hosted via uvicorn.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import email_suppression

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
    print("=" * 60)
    print(f"🚀 {settings.api_title} v{settings.api_version}")
    print("=" * 60)
    print(f"📍 OCI Region: {settings.oci_region}")
    print(f"📍 Tenancy: {settings.oci_tenancy_ocid[:20]}...")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"📚 Alternative Docs: http://localhost:8000/redoc")
    print("=" * 60)


# Shutdown event - runs when application stops
@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event.
    Runs once when the server stops.
    Use this to clean up resources, close connections, etc.
    """
    print("=" * 60)
    print("🛑 Application shutting down...")
    print("=" * 60)
