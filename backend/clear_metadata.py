"""
Script to clear all training metadata from the database
Keeps the module intact, only removes records
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def clear_training_metadata():
    """Clear all training metadata and datasets"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'autopredict_db')  # Use correct DB name
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f"🗑️  Clearing all data from database: {db_name}...")
    
    # Clear datasets collection
    datasets_result = await db.datasets.delete_many({})
    print(f"✅ Deleted {datasets_result.deleted_count} datasets")
    
    # Clear saved_states collection (training metadata)
    result = await db.saved_states.delete_many({})
    print(f"✅ Deleted {result.deleted_count} training metadata records")
    
    # Clear prediction feedback
    feedback_result = await db.prediction_feedback.delete_many({})
    print(f"✅ Deleted {feedback_result.deleted_count} feedback records")
    
    # Clear any GridFS files (for large datasets)
    fs_files = await db.fs.files.delete_many({})
    fs_chunks = await db.fs.chunks.delete_many({})
    print(f"✅ Deleted {fs_files.deleted_count} GridFS files and {fs_chunks.deleted_count} chunks")
    
    print("\n✨ All data cleared successfully!")
    print("📊 Database is now clean and ready for new analyses")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(clear_training_metadata())
