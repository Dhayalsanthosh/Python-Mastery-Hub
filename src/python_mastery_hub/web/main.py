# Location: src/python_mastery_hub/web/main.py

"""
Main FastAPI Application

Entry point for the Python Mastery Hub web application.
Configures FastAPI app, middleware, routes, and startup/shutdown events.
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import uvicorn

# Import routers
from python_mastery_hub.web.api.auth import router as auth_router
from python_mastery_hub.web.api.modules import router as modules_router  
from python_mastery_hub.web.api.progress import router as progress_router
from python_mastery_hub.web.api.exercises import router as exercises_router
from python_mastery_hub.web.api.admin import router as admin_router

# Import middleware and config
from python_mastery_hub.web.middleware.cors import setup_all_middleware
from python_mastery_hub.web.middleware.rate_limiting import rate_limit_middleware
from python_mastery_hub.web.middleware.error_handling import setup_error_handlers
from python_mastery_hub.web.config.database import get_database
from python_mastery_hub.web.config.cache import get_cache_manager
from python_mastery_hub.web.config.security import get_security_config

# Import utilities
from python_mastery_hub.utils.logging_config import get_logger
from python_mastery_hub.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    logger.info("Starting Python Mastery Hub application...")
    
    try:
        # Initialize database
        db = await get_database()
        logger.info("Database initialized")
        
        # Run migrations
        migration_success = await db.run_migrations()
        if migration_success:
            logger.info("Database migrations completed")
        else:
            logger.warning("Database migrations failed or skipped")
        
        # Initialize cache
        cache = await get_cache_manager()
        logger.info("Cache manager initialized")
        
        # Initialize security config
        security_config = get_security_config()
        validation = security_config.validate_configuration()
        if not validation['valid']:
            logger.warning(f"Security configuration issues: {validation['issues']}")
        else:
            logger.info("Security configuration validated")
        
        # Store instances in app state
        app.state.database = db
        app.state.cache = cache
        app.state.security = security_config
        
        logger.info("Application startup completed successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise
    
    finally:
        # Cleanup on shutdown
        logger.info("Shutting down Python Mastery Hub application...")
        
        try:
            if hasattr(app.state, 'cache'):
                await app.state.cache.close()
                logger.info("Cache connections closed")
            
            if hasattr(app.state, 'database'):
                await app.state.database.close()
                logger.info("Database connections closed")
                
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        
        logger.info("Application shutdown completed")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Create FastAPI app with metadata
    app = FastAPI(
        title="Python Mastery Hub API",
        description="Interactive Python learning platform with exercises, progress tracking, and community features",
        version="1.0.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
        openapi_url="/openapi.json" if settings.environment != "production" else None,
        lifespan=lifespan
    )
    
    # Setup middleware (order matters - added in reverse execution order)
    setup_all_middleware(app)
    
    # Add rate limiting middleware
    app.middleware("http")(rate_limit_middleware)
    
    # Setup error handlers
    setup_error_handlers(app)
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="src/python_mastery_hub/web/static"), name="static")
    
    # Setup templates
    templates = Jinja2Templates(directory="src/python_mastery_hub/web/templates")
    app.state.templates = templates
    
    # Include API routers
    app.include_router(
        auth_router,
        prefix="/api/auth",
        tags=["Authentication"]
    )
    
    app.include_router(
        modules_router,
        prefix="/api/modules", 
        tags=["Learning Modules"]
    )
    
    app.include_router(
        progress_router,
        prefix="/api/progress",
        tags=["Progress Tracking"]
    )
    
    app.include_router(
        exercises_router,
        prefix="/api/exercises",
        tags=["Code Exercises"]
    )
    
    app.include_router(
        admin_router,
        prefix="/api/admin",
        tags=["Administration"]
    )
    
    # Add health check endpoints
    setup_health_endpoints(app)
    
    # Add frontend routes (for SPA)
    setup_frontend_routes(app)
    
    return app


def setup_health_endpoints(app: FastAPI):
    """Setup health check and monitoring endpoints."""
    
    @app.get("/health")
    async def health_check():
        """Basic health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0.0",
            "environment": settings.environment
        }
    
    @app.get("/health/detailed")
    async def detailed_health_check(request: Request):
        """Detailed health check with component status."""
        health_status = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0.0",
            "environment": settings.environment,
            "components": {}
        }
        
        try:
            # Check database health
            if hasattr(request.app.state, 'database'):
                db_health = await request.app.state.database.health_check()
                health_status["components"]["database"] = db_health
                
                if db_health["status"] != "healthy":
                    health_status["status"] = "degraded"
            
            # Check cache health
            if hasattr(request.app.state, 'cache'):
                cache_health = await request.app.state.cache.health_check()
                health_status["components"]["cache"] = cache_health
                
                if cache_health["status"] != "healthy":
                    health_status["status"] = "degraded"
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        # Return appropriate status code
        status_code = 200 if health_status["status"] == "healthy" else 503
        return JSONResponse(content=health_status, status_code=status_code)
    
    @app.get("/metrics")
    async def get_metrics(request: Request):
        """Get application metrics (Prometheus format could be added)."""
        metrics = {
            "http_requests_total": 0,  # Would track in middleware
            "http_request_duration_seconds": 0.0,
            "database_connections_active": 0,
            "cache_hit_rate": 0.0,
            "memory_usage_bytes": 0
        }
        
        try:
            # Get database stats
            if hasattr(request.app.state, 'database'):
                db_stats = await request.app.state.database.get_database_stats()
                if 'pool_stats' in db_stats:
                    metrics["database_connections_active"] = db_stats['pool_stats'].get('size', 0)
            
            # Get cache stats
            if hasattr(request.app.state, 'cache'):
                cache_stats = await request.app.state.cache.get_stats()
                if 'memory_cache' in cache_stats:
                    memory_stats = cache_stats['memory_cache']
                    metrics["cache_hit_rate"] = memory_stats.get('hit_rate', 0.0) / 100
                
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
        
        return metrics


def setup_frontend_routes(app: FastAPI):
    """Setup routes for frontend SPA (Single Page Application)."""
    
    @app.get("/")
    async def home_page(request: Request):
        """Home page route."""
        return request.app.state.templates.TemplateResponse(
            "index.html",
            {"request": request, "title": "Python Mastery Hub"}
        )
    
    @app.get("/dashboard")
    async def dashboard_page(request: Request):
        """Dashboard page route."""
        return request.app.state.templates.TemplateResponse(
            "dashboard/overview.html",
            {"request": request, "title": "Dashboard - Python Mastery Hub"}
        )
    
    @app.get("/exercises")
    async def exercises_page(request: Request):
        """Exercises page route."""
        return request.app.state.templates.TemplateResponse(
            "exercises/list.html",
            {"request": request, "title": "Exercises - Python Mastery Hub"}
        )
    
    @app.get("/modules")
    async def modules_page(request: Request):
        """Learning modules page route."""
        return request.app.state.templates.TemplateResponse(
            "modules/list.html",
            {"request": request, "title": "Learning Modules - Python Mastery Hub"}
        )
    
    @app.get("/progress")
    async def progress_page(request: Request):
        """Progress page route."""
        return request.app.state.templates.TemplateResponse(
            "dashboard/progress.html",
            {"request": request, "title": "Progress - Python Mastery Hub"}
        )
    
    @app.get("/login")
    async def login_page(request: Request):
        """Login page route."""
        return request.app.state.templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "title": "Login - Python Mastery Hub"}
        )
    
    @app.get("/register")
    async def register_page(request: Request):
        """Registration page route."""
        return request.app.state.templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "title": "Register - Python Mastery Hub"}
        )
    
    @app.get("/profile")
    async def profile_page(request: Request):
        """User profile page route."""
        return request.app.state.templates.TemplateResponse(
            "auth/profile.html",
            {"request": request, "title": "Profile - Python Mastery Hub"}
        )


# Create the application instance
app = create_application()


# Development server runner
def run_dev_server():
    """Run development server with auto-reload."""
    uvicorn.run(
        "python_mastery_hub.web.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )


# Production server runner
def run_prod_server():
    """Run production server."""
    uvicorn.run(
        "python_mastery_hub.web.main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        log_level="warning",
        access_log=False
    )


if __name__ == "__main__":
    if settings.environment == "development":
        run_dev_server()
    else:
        run_prod_server()