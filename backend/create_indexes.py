"""
Create MongoDB indexes for better performance
Run this script once to create all necessary indexes
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv

# Standardized .env loading
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def create_indexes():
    """Create all necessary indexes for the application"""
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'autopredict_db')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔧 Creating MongoDB indexes for performance optimization...")
    
    # Datasets collection indexes
    print("\n📊 Creating indexes for 'datasets' collection...")
    await db.datasets.create_index("id", unique=True)
    await db.datasets.create_index("created_at")
    await db.datasets.create_index([("name", 1), ("created_at", -1)])
    print("   ✅ Created indexes on: id, created_at, name")
    
    # Saved states (workspaces) collection indexes
    print("\n💾 Creating indexes for 'saved_states' collection...")
    await db.saved_states.create_index("id", unique=True)
    await db.saved_states.create_index("dataset_id")
    await db.saved_states.create_index([("dataset_id", 1), ("created_at", -1)])
    await db.saved_states.create_index("state_name")
    await db.saved_states.create_index("storage_type")
    print("   ✅ Created indexes on: id, dataset_id, state_name, storage_type")
    
    # Prediction feedback collection indexes
    print("\n👍 Creating indexes for 'prediction_feedback' collection...")
    await db.prediction_feedback.create_index("prediction_id", unique=True)
    await db.prediction_feedback.create_index([("dataset_id", 1), ("model_name", 1)])
    await db.prediction_feedback.create_index("created_at")
    print("   ✅ Created indexes on: prediction_id, dataset_id+model_name, created_at")
    
    # GridFS indexes (if not already created)
    print("\n📁 Creating indexes for GridFS collections...")
    await db.fs.files.create_index("metadata.dataset_id")
    await db.fs.files.create_index("metadata.type")
    print("   ✅ Created indexes on GridFS metadata")
    
    print("\n✨ All indexes created successfully!")
    print("🚀 Database is now optimized for fast queries!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_indexes())
