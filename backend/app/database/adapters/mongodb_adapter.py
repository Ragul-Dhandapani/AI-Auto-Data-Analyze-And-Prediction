"""MongoDB Database Adapter - Wraps existing MongoDB code"""
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
import gzip

from .base import DatabaseAdapter

logger = logging.getLogger(__name__)

class MongoDBAdapter(DatabaseAdapter):
    """MongoDB implementation of DatabaseAdapter"""
    
    def __init__(self, mongo_url: str, db_name: str):
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.client = None
        self.db = None
        self.fs = None
        logger.info(f"MongoDBAdapter initialized for database: {db_name}")
    
    async def connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            self.fs = AsyncIOMotorGridFSBucket(self.db)
            logger.info("✅ MongoDB connection established successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            raise
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    # ==================== Dataset Operations ====================
    
    async def create_dataset(self, dataset: Dict[str, Any]) -> str:
        """Create a new dataset"""
        dataset_id = dataset.get('id')
        
        # Ensure created_at is string
        if 'created_at' in dataset and isinstance(dataset['created_at'], datetime):
            dataset['created_at'] = dataset['created_at'].isoformat()
        
        await self.db.datasets.insert_one(dataset)
        logger.info(f"✅ Created dataset: {dataset_id}")
        return dataset_id
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get dataset by ID"""
        dataset = await self.db.datasets.find_one({"id": dataset_id}, {"_id": 0})
        return dataset
    
    async def list_datasets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List all datasets"""
        cursor = self.db.datasets.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
        datasets = await cursor.to_list(length=limit)
        return datasets
    
    async def update_dataset(self, dataset_id: str, updates: Dict[str, Any]) -> bool:
        """Update dataset"""
        result = await self.db.datasets.update_one(
            {"id": dataset_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def delete_dataset(self, dataset_id: str) -> bool:
        """Delete dataset and associated data"""
        # Delete dataset
        result = await self.db.datasets.delete_one({"id": dataset_id})
        
        # Delete associated workspaces
        await self.db.saved_states.delete_many({"dataset_id": dataset_id})
        
        # Delete associated feedback
        await self.db.prediction_feedback.delete_many({"dataset_id": dataset_id})
        
        # Delete GridFS files
        cursor = self.db.fs.files.find({"metadata.dataset_id": dataset_id})
        async for file_doc in cursor:
            await self.fs.delete(file_doc["_id"])
        
        logger.info(f"✅ Deleted dataset and associated data: {dataset_id}")
        return result.deleted_count > 0
    
    async def increment_training_count(self, dataset_id: str) -> bool:
        """Increment training count for dataset"""
        result = await self.db.datasets.update_one(
            {"id": dataset_id},
            {
                "$inc": {"training_count": 1},
                "$set": {"last_trained_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        return result.modified_count > 0
    
    # ==================== File Storage Operations (GridFS) ====================
    
    async def store_file(self, filename: str, data: bytes, metadata: Dict[str, Any]) -> str:
        """Store large file in GridFS"""
        # Compress if requested
        compressed = metadata.get('compressed', False)
        original_size = len(data)
        
        if compressed:
            data = gzip.compress(data)
            metadata['original_size'] = original_size
            metadata['compressed_size'] = len(data)
        
        file_id = await self.fs.upload_from_stream(
            filename,
            data,
            metadata=metadata
        )
        
        logger.info(f"✅ Stored file in GridFS: {file_id} ({len(data)} bytes)")
        return str(file_id)
    
    async def retrieve_file(self, file_id: str) -> bytes:
        """Retrieve file data from GridFS"""
        from bson import ObjectId
        
        grid_out = await self.fs.open_download_stream(ObjectId(file_id))
        data = await grid_out.read()
        
        # Check if compressed
        metadata = grid_out.metadata
        if metadata and metadata.get('compressed'):
            data = gzip.decompress(data)
        
        return data
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file from GridFS"""
        from bson import ObjectId
        try:
            await self.fs.delete(ObjectId(file_id))
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {file_id}: {str(e)}")
            return False
    
    # ==================== Workspace Operations ====================
    
    async def save_workspace(self, workspace: Dict[str, Any]) -> str:
        """Save workspace state"""
        workspace_id = workspace.get('id')
        
        # Ensure timestamps are strings
        if 'created_at' in workspace and isinstance(workspace['created_at'], datetime):
            workspace['created_at'] = workspace['created_at'].isoformat()
        if 'updated_at' in workspace and isinstance(workspace['updated_at'], datetime):
            workspace['updated_at'] = workspace['updated_at'].isoformat()
        
        await self.db.saved_states.insert_one(workspace)
        logger.info(f"✅ Saved workspace: {workspace_id}")
        return workspace_id
    
    async def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace by ID"""
        workspace = await self.db.saved_states.find_one({"id": workspace_id}, {"_id": 0})
        return workspace
    
    async def list_workspaces(self, dataset_id: str) -> List[Dict[str, Any]]:
        """List workspaces for a dataset"""
        cursor = self.db.saved_states.find(
            {"dataset_id": dataset_id},
            {"id": 1, "state_name": 1, "created_at": 1, "size_bytes": 1, "_id": 0}
        ).sort("created_at", -1)
        
        workspaces = await cursor.to_list(length=100)
        return workspaces
    
    async def delete_workspace(self, workspace_id: str) -> bool:
        """Delete workspace"""
        # Get workspace to find GridFS file if exists
        workspace = await self.db.saved_states.find_one({"id": workspace_id})
        
        if workspace:
            # Delete GridFS file if exists
            if workspace.get('storage_type') == 'gridfs' and workspace.get('gridfs_file_id'):
                await self.delete_file(workspace['gridfs_file_id'])
            
            # Delete workspace document
            result = await self.db.saved_states.delete_one({"id": workspace_id})
            return result.deleted_count > 0
        
        return False
    
    # ==================== Feedback Operations ====================
    
    async def save_feedback(self, feedback: Dict[str, Any]) -> str:
        """Save prediction feedback"""
        feedback_id = feedback.get('id')
        
        # Ensure timestamp is string
        if 'timestamp' in feedback and isinstance(feedback['timestamp'], datetime):
            feedback['timestamp'] = feedback['timestamp'].isoformat()
        elif 'timestamp' not in feedback:
            feedback['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        await self.db.prediction_feedback.insert_one(feedback)
        logger.info(f"✅ Saved feedback: {feedback_id}")
        return feedback_id
    
    async def get_feedback_stats(self, dataset_id: str, model_name: str) -> Dict[str, Any]:
        """Get feedback statistics for a model"""
        pipeline = [
            {
                "$match": {
                    "dataset_id": dataset_id,
                    "model_name": model_name
                }
            },
            {
                "$group": {
                    "_id": None,
                    "feedback_count": {"$sum": 1},
                    "correct_predictions": {
                        "$sum": {"$cond": ["$is_correct", 1, 0]}
                    },
                    "incorrect_predictions": {
                        "$sum": {"$cond": ["$is_correct", 0, 1]}
                    }
                }
            }
        ]
        
        result = await self.db.prediction_feedback.aggregate(pipeline).to_list(length=1)
        
        if result:
            stats = result[0]
            total = stats.get('feedback_count', 0)
            correct = stats.get('correct_predictions', 0)
            stats['accuracy'] = correct / total if total > 0 else None
            del stats['_id']
            return stats
        
        return {
            'feedback_count': 0,
            'correct_predictions': 0,
            'incorrect_predictions': 0,
            'accuracy': None
        }
    
    async def list_feedback(self, dataset_id: str, model_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """List feedback records"""
        cursor = self.db.prediction_feedback.find(
            {
                "dataset_id": dataset_id,
                "model_name": model_name
            },
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit)
        
        feedback_list = await cursor.to_list(length=limit)
        return feedback_list
