"""Oracle 23 Database Adapter with async support"""
import json
import logging
import gzip
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

try:
    import cx_Oracle
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False
    logging.warning("cx_Oracle not available. Install with: pip install cx_Oracle")

from .base import DatabaseAdapter

logger = logging.getLogger(__name__)

class OracleAdapter(DatabaseAdapter):
    """Oracle 23 implementation of DatabaseAdapter"""
    
    def __init__(self, connection_string: str, pool_size: int = 10):
        if not ORACLE_AVAILABLE:
            raise ImportError("cx_Oracle is required for Oracle adapter")
        
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.pool = None
        self.executor = ThreadPoolExecutor(max_workers=pool_size)
        logger.info(f"OracleAdapter initialized with pool_size={pool_size}")
    
    async def connect(self):
        """Establish Oracle connection pool"""
        try:
            loop = asyncio.get_event_loop()
            self.pool = await loop.run_in_executor(
                self.executor,
                self._create_pool
            )
            logger.info("✅ Oracle connection pool created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create Oracle pool: {str(e)}")
            raise
    
    def _create_pool(self):
        """Create Oracle connection pool (sync)"""
        return cx_Oracle.SessionPool(
            self.connection_string,
            min=2,
            max=self.pool_size,
            increment=1,
            threaded=True
        )
    
    async def disconnect(self):
        """Close Oracle connection pool"""
        if self.pool:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self.pool.close
            )
            self.executor.shutdown(wait=True)
            logger.info("Oracle connection pool closed")
    
    async def _execute(self, query: str, params: Dict = None, fetch_one=False, fetch_all=False):
        """Execute SQL query asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._execute_sync,
            query,
            params,
            fetch_one,
            fetch_all
        )
    
    def _execute_sync(self, query: str, params: Dict = None, fetch_one=False, fetch_all=False):
        """Execute SQL query (sync)"""
        conn = self.pool.acquire()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or {})
            
            if fetch_one:
                result = cursor.fetchone()
                return self._row_to_dict(cursor, result) if result else None
            elif fetch_all:
                rows = cursor.fetchall()
                return [self._row_to_dict(cursor, row) for row in rows]
            else:
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            conn.rollback()
            logger.error(f"Oracle query error: {str(e)}")
            raise
        finally:
            self.pool.release(conn)
    
    def _row_to_dict(self, cursor, row) -> Dict:
        """Convert Oracle row to dictionary"""
        if not row:
            return None
        columns = [col[0].lower() for col in cursor.description]
        result = dict(zip(columns, row))
        
        # Parse JSON columns
        for key in list(result.keys()):
            if key.endswith('_json') and result[key]:
                try:
                    if isinstance(result[key], cx_Oracle.LOB):
                        json_str = result[key].read()
                    else:
                        json_str = result[key]
                    result[key.replace('_json', '')] = json.loads(json_str)
                    del result[key]
                except:
                    pass
        
        # Convert timestamps
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
        
        return result
    
    # ==================== Dataset Operations ====================
    
    async def create_dataset(self, dataset: Dict[str, Any]) -> str:
        """Create a new dataset"""
        dataset_id = dataset.get('id', str(uuid.uuid4()))
        
        query = """
        INSERT INTO datasets (
            id, name, source, row_count, column_count,
            columns_json, dtypes_json, data_preview_json,
            storage_type, file_id, training_count, created_at
        ) VALUES (
            :id, :name, :source, :row_count, :column_count,
            :columns_json, :dtypes_json, :data_preview_json,
            :storage_type, :file_id, :training_count, :created_at
        )
        """
        
        params = {
            'id': dataset_id,
            'name': dataset.get('name', 'Unnamed'),
            'source': dataset.get('source', 'upload'),
            'row_count': dataset.get('row_count', 0),
            'column_count': dataset.get('column_count', 0),
            'columns_json': json.dumps(dataset.get('columns', [])),
            'dtypes_json': json.dumps(dataset.get('dtypes', {})),
            'data_preview_json': json.dumps(dataset.get('data_preview', [])),
            'storage_type': dataset.get('storage_type', 'direct'),
            'file_id': dataset.get('gridfs_file_id') or dataset.get('file_id'),
            'training_count': dataset.get('training_count', 0),
            'created_at': datetime.now(timezone.utc)
        }
        
        await self._execute(query, params)
        logger.info(f"✅ Created dataset: {dataset_id}")
        return dataset_id
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get dataset by ID"""
        query = """
        SELECT id, name, source, row_count, column_count,
               columns_json, dtypes_json, data_preview_json,
               storage_type, file_id, training_count, 
               created_at, last_trained_at
        FROM datasets
        WHERE id = :id
        """
        
        result = await self._execute(query, {'id': dataset_id}, fetch_one=True)
        if result and result.get('file_id'):
            result['gridfs_file_id'] = result['file_id']
        return result
    
    async def list_datasets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List all datasets"""
        query = """
        SELECT id, name, source, row_count, column_count,
               columns_json, dtypes_json, data_preview_json,
               storage_type, file_id, training_count, 
               created_at, last_trained_at
        FROM datasets
        ORDER BY created_at DESC
        FETCH FIRST :limit ROWS ONLY
        """
        
        results = await self._execute(query, {'limit': limit}, fetch_all=True)
        for result in results:
            if result.get('file_id'):
                result['gridfs_file_id'] = result['file_id']
        return results
    
    async def update_dataset(self, dataset_id: str, updates: Dict[str, Any]) -> bool:
        """Update dataset"""
        # Build dynamic UPDATE query
        set_clauses = []
        params = {'id': dataset_id}
        
        for key, value in updates.items():
            if key in ['columns', 'dtypes', 'data_preview']:
                set_clauses.append(f"{key}_json = :{key}_json")
                params[f"{key}_json"] = json.dumps(value)
            elif key in ['training_count', 'last_trained_at', 'row_count', 'column_count']:
                set_clauses.append(f"{key} = :{key}")
                params[key] = value
        
        if not set_clauses:
            return True
        
        query = f"UPDATE datasets SET {', '.join(set_clauses)} WHERE id = :id"
        rows_affected = await self._execute(query, params)
        return rows_affected > 0
    
    async def delete_dataset(self, dataset_id: str) -> bool:
        """Delete dataset (cascade deletes workspaces and feedback)"""
        query = "DELETE FROM datasets WHERE id = :id"
        rows_affected = await self._execute(query, {'id': dataset_id})
        logger.info(f"✅ Deleted dataset: {dataset_id}")
        return rows_affected > 0
    
    async def increment_training_count(self, dataset_id: str) -> bool:
        """Increment training count"""
        query = """
        UPDATE datasets 
        SET training_count = training_count + 1,
            last_trained_at = :now
        WHERE id = :id
        """
        params = {
            'id': dataset_id,
            'now': datetime.now(timezone.utc)
        }
        rows_affected = await self._execute(query, params)
        return rows_affected > 0
    
    # ==================== File Storage Operations ====================
    
    async def store_file(self, filename: str, data: bytes, metadata: Dict[str, Any]) -> str:
        """Store large file as BLOB"""
        file_id = str(uuid.uuid4())
        
        # Compress if needed
        compressed = metadata.get('compressed', False)
        if compressed:
            data = gzip.compress(data)
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self._store_file_sync,
            file_id,
            filename,
            data,
            metadata,
            compressed
        )
        
        logger.info(f"✅ Stored file: {file_id} ({len(data)} bytes)")
        return file_id
    
    def _store_file_sync(self, file_id: str, filename: str, data: bytes, metadata: Dict, compressed: bool):
        """Store file synchronously"""
        conn = self.pool.acquire()
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO file_storage (
                id, filename, file_data, metadata_json,
                file_size, compressed, original_size, created_at
            ) VALUES (
                :id, :filename, :data, :metadata,
                :size, :compressed, :original_size, :created_at
            )
            """
            
            cursor.execute(query, {
                'id': file_id,
                'filename': filename,
                'data': data,
                'metadata': json.dumps(metadata),
                'size': len(data),
                'compressed': 'Y' if compressed else 'N',
                'original_size': metadata.get('original_size', len(data)),
                'created_at': datetime.now(timezone.utc)
            })
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to store file: {str(e)}")
            raise
        finally:
            self.pool.release(conn)
    
    async def retrieve_file(self, file_id: str) -> bytes:
        """Retrieve file data"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._retrieve_file_sync,
            file_id
        )
    
    def _retrieve_file_sync(self, file_id: str) -> bytes:
        """Retrieve file synchronously"""
        conn = self.pool.acquire()
        try:
            cursor = conn.cursor()
            query = "SELECT file_data, compressed FROM file_storage WHERE id = :id"
            cursor.execute(query, {'id': file_id})
            result = cursor.fetchone()
            
            if not result:
                raise FileNotFoundError(f"File not found: {file_id}")
            
            data, compressed = result
            if isinstance(data, cx_Oracle.LOB):
                data = data.read()
            
            if compressed == 'Y':
                data = gzip.decompress(data)
            
            return data
        finally:
            self.pool.release(conn)
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file"""
        query = "DELETE FROM file_storage WHERE id = :id"
        rows_affected = await self._execute(query, {'id': file_id})
        return rows_affected > 0
    
    # ==================== Workspace Operations ====================
    
    async def save_workspace(self, workspace: Dict[str, Any]) -> str:
        """Save workspace state"""
        workspace_id = workspace.get('id', str(uuid.uuid4()))
        
        query = """
        INSERT INTO workspace_states (
            id, dataset_id, state_name, storage_type, file_id,
            analysis_data_json, chat_history_json,
            size_bytes, compressed_size, created_at, updated_at
        ) VALUES (
            :id, :dataset_id, :state_name, :storage_type, :file_id,
            :analysis_data, :chat_history,
            :size_bytes, :compressed_size, :created_at, :updated_at
        )
        """
        
        params = {
            'id': workspace_id,
            'dataset_id': workspace['dataset_id'],
            'state_name': workspace['state_name'],
            'storage_type': workspace.get('storage_type', 'direct'),
            'file_id': workspace.get('gridfs_file_id'),
            'analysis_data': json.dumps(workspace.get('analysis_data', {})) if workspace.get('storage_type') == 'direct' else None,
            'chat_history': json.dumps(workspace.get('chat_history', [])) if workspace.get('storage_type') == 'direct' else None,
            'size_bytes': workspace.get('size_bytes', 0),
            'compressed_size': workspace.get('compressed_size'),
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
        
        await self._execute(query, params)
        logger.info(f"✅ Saved workspace: {workspace_id}")
        return workspace_id
    
    async def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace by ID"""
        query = """
        SELECT id, dataset_id, state_name, storage_type, file_id,
               analysis_data_json, chat_history_json,
               size_bytes, compressed_size, created_at, updated_at
        FROM workspace_states
        WHERE id = :id
        """
        
        result = await self._execute(query, {'id': workspace_id}, fetch_one=True)
        if result and result.get('file_id'):
            result['gridfs_file_id'] = result['file_id']
        return result
    
    async def list_workspaces(self, dataset_id: str) -> List[Dict[str, Any]]:
        """List workspaces for a dataset"""
        query = """
        SELECT id, dataset_id, state_name, storage_type,
               size_bytes, created_at, updated_at
        FROM workspace_states
        WHERE dataset_id = :dataset_id
        ORDER BY created_at DESC
        """
        
        return await self._execute(query, {'dataset_id': dataset_id}, fetch_all=True)
    
    async def delete_workspace(self, workspace_id: str) -> bool:
        """Delete workspace"""
        query = "DELETE FROM workspace_states WHERE id = :id"
        rows_affected = await self._execute(query, {'id': workspace_id})
        return rows_affected > 0
    
    # ==================== Feedback Operations ====================
    
    async def save_feedback(self, feedback: Dict[str, Any]) -> str:
        """Save prediction feedback"""
        feedback_id = feedback.get('id', str(uuid.uuid4()))
        
        query = """
        INSERT INTO prediction_feedback (
            id, prediction_id, dataset_id, model_name,
            is_correct, prediction, actual_outcome, comment, created_at
        ) VALUES (
            :id, :prediction_id, :dataset_id, :model_name,
            :is_correct, :prediction, :actual_outcome, :comment, :created_at
        )
        """
        
        params = {
            'id': feedback_id,
            'prediction_id': feedback['prediction_id'],
            'dataset_id': feedback['dataset_id'],
            'model_name': feedback['model_name'],
            'is_correct': 'Y' if feedback.get('is_correct') else 'N',
            'prediction': feedback.get('prediction'),
            'actual_outcome': feedback.get('actual_outcome'),
            'comment': feedback.get('comment'),
            'created_at': datetime.now(timezone.utc)
        }
        
        await self._execute(query, params)
        return feedback_id
    
    async def get_feedback_stats(self, dataset_id: str, model_name: str) -> Dict[str, Any]:
        """Get feedback statistics"""
        query = """
        SELECT 
            COUNT(*) as feedback_count,
            SUM(CASE WHEN is_correct = 'Y' THEN 1 ELSE 0 END) as correct_predictions,
            SUM(CASE WHEN is_correct = 'N' THEN 1 ELSE 0 END) as incorrect_predictions
        FROM prediction_feedback
        WHERE dataset_id = :dataset_id AND model_name = :model_name
        """
        
        result = await self._execute(
            query, 
            {'dataset_id': dataset_id, 'model_name': model_name},
            fetch_one=True
        )
        
        if result:
            total = result.get('feedback_count', 0)
            correct = result.get('correct_predictions', 0)
            result['accuracy'] = correct / total if total > 0 else None
        
        return result or {'feedback_count': 0, 'correct_predictions': 0, 'incorrect_predictions': 0, 'accuracy': None}
    
    async def list_feedback(self, dataset_id: str, model_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """List feedback records"""
        query = """
        SELECT id, prediction_id, is_correct, prediction, 
               actual_outcome, comment, created_at
        FROM prediction_feedback
        WHERE dataset_id = :dataset_id AND model_name = :model_name
        ORDER BY created_at DESC
        FETCH FIRST :limit ROWS ONLY
        """
        
        results = await self._execute(
            query,
            {'dataset_id': dataset_id, 'model_name': model_name, 'limit': limit},
            fetch_all=True
        )
        
        # Convert Y/N to boolean
        for result in results:
            result['is_correct'] = result.get('is_correct') == 'Y'
        
        return results
