"""
CrimeLens AI — FastAPI Application Entry Point
=================================================
Assembles the complete FastAPI application with:
- Lifespan events (DB connect/disconnect)
- CORS middleware
- Rate limiting middleware
- All API routers
- Global exception handlers
- Health check endpoint
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import connect_to_mongodb, close_mongodb_connection
from app.middleware.rate_limiter import RateLimiterMiddleware

# Import all routers
from app.routers import auth, cases, evidence, search, reports, admin, analytics


# ── Lifespan Events ─────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    # Startup
    settings = get_settings()
    print(f"[CrimeLens] Starting {settings.app_name} v{settings.app_version}")

    # Ensure upload and export directories exist
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    settings.export_path.mkdir(parents=True, exist_ok=True)

    # Connect to MongoDB
    await connect_to_mongodb()

    print(f"[CrimeLens] Application ready.")
    yield

    # Shutdown
    await close_mongodb_connection()
    print("[CrimeLens] Application shut down.")


# ── App Factory ──────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """
    Application factory.
    Constructs and configures the FastAPI instance.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-Powered Digital Forensics & Crime Investigation Platform",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin for origin in settings.cors_origin_list if "*" not in origin],
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Rate Limiter ──
    app.add_middleware(RateLimiterMiddleware)

    # ── Routers ──
    api_prefix = "/api"
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(cases.router, prefix=api_prefix)
    app.include_router(evidence.router, prefix=api_prefix)
    app.include_router(search.router, prefix=api_prefix)
    app.include_router(reports.router, prefix=api_prefix)
    app.include_router(admin.router, prefix=api_prefix)
    app.include_router(analytics.router, prefix=api_prefix)

    # ── Exception Handlers ──
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Clean and format validation errors into a readable string
        error_msgs = []
        for error in exc.errors():
            field = str(error.get("loc", [])[-1]) if error.get("loc") else "field"
            msg = error.get("msg", "validation error")
            error_msgs.append(f"Invalid {field}: {msg}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"success": False, "message": " | ".join(error_msgs)},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        print(f"[CrimeLens] Unhandled error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal server error."},
        )

    # ── Health Check ──
    @app.get("/health", tags=["System"])
    async def health_check():
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
        }

    @app.get("/", tags=["System"])
    async def root():
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
        }

    return app


# Create the app instance
app = create_app()
