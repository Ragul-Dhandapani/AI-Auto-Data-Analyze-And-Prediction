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
    """Clear all training metadata records"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.promise_ai
    
    print("🗑️  Clearing training metadata...")
    
    # Clear saved_states collection (training metadata)
    result = await db.saved_states.delete_many({})
    print(f"✅ Deleted {result.deleted_count} training metadata records")
    
    # Reset training_count in datasets
    datasets_result = await db.datasets.update_many(
        {},
        {"$set": {"training_count": 0, "last_trained_at": None}}
    )
    print(f"✅ Reset training count for {datasets_result.modified_count} datasets")
    
    # Clear prediction feedback
    feedback_result = await db.prediction_feedback.delete_many({})
    print(f"✅ Deleted {feedback_result.deleted_count} feedback records")
    
    print("\n✨ Training metadata cleared successfully!")
    print("📊 Training Metadata module is still intact and will track new analyses")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(clear_training_metadata())
