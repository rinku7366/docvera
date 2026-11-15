from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.database import create_tables
from app.features.audit.middleware import AuditMiddleware
from app.features.auth.router import router as auth_router
from app.features.documents.router import router as documents_router
from app.features.query.router import router as query_router
from app.features.verification.router import router as verification_router
from app.features.translation.router import router as translation_router
from app.features.audit.router import router as audit_router
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup. Runs once when the server starts."""
    logger.info("DocVera starting up — creating database tables...")
    create_tables()
    logger.info("Database ready.")
    yield
    logger.info("DocVera shutting down.")


app = FastAPI(
    title="DocVera API",
    description="Document intelligence, query, verification, and translation platform.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: allow all origins in development.
# Why: frontend runs on a different port (Vite dev server) from the backend.
# In production, restrict origins to your actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
app.add_middleware(AuditMiddleware)

# Register all feature routers
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(query_router)
app.include_router(verification_router)
app.include_router(translation_router)
app.include_router(audit_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch any unhandled exception and return a clean JSON error.
    Why: never expose raw stack traces to API consumers — they reveal
    implementation details and confuse users. All errors should be
    plain-language messages.
    """
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


@app.get("/health")
def health():
    """Health check endpoint for the frontend and monitoring tools."""
    return {"status": "ok", "service": "DocVera API"}
