"""
Script to completely clear all datasets, training metadata, and workspace data
Provides a fresh start for PROMISE AI
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

async def clear_all_data():
    """Clear all datasets, training metadata, and workspace data"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.promise_ai
    
    print("🗑️  Clearing ALL data from PROMISE AI...")
    print("=" * 50)
    
    # 1. Clear datasets collection
    datasets_result = await db.datasets.delete_many({})
    print(f"✅ Deleted {datasets_result.deleted_count} datasets")
    
    # 2. Clear all data_* collections (actual dataset data)
    collection_names = await db.list_collection_names()
    data_collections_deleted = 0
    for collection_name in collection_names:
        if collection_name.startswith('data_'):
            await db[collection_name].drop()
            data_collections_deleted += 1
    print(f"✅ Dropped {data_collections_deleted} dataset data collections")
    
    # 3. Clear saved_states collection (training metadata)
    saved_states_result = await db.saved_states.delete_many({})
    print(f"✅ Deleted {saved_states_result.deleted_count} training metadata records")
    
    # 4. Clear prediction feedback
    feedback_result = await db.prediction_feedback.delete_many({})
    print(f"✅ Deleted {feedback_result.deleted_count} feedback records")
    
    # 5. Clear any workspace saves (if exists)
    if 'workspaces' in collection_names:
        workspace_result = await db.workspaces.delete_many({})
        print(f"✅ Deleted {workspace_result.deleted_count} workspace saves")
    
    print("=" * 50)
    print("\n✨ All data cleared successfully!")
    print("📊 PROMISE AI is now in pristine state")
    print("🚀 Ready for fresh analyses with updated features")
    print("\n💡 Note: Modules and codebase are intact - only data was cleared")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(clear_all_data())
