"""
RecoverAI FastAPI Application Entry Point.
Provides core REST endpoints, CORS support, and automatic database seeding.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from database import seed_database_if_empty, engine
from routes.api import router as buildathon_api_router
from routes.dashboard import router as dashboard_router
from routes.transactions import router as transactions_router
from routes.evaluation import router as evaluation_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist and database has seed data
    print("Initializing RecoverAI database...")
    try:
        seed_database_if_empty()
    except Exception as e:
        print(f"[WARNING] Database initialization encountered an error: {e}. RecoverAI continuing with operational endpoints.")
    yield
    print("RecoverAI shutdown.")

app = FastAPI(
    title="RecoverAI - Context-Aware Autonomous Revenue Recovery Agent",
    description="Production-style revenue recovery decision engine with counterfactual strategy evaluation and deterministic safety policies for Razorpay Buildathon Track 3.",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS for local development and deployed Render frontend
frontend_url = os.getenv("FRONTEND_URL", "").strip()
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

if frontend_url:
    for origin in frontend_url.split(","):
        clean = origin.strip().rstrip("/")
        if clean:
            if clean.startswith("http://") or clean.startswith("https://"):
                if clean not in allowed_origins:
                    allowed_origins.append(clean)
            else:
                allowed_origins.append(f"https://{clean}")
                allowed_origins.append(f"http://{clean}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if frontend_url else ["*"],
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes: primary /api router + legacy fallback routers
app.include_router(buildathon_api_router)
app.include_router(dashboard_router)
app.include_router(transactions_router)
app.include_router(evaluation_router)

@app.get("/", tags=["Root"])
def root_endpoint() -> Dict[str, Any]:
    """Root endpoint confirming API status and providing quick documentation links."""
    return {
        "service": "RecoverAI — Context-Aware Autonomous Revenue Recovery Agent",
        "track": "Razorpay Buildathon Track 3: AI Revenue Recovery",
        "status": "operational",
        "version": "2.0.0",
        "docs_url": "/docs",
        "health_url": "/health",
        "endpoints": {
            "dashboard_metrics": "/api/dashboard/metrics",
            "transactions": "/api/transactions",
            "rag_evaluation": "/rag/evaluation"
        }
    }

@app.get("/health", tags=["Health"])
def health_check() -> Dict[str, Any]:
    """Health check endpoint confirming backend operational status."""
    db_url_str = str(engine.url)
    db_type = "Supabase PostgreSQL" if "postgres" in db_url_str else "SQLite (recoverai.db)"
    return {
        "status": "healthy",
        "service": "RecoverAI Backend",
        "version": "2.0.0",
        "database": db_type,
        "guardrails": "Active",
        "rag_engine": "Operational"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=False)
