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
        """Establish MongoDB connection and create indexes"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            self.fs = AsyncIOMotorGridFSBucket(self.db)
            logger.info("✅ MongoDB connection established successfully")
            
            # Create indexes for optimal performance
            await self._create_indexes()
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            raise
    
    async def _create_indexes(self):
        """Create database indexes for performance"""
        try:
            # Workspaces indexes
            await self.db.workspaces.create_index([("id", 1)], unique=True)
            await self.db.workspaces.create_index([("created_at", -1)])
            
            # Datasets indexes
            await self.db.datasets.create_index([("id", 1)], unique=True)
            await self.db.datasets.create_index([("workspace_id", 1)])
            await self.db.datasets.create_index([("created_at", -1)])
            
            # Training metadata indexes
            await self.db.training_metadata.create_index([("dataset_id", 1)])
            await self.db.training_metadata.create_index([("workspace_id", 1)])
            await self.db.training_metadata.create_index([("timestamp", -1)])
            await self.db.training_metadata.create_index([("workspace_id", 1), ("timestamp", -1)])
            
            logger.info("✅ Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Index creation warning (may already exist): {str(e)}")
    
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

    
    # ==================== Training Metadata Operations ====================
    
    async def save_training_metadata(self, metadata: Dict[str, Any]) -> str:
        """Save training metadata"""
        from datetime import datetime, timezone
        
        metadata_id = metadata.get('id', str(uuid.uuid4()))
        
        # Convert feature_variables to string if list
        feature_vars = metadata.get('feature_variables', [])
        if isinstance(feature_vars, list):
            feature_vars = ', '.join(feature_vars)
        
        doc = {
            '_id': metadata_id,
            'dataset_id': metadata['dataset_id'],
            'workspace_id': metadata.get('workspace_id'),  # NEW: Workspace tracking
            'problem_type': metadata['problem_type'],
            'target_variable': metadata['target_variable'],
            'feature_variables': feature_vars,
            'model_type': metadata['model_type'],
            'model_params': metadata.get('model_params', {}),
            'metrics': metadata.get('metrics', {}),
            'training_duration': metadata.get('training_duration', 0.0),
            'timestamp': datetime.now(timezone.utc),  # For 30-day tracking
            'created_at': datetime.now(timezone.utc),
            'automl_enabled': metadata.get('automl_enabled', False),  # NEW
            'hyperparameters_tuned': metadata.get('hyperparameters_tuned', [])  # NEW
        }
        
        await self.db.training_metadata.insert_one(doc)
        logger.info(f"✅ Saved training metadata: {metadata_id} for model {metadata['model_type']}")
        return metadata_id
    
    async def get_training_metadata(
        self, 
        dataset_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get training metadata with optional filtering"""
        query = {}
        if dataset_id:
            query['dataset_id'] = dataset_id
        
        cursor = self.db.training_metadata.find(query).sort('created_at', -1).limit(limit)
        results = await cursor.to_list(length=limit)
        
        # Get dataset names
        for result in results:
            result['id'] = result.pop('_id')
            if result.get('dataset_id'):
                dataset = await self.db.datasets.find_one({'_id': result['dataset_id']})
                result['dataset_name'] = dataset.get('name') if dataset else 'Unknown'
            
            # Convert datetime to string
            if result.get('created_at'):
                result['created_at'] = result['created_at'].isoformat()
        
        return results
    

    async def update_training_metadata_workspace_name(self, dataset_id: str, workspace_name: str):
        """
        Update workspace_name for all training_metadata records of a dataset
        This is called when user saves a workspace to associate training history with the workspace
        """
        result = await self.db.training_metadata.update_many(
            {'dataset_id': dataset_id},
            {'$set': {'workspace_name': workspace_name}}
        )

    async def delete_training_metadata_by_workspace(self, workspace_name: str, dataset_id: Optional[str] = None):
        """
        Delete all training metadata records for a specific workspace
        Optionally filter by dataset_id as well
        """
        query = {'workspace_name': workspace_name}
        if dataset_id:
            query['dataset_id'] = dataset_id
        
        result = await self.db.training_metadata.delete_many(query)
        deleted_count = result.deleted_count
        
        logger.info(f"Deleted {deleted_count} training metadata records for workspace: {workspace_name}")
        return {'deleted_count': deleted_count}

        logger.info(f"Updated {result.modified_count} training metadata records for dataset {dataset_id} with workspace_name: {workspace_name}")
        return result

    async def get_training_stats(self, dataset_id: str) -> Dict[str, Any]:
        """Get training statistics for a dataset"""
        pipeline = [
            {'$match': {'dataset_id': dataset_id}},
            {'$group': {
                '_id': None,
                'total_trainings': {'$sum': 1},
                'unique_models': {'$addToSet': '$model_type'},
                'last_training': {'$max': '$created_at'},
                'first_training': {'$min': '$created_at'}
            }}
        ]
        
        result = await self.db.training_metadata.aggregate(pipeline).to_list(length=1)
        
        if result:
            return {
                'total_trainings': result[0]['total_trainings'],
                'unique_models': len(result[0]['unique_models']),
                'last_training': result[0]['last_training'].isoformat() if result[0].get('last_training') else None,
                'first_training': result[0]['first_training'].isoformat() if result[0].get('first_training') else None
            }
        
        return {
            'total_trainings': 0,
            'unique_models': 0,
            'last_training': None,
            'first_training': None
        }
    
    async def delete_training_metadata(self, metadata_id: str) -> bool:
        """Delete training metadata by ID"""
        result = await self.db.training_metadata.delete_one({'_id': metadata_id})
        return result.deleted_count > 0
    
    async def get_best_model_for_dataset(self, dataset_id: str, problem_type: str) -> Optional[Dict[str, Any]]:
        """Get the best performing model for a dataset"""
        query = {
            'dataset_id': dataset_id,
            'problem_type': problem_type
        }
        
        # Sort by appropriate metric
        if problem_type == 'regression':
            sort_field = 'metrics.r2_score'
        else:
            sort_field = 'metrics.accuracy'
        
        result = await self.db.training_metadata.find_one(
            query,
            sort=[(sort_field, -1)]
        )
        
        if result:
            result['id'] = result.pop('_id')
            if result.get('created_at'):
                result['created_at'] = result['created_at'].isoformat()
        
        return result


    # ==================== Workspace Operations ====================
    
    async def create_workspace(self, workspace: Dict[str, Any]) -> str:
        """Create a new workspace"""
        await self.db.workspaces.insert_one(workspace)
        logger.info(f"✅ Created workspace: {workspace['id']}")
        return workspace['id']
    
    async def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace by ID"""
        workspace = await self.db.workspaces.find_one({"id": workspace_id}, {"_id": 0})
        return workspace
    
    async def get_workspaces(self) -> List[Dict[str, Any]]:
        """Get all workspaces"""
        cursor = self.db.workspaces.find({}, {"_id": 0}).sort("created_at", -1)
        workspaces = await cursor.to_list(length=1000)
        return workspaces
    
    async def get_workspace_datasets(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all datasets in a workspace"""
        cursor = self.db.datasets.find({"workspace_id": workspace_id}, {"_id": 0}).sort("created_at", -1)
        datasets = await cursor.to_list(length=1000)
        return datasets
    
    async def get_workspace_training_history(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get training history for all datasets in workspace"""
        # First get all datasets in workspace
        datasets = await self.get_workspace_datasets(workspace_id)
        dataset_ids = [d["id"] for d in datasets]
        
        if not dataset_ids:
            return []
        
        # Get training metadata for these datasets
        cursor = self.db.training_metadata.find(
            {"dataset_id": {"$in": dataset_ids}},
            {"_id": 0}
        ).sort("timestamp", -1)
        
        history = await cursor.to_list(length=10000)
        return history
    
    async def increment_workspace_dataset_count(self, workspace_id: str) -> bool:
        """Increment dataset count for workspace"""
        result = await self.db.workspaces.update_one(
            {"id": workspace_id},
            {
                "$inc": {"dataset_count": 1},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        return result.modified_count > 0
    
    async def delete_workspace(self, workspace_id: str) -> bool:
        """Delete workspace"""
        result = await self.db.workspaces.delete_one({"id": workspace_id})
        logger.info(f"✅ Deleted workspace: {workspace_id}")
        return result.deleted_count > 0

