"""
RecoverAI FastAPI Application Entry Point.
Provides core REST endpoints, CORS support, and automatic database seeding.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from database import seed_database_if_empty
from routes.api import router as buildathon_api_router
from routes.dashboard import router as dashboard_router
from routes.transactions import router as transactions_router
from routes.evaluation import router as evaluation_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist and database has seed data
    print("Initializing RecoverAI database...")
    seed_database_if_empty()
    yield
    print("RecoverAI shutdown.")

app = FastAPI(
    title="RecoverAI - Context-Aware Autonomous Revenue Recovery Agent",
    description="Production-style revenue recovery decision engine with counterfactual strategy evaluation and deterministic safety policies for Razorpay Buildathon Track 3.",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS for seamless frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes: primary /api router + legacy fallback routers
app.include_router(buildathon_api_router)
app.include_router(dashboard_router)
app.include_router(transactions_router)
app.include_router(evaluation_router)

@app.get("/health", tags=["Health"])
def health_check() -> Dict[str, Any]:
    """Health check endpoint confirming backend operational status."""
    return {
        "status": "healthy",
        "service": "RecoverAI Backend",
        "version": "1.0.0",
        "database": "SQLite (recoverai.db)",
        "guardrails": "Active",
        "rag_engine": "Operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
