"""
Main Application Entry Point
Refactored modular FastAPI application with dual-database support
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from dotenv import load_dotenv
import os
import logging

# Standardized .env loading
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PROMISE AI API",
    description="AI-powered data analysis and prediction platform with dual-database support (MongoDB/Oracle)",
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

# Startup event: Initialize database connection
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    from app.database.adapters.factory import initialize_database
    
    try:
        db_type = os.getenv('DB_TYPE', 'mongodb')
        logger.info(f"🚀 Starting PROMISE AI with {db_type.upper()} database...")
        await initialize_database()
        logger.info(f"✅ {db_type.upper()} database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {str(e)}")
        raise

# Shutdown event: Close database connection
@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    from app.database.adapters.factory import close_database
    
    try:
        await close_database()
        logger.info("✅ Database connection closed successfully")
    except Exception as e:
        logger.error(f"❌ Error closing database: {str(e)}")

# Import and include routers
from app.routes import datasource, analysis, training, config, models, enhanced_chat, migration

# Create main API router
from fastapi import APIRouter
api_router = APIRouter(prefix="/api")

# Include sub-routers
api_router.include_router(datasource.router)
api_router.include_router(analysis.router)
api_router.include_router(training.router)
api_router.include_router(config.router)  # Database switcher
api_router.include_router(models.router)  # Model management (NEW)
api_router.include_router(enhanced_chat.router)  # Enhanced AI Chat Assistant (NEW)
api_router.include_router(migration.router)  # Database migrations (NEW)

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

# Backward compatibility - datasets endpoint (uses datasource.get_recent_datasets)
@api_router.get("/datasets")
async def get_datasets_compat(limit: int = 10):
    """Backward compatibility for /api/datasets"""
    return await datasource.get_recent_datasets(limit)


# Backward compatibility - get dataset endpoint
@api_router.get("/datasets/{dataset_id}")
async def get_dataset_compat(dataset_id: str):
    """Backward compatibility for /api/datasets/{dataset_id}"""
    from app.routes.datasource import get_dataset
    return await get_dataset(dataset_id)


# Backward compatibility - delete dataset endpoint
@api_router.delete("/datasets/{dataset_id}")
async def delete_dataset_compat(dataset_id: str):
    """Backward compatibility for /api/datasets/{dataset_id}"""
    from app.routes.datasource import delete_dataset
    return await delete_dataset(dataset_id)


# Backward compatibility - training metadata endpoint
@api_router.get("/training-metadata")
async def get_training_metadata_compat():
    """Backward compatibility for /api/training-metadata"""
    from app.routes.training import get_all_training_metadata
    return await get_all_training_metadata()

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
