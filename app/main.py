"""
California Circuity Factor API - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.database import create_tables, test_connection
from app.routers import circuity

app = FastAPI(
    title="California Circuity Factor API",
    description="Calculate transportation efficiency using circuity factors",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(circuity.router, tags=["circuity"])

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    print("Starting California Circuity Factor API...")
    print("Creating database tables...")
    create_tables()
    
    db_connected = test_connection()
    print(f"🗄️  Database: {'Connected' if db_connected else 'Failed'}")
    
    from app.services.distance_service import DistanceService
    distance_service = DistanceService()
    osrm_connected = distance_service.test_osrm_connection()
    print(f"OSRM: {'Connected' if osrm_connected else 'Failed'}")
    
    if db_connected and osrm_connected:
        print("All services ready!")
    else:
        print("Some services are not available")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "California Circuity Factor API",
        "version": "1.0.0",
        "description": "Calculate transportation efficiency using circuity factors",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "calculate": "POST /calculate - Calculate circuity between two points",
            "history": "GET /history - Get calculation history", 
            "stats": "GET /stats - Get calculation statistics",
            "health": "GET /health - Service health check"
        }
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)