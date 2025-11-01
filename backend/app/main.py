"""
Main Application Entry Point
Refactored modular FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title="PROMISE AI API",
    description="AI-powered data analysis and prediction platform",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.routes import datasource, analysis, training

# Create main API router
from fastapi import APIRouter
api_router = APIRouter(prefix="/api")

# Include sub-routers
api_router.include_router(datasource.router)
api_router.include_router(analysis.router)
api_router.include_router(training.router)

# Add root endpoint
@api_router.get("/")
async def root():
    return {
        "message": "AutoPredict API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "datasource": "/api/datasource",
            "analysis": "/api/analysis",
            "training": "/api/training"
        }
    }

# Backward compatibility - datasets endpoint
@api_router.get("/datasets")
async def get_datasets_compat():
    """Backward compatibility for /api/datasets"""
    from app.database.mongodb import db
    try:
        cursor = db.datasets.find({}, {"_id": 0}).sort("created_at", -1).limit(10)
        datasets = await cursor.to_list(length=10)
        return {"datasets": datasets}  # Frontend expects {datasets: [...]}
    except Exception as e:
        return {"datasets": []}

# Backward compatibility - training metadata endpoint
@api_router.get("/training-metadata")
async def get_training_metadata_compat():
    """Backward compatibility for /api/training-metadata"""
    from app.routes.training import get_training_metadata
    return await get_training_metadata()

# Include main router
app.include_router(api_router)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
