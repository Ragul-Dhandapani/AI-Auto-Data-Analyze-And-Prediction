"""
MongoDB Connection and GridFS Setup
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from app.config import MONGO_URL, DB_NAME

# MongoDB client and database
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# GridFS for large file storage
fs = AsyncIOMotorGridFSBucket(db)

async def get_database():
    """Get database instance"""
    return db

async def get_gridfs():
    """Get GridFS instance"""
    return fs
