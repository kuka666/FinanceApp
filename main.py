from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.util import get_remote_address
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

from config import settings
from limiter import limiter
from routes import information

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} in {'debug' if settings.DEBUG else 'production'} mode")
    yield
    logger.info("Shutting down Financial Advisor API")

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="0.1.0",
    description="API for financial planning and savings calculations",
    lifespan=lifespan,
)

# Set limiter on app state
app.state.limiter = limiter

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourfrontend.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# Include routers
app.include_router(information.router, prefix="/api/v1")

# Root endpoint with rate limiting
@app.get("/", response_model=Dict[str, Any])
@limiter.limit(settings.RATE_LIMIT)
async def read_root(request: Request) -> Dict[str, Any]:
    """Welcome endpoint with API metadata."""
    return {
        "message": f"Welcome to the {settings.APP_NAME}!",
        "version": app.version,
        "debug": settings.DEBUG,
        "docs": f"{request.url}docs",
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions globally."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Please try again later."},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)