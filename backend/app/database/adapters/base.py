"""Base Database Adapter Interface"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class DatabaseAdapter(ABC):
    """Abstract base class for database adapters"""
    
    @abstractmethod
    async def connect(self):
        """Establish database connection"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Close database connection"""
        pass
    
    # Dataset Operations
    @abstractmethod
    async def create_dataset(self, dataset: Dict[str, Any]) -> str:
        """Create a new dataset. Returns dataset_id"""
        pass
    
    @abstractmethod
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get dataset by ID"""
        pass
    
    @abstractmethod
    async def list_datasets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List all datasets"""
        pass
    
    @abstractmethod
    async def update_dataset(self, dataset_id: str, updates: Dict[str, Any]) -> bool:
        """Update dataset. Returns success status"""
        pass
    
    @abstractmethod
    async def delete_dataset(self, dataset_id: str) -> bool:
        """Delete dataset and associated data"""
        pass
    
    @abstractmethod
    async def increment_training_count(self, dataset_id: str) -> bool:
        """Increment training count for dataset"""
        pass
    
    # File Storage Operations (GridFS/BLOB)
    @abstractmethod
    async def store_file(self, filename: str, data: bytes, metadata: Dict[str, Any]) -> str:
        """Store large file. Returns file_id"""
        pass
    
    @abstractmethod
    async def retrieve_file(self, file_id: str) -> bytes:
        """Retrieve file data by ID"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_id: str) -> bool:
        """Delete file"""
        pass
    
    # Workspace/State Operations
    @abstractmethod
    async def save_workspace(self, workspace: Dict[str, Any]) -> str:
        """Save workspace state. Returns workspace_id"""
        pass
    
    @abstractmethod
    async def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace by ID"""
        pass
    
    @abstractmethod
    async def list_workspaces(self, dataset_id: str) -> List[Dict[str, Any]]:
        """List workspaces for a dataset"""
        pass
    
    @abstractmethod
    async def delete_workspace(self, workspace_id: str) -> bool:
        """Delete workspace"""
        pass
    
    # Feedback Operations
    @abstractmethod
    async def save_feedback(self, feedback: Dict[str, Any]) -> str:
        """Save prediction feedback. Returns feedback_id"""
        pass
    
    @abstractmethod
    async def get_feedback_stats(self, dataset_id: str, model_name: str) -> Dict[str, Any]:
        """Get feedback statistics for a model"""
        pass
    
    @abstractmethod
    async def list_feedback(self, dataset_id: str, model_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """List feedback records"""
        pass

    
    # Training Metadata Operations
    @abstractmethod
    async def save_training_metadata(self, metadata: Dict[str, Any]) -> str:
        """Save training metadata. Returns metadata_id"""
        pass
    
    @abstractmethod
    async def get_training_metadata(self, dataset_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get training metadata with optional filtering"""
        pass
    
    @abstractmethod
    async def get_training_stats(self, dataset_id: str) -> Dict[str, Any]:
        """Get training statistics for a dataset"""
        pass
    
    @abstractmethod
    async def delete_training_metadata(self, metadata_id: str) -> bool:
        """Delete training metadata by ID"""
        pass
    
    @abstractmethod
    async def get_best_model_for_dataset(self, dataset_id: str, problem_type: str) -> Optional[Dict[str, Any]]:
        """Get the best performing model for a dataset"""
        pass

