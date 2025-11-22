"""Oracle 19c/21c/23ai Database Adapter with async support"""
import json
import logging
import gzip
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

try:
    import cx_Oracle
    # Initialize Oracle Client with library path
    try:
        cx_Oracle.init_oracle_client(lib_dir='/opt/oracle/instantclient_19_23')
        logger = logging.getLogger(__name__)
        logger.info("✅ Oracle Client initialized")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Oracle Client may already be initialized: {str(e)}")
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("cx_Oracle not available. Install with: pip install cx_Oracle")

from .base import DatabaseAdapter

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
        """Create Oracle connection pool (sync) - supports both Kerberos and standard auth"""
        try:
            # Initialize Oracle Instant Client
            try:
                cx_Oracle.init_oracle_client(lib_dir='/opt/oracle/instantclient_19_23')
                logger.info("✅ Oracle Client initialized")
            except cx_Oracle.ProgrammingError:
                # Already initialized
                logger.info("⚠️ Oracle Client already initialized")
            except Exception as e:
                logger.warning(f"Oracle Client init warning: {e}")
            
            # Check if using Kerberos/external authentication
            use_kerberos = os.getenv('ORACLE_USE_KERBEROS', 'false').lower() == 'true'
            
            if use_kerberos:
                # Kerberos/External Authentication
                logger.info("🔐 Using Kerberos/External Authentication")
                return self._create_pool_kerberos()
            else:
                # Standard username/password authentication
                logger.info("🔑 Using standard username/password authentication")
                return self._create_pool_standard()
                
        except Exception as e:
            logger.error(f"Failed to create connection pool: {str(e)}")
            raise
    
    def _create_pool_kerberos(self):
        """Create Oracle SessionPool with Kerberos/External authentication"""
        host = os.getenv('ORACLE_HOST')
        port = os.getenv('ORACLE_PORT', '1521')
        service_name = os.getenv('ORACLE_SERVICE_NAME')
        
        if not all([host, service_name]):
            raise ValueError("ORACLE_HOST and ORACLE_SERVICE_NAME required for Kerberos auth")
        
        # Create DSN without credentials
        dsn = cx_Oracle.makedsn(host, int(port), service_name=service_name)
        
        logger.info(f"🔐 Kerberos connection to {host}:{port}/{service_name}")
        
        # Create SessionPool with external auth
        # DO NOT pass user/password when using external_auth=True
        return cx_Oracle.SessionPool(
            dsn=dsn,
            min=2,
            max=self.pool_size,
            increment=1,
            threaded=True,
            external_auth=True  # Uses Kerberos/OS authentication
        )
    
    def _create_pool_standard(self):
        """Create Oracle SessionPool with username/password"""
        # Try to get credentials from environment or parse connection string
        user = os.getenv('ORACLE_USER')
        password = os.getenv('ORACLE_PASSWORD')
        host = os.getenv('ORACLE_HOST')
        port = os.getenv('ORACLE_PORT', '1521')
        service_name = os.getenv('ORACLE_SERVICE_NAME')
        
        # If env vars not set, try parsing connection string
        if not all([user, password, host, service_name]):
            # Parse connection string: user/password@host:port/service_name
            parts = self.connection_string.split('@')
            if len(parts) == 2:
                user_pass = parts[0].split('/')
                host_info = parts[1]
                
                user = user_pass[0]
                password = user_pass[1]
                host = host_info.split(':')[0]
                port = host_info.split(':')[1].split('/')[0]
                service_name = host_info.split('/')[-1]
            else:
                # Fallback to direct connection string
                logger.warning("Using direct connection string (not recommended)")
                return cx_Oracle.SessionPool(
                    self.connection_string,
                    min=2,
                    max=self.pool_size,
                    increment=1,
                    threaded=True
                )
        
        # Create DSN
        dsn = cx_Oracle.makedsn(host, int(port), service_name=service_name)
        
        logger.info(f"🔑 Standard auth for {user}@{host}:{port}/{service_name}")
        
        # Create SessionPool with credentials
        # DO NOT use external_auth when passing user/password
        return cx_Oracle.SessionPool(
            user=user,
            password=password,
            dsn=dsn,
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
        
        # Read all LOB objects first (must happen in sync context)
        for key, value in list(result.items()):
            if isinstance(value, cx_Oracle.LOB):
                try:
                    result[key] = value.read()
                except Exception as e:
                    logger.warning(f"Failed to read LOB for {key}: {e}")
                    result[key] = None
        
        # Parse JSON columns (both _json suffix and CLOB fields)
        json_fields = ['columns', 'dtypes', 'data_preview', 'tags', 'feature_variables', 
                      'metrics', 'model_params', 'hyperparameters_tuned']
        
        for key in list(result.keys()):
            if key.endswith('_json') and result[key]:
                try:
                    json_str = result[key]
                    result[key.replace('_json', '')] = json.loads(json_str)
                    del result[key]
                except Exception as e:
                    logger.warning(f"Failed to parse JSON for {key}: {e}")
                    pass
            elif key in json_fields and result[key] and isinstance(result[key], str):
                try:
                    result[key] = json.loads(result[key])
                except Exception as e:
                    logger.warning(f"Failed to parse JSON for {key}: {e}")
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
        INSERT INTO DATASETS (
            ID, WORKSPACE_ID, NAME, ROW_COUNT, COLUMN_COUNT,
            COLUMNS, DTYPES, DATA_PREVIEW,
            STORAGE_TYPE, GRIDFS_FILE_ID, SOURCE_TYPE, FILE_SIZE,
            TRAINING_COUNT, CREATED_AT, UPDATED_AT
        ) VALUES (
            :id, :workspace_id, :name, :row_count, :column_count,
            :columns, :dtypes, :data_preview,
            :storage_type, :gridfs_file_id, :source_type, :file_size,
            :training_count, :created_at, :updated_at
        )
        """
        
        # Validate and serialize JSON fields (handle NaN, inf, etc.)
        try:
            columns_json = json.dumps(dataset.get('columns', []), allow_nan=False)
        except ValueError as e:
            logger.warning(f"Invalid columns data, using empty array: {e}")
            columns_json = json.dumps([])
        
        try:
            dtypes_json = json.dumps(dataset.get('dtypes', {}), allow_nan=False)
        except ValueError as e:
            logger.warning(f"Invalid dtypes data, using empty object: {e}")
            dtypes_json = json.dumps({})
        
        try:
            data_preview_json = json.dumps(dataset.get('data_preview', []), allow_nan=False)
        except ValueError as e:
            logger.warning(f"Invalid data_preview, using empty array: {e}")
            data_preview_json = json.dumps([])
        
        params = {
            'id': dataset_id,
            'workspace_id': dataset.get('workspace_id'),
            'name': dataset.get('name', 'Unnamed'),
            'row_count': dataset.get('row_count', 0),
            'column_count': dataset.get('column_count', 0),
            'columns': columns_json,
            'dtypes': dtypes_json,
            'data_preview': data_preview_json,
            'storage_type': dataset.get('storage_type', 'direct'),
            'gridfs_file_id': dataset.get('gridfs_file_id'),
            'source_type': dataset.get('source_type', 'file_upload'),
            'file_size': dataset.get('file_size', 0),
            'training_count': dataset.get('training_count', 0),
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
        
        await self._execute(query, params)
        logger.info(f"✅ Created dataset: {dataset_id}")
        return dataset_id
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get dataset by ID"""
        query = """
        SELECT ID, WORKSPACE_ID, NAME, ROW_COUNT, COLUMN_COUNT,
               COLUMNS, DTYPES, DATA_PREVIEW,
               STORAGE_TYPE, GRIDFS_FILE_ID, SOURCE_TYPE, FILE_SIZE,
               TRAINING_COUNT, CREATED_AT, LAST_TRAINED_AT, UPDATED_AT
        FROM DATASETS
        WHERE ID = :id
        """
        
        result = await self._execute(query, {'id': dataset_id}, fetch_one=True)
        # LOB reading and JSON parsing already handled by _row_to_dict
        return result
    
    async def list_datasets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List all datasets"""
        query = """
        SELECT ID, WORKSPACE_ID, NAME, ROW_COUNT, COLUMN_COUNT,
               COLUMNS, DTYPES, DATA_PREVIEW,
               STORAGE_TYPE, GRIDFS_FILE_ID, SOURCE_TYPE, FILE_SIZE,
               TRAINING_COUNT, CREATED_AT, LAST_TRAINED_AT, UPDATED_AT
        FROM DATASETS
        ORDER BY CREATED_AT DESC
        FETCH FIRST :limit ROWS ONLY
        """
        
        results = await self._execute(query, {'limit': limit}, fetch_all=True)
        # LOB reading and JSON parsing already handled by _row_to_dict
        return results
    
    async def update_dataset(self, dataset_id: str, updates: Dict[str, Any]) -> bool:
        """Update dataset"""
        from datetime import datetime
        
        # Build dynamic UPDATE query
        set_clauses = []
        params = {'id': dataset_id}
        
        for key, value in updates.items():
            if key in ['columns', 'dtypes', 'data_preview']:
                set_clauses.append(f"{key}_json = :{key}_json")
                params[f"{key}_json"] = json.dumps(value)
            elif key in ['training_count', 'row_count', 'column_count']:
                set_clauses.append(f"{key} = :{key}")
                params[key] = value
            elif key in ['last_trained_at', 'created_at']:
                # Handle datetime fields - convert ISO string to Oracle format
                set_clauses.append(f"{key} = :{key}")
                if isinstance(value, str):
                    # Parse ISO format and convert to Python datetime
                    try:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        params[key] = dt
                    except:
                        params[key] = value
                else:
                    params[key] = value
        
        if not set_clauses:
            return True
        
        query = f"UPDATE datasets SET {', '.join(set_clauses)} WHERE id = :id"
        rows_affected = await self._execute(query, params)
        return rows_affected > 0
    
    async def delete_dataset(self, dataset_id: str) -> bool:
        """Delete dataset (cascade deletes workspaces, files, and feedback)"""
        try:
            # First, get the dataset to find associated file_id
            dataset = await self.get_dataset(dataset_id)
            
            if dataset and dataset.get('file_id'):
                # Delete associated file from BLOB storage
                try:
                    await self.delete_file(dataset['file_id'])
                    logger.info(f"✅ Deleted associated file: {dataset['file_id']}")
                except Exception as e:
                    logger.warning(f"Could not delete file {dataset['file_id']}: {e}")
            
            # Delete the dataset (CASCADE constraints will handle workspaces/feedback)
            query = "DELETE FROM datasets WHERE id = :id"
            rows_affected = await self._execute(query, {'id': dataset_id})
            logger.info(f"✅ Deleted dataset: {dataset_id}")
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Error deleting dataset {dataset_id}: {e}")
            raise
    
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
            # Use DATASET_BLOBS table with correct schema
            query = """
            INSERT INTO DATASET_BLOBS (
                ID, DATASET_ID, FILENAME, CONTENT_TYPE, FILE_DATA, CREATED_AT
            ) VALUES (
                :file_id, :dataset_id, :filename, :content_type, :file_data, :created_at
            )
            """
            
            cursor.execute(query, {
                'file_id': file_id,
                'dataset_id': metadata.get('dataset_id', file_id),
                'filename': filename,
                'content_type': metadata.get('content_type', 'application/octet-stream'),
                'file_data': data,
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
            query = "SELECT FILE_DATA FROM DATASET_BLOBS WHERE ID = :id"
            cursor.execute(query, {'id': file_id})
            result = cursor.fetchone()
            
            if not result:
                raise FileNotFoundError(f"File not found: {file_id}")
            
            data = result[0]
            if isinstance(data, cx_Oracle.LOB):
                data = data.read()
            
            if compressed == 'Y':
                data = gzip.decompress(data)
            
            return data
        finally:
            self.pool.release(conn)
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file"""
        query = "DELETE FROM DATASET_BLOBS WHERE ID = :id"
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
            is_correct, prediction, actual_outcome, feedback_comment, created_at
        ) VALUES (
            :id, :prediction_id, :dataset_id, :model_name,
            :is_correct, :prediction, :actual_outcome, :feedback_comment, :created_at
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
            'feedback_comment': feedback.get('comment'),  # Map 'comment' to 'feedback_comment'
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
               actual_outcome, feedback_comment as comment, created_at
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

    
    # ==================== Training Metadata Operations ====================
    
    async def save_training_metadata(self, metadata: Dict[str, Any]) -> str:
        """
        Save training metadata for ML model training session
        
        Args:
            metadata: {
                'id': str (optional, will generate if not provided),
                'dataset_id': str,
                'problem_type': str,
                'target_variable': str,
                'feature_variables': List[str] or str,
                'model_type': str,
                'model_params': dict (optional),
                'metrics': dict,
                'training_duration': float
            }
        
        Returns:
            str: metadata_id
        """
        import json
        from datetime import datetime, timezone
        
        metadata_id = metadata.get('id', str(uuid.uuid4()))
        
        # Convert feature_variables to string if list
        feature_vars = metadata.get('feature_variables', [])
        if isinstance(feature_vars, list):
            feature_vars = ', '.join(feature_vars)
        
        # Convert dicts to JSON strings
        model_params_json = json.dumps(metadata.get('model_params', {}))
        metrics_json = json.dumps(metadata.get('metrics', {}))
        
        query = """
        INSERT INTO training_metadata (
            id, dataset_id, workspace_name, problem_type, target_variable, feature_variables,
            model_type, model_params_json, metrics_json, training_duration, created_at
        ) VALUES (
            :id, :dataset_id, :workspace_name, :problem_type, :target_variable, :feature_variables,
            :model_type, :model_params_json, :metrics_json, :training_duration, :created_at
        )
        """
        
        params = {
            'id': metadata_id,
            'dataset_id': metadata['dataset_id'],
            'workspace_name': metadata.get('workspace_name', 'default'),
            'problem_type': metadata['problem_type'],
            'target_variable': metadata['target_variable'],
            'feature_variables': feature_vars,
            'model_type': metadata['model_type'],
            'model_params_json': model_params_json,
            'metrics_json': metrics_json,
            'training_duration': metadata.get('training_duration', 0.0),
            'created_at': datetime.now(timezone.utc)
        }
        
        await self._execute(query, params)
        logger.info(f"✅ Saved training metadata: {metadata_id} for model {metadata['model_type']}")
        return metadata_id
    
    async def get_training_metadata(
        self, 
        dataset_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get training metadata with optional filtering
        
        Args:
            dataset_id: Optional filter by dataset
            limit: Maximum number of records to return
        
        Returns:
            List of training metadata records
        """
        import json
        
        if dataset_id:
            query = """
            SELECT 
                tm.id, tm.dataset_id, tm.problem_type, tm.target_variable,
                tm.feature_variables, tm.model_type, tm.model_params_json,
                tm.metrics_json, tm.training_duration, tm.created_at,
                d.name as dataset_name
            FROM training_metadata tm
            LEFT JOIN datasets d ON tm.dataset_id = d.id
            WHERE tm.dataset_id = :dataset_id
            ORDER BY tm.created_at DESC
            FETCH FIRST :limit ROWS ONLY
            """
            params = {'dataset_id': dataset_id, 'limit': limit}
        else:
            query = """
            SELECT 
                tm.id, tm.dataset_id, tm.problem_type, tm.target_variable,
                tm.feature_variables, tm.model_type, tm.model_params_json,
                tm.metrics_json, tm.training_duration, tm.created_at,
                d.name as dataset_name
            FROM training_metadata tm
            LEFT JOIN datasets d ON tm.dataset_id = d.id
            ORDER BY tm.created_at DESC
            FETCH FIRST :limit ROWS ONLY
            """
            params = {'limit': limit}
        
        results = await self._execute(query, params, fetch_all=True)
        
        # Parse JSON fields
        for result in results:
            if result.get('model_params_json'):
                try:
                    result['model_params'] = json.loads(result['model_params_json'])
                except:
                    result['model_params'] = {}
                del result['model_params_json']
            
            if result.get('metrics_json'):
                try:
                    result['metrics'] = json.loads(result['metrics_json'])
                except:
                    result['metrics'] = {}
                del result['metrics_json']
            
            # Convert created_at to string if datetime
            if result.get('created_at'):
                result['created_at'] = str(result['created_at'])
        
        return results
    

    async def update_training_metadata_workspace_name(self, dataset_id: str, workspace_name: str):
        """
        Update workspace_name for all training_metadata records of a dataset
        This is called when user saves a workspace to associate training history with the workspace
        """
        query = """
        UPDATE training_metadata 
        SET workspace_name = :workspace_name 
        WHERE dataset_id = :dataset_id
        """
        params = {
            'workspace_name': workspace_name,
            'dataset_id': dataset_id
        }
        
        # Execute update without fetch - use executor for async
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._update_training_metadata_workspace_name_sync,
            query,
            params,
            dataset_id,
            workspace_name
        )

    def _update_training_metadata_workspace_name_sync(self, query: str, params: Dict, dataset_id: str, workspace_name: str):
        """Execute update training metadata workspace name synchronously"""
        conn = self.pool.acquire()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows_updated = cursor.rowcount
            conn.commit()
            logger.info(f"✅ Updated {rows_updated} training metadata records for dataset {dataset_id} with workspace_name: {workspace_name}")
            return rows_updated
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to update training metadata workspace_name: {e}")
            raise
        finally:
            self.pool.release(conn)
    async def delete_training_metadata_by_workspace(self, workspace_name: str, dataset_id: Optional[str] = None):
        """
        Delete all training metadata records for a specific workspace
        Optionally filter by dataset_id as well
        """
        query_parts = ["DELETE FROM training_metadata WHERE workspace_name = :workspace_name"]
        params = {'workspace_name': workspace_name}
        
        if dataset_id:
            query_parts.append("AND dataset_id = :dataset_id")
            params['dataset_id'] = dataset_id
        
        query = " ".join(query_parts)
        
        # Execute delete using executor pattern
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._delete_training_metadata_sync,
            query,
            params,
            workspace_name
        )
    
    def _delete_training_metadata_sync(self, query: str, params: Dict, workspace_name: str):
        """Execute delete training metadata synchronously"""
        conn = self.pool.acquire()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            deleted_count = cursor.rowcount
            conn.commit()
            logger.info(f"✅ Deleted {deleted_count} training metadata records for workspace: {workspace_name}")
            return {'deleted_count': deleted_count}
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to delete training metadata: {e}")
            raise
        finally:
            self.pool.release(conn)

        logger.info(f"Updated training metadata for dataset {dataset_id} with workspace_name: {workspace_name}")
        return result

    async def get_training_stats(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get training statistics for a dataset
        
        Args:
            dataset_id: Dataset ID
        
        Returns:
            Training statistics
        """
        query = """
        SELECT 
            COUNT(*) as total_trainings,
            COUNT(DISTINCT model_type) as unique_models,
            MAX(created_at) as last_training,
            MIN(created_at) as first_training
        FROM training_metadata
        WHERE dataset_id = :dataset_id
        """
        
        result = await self._execute(query, {'dataset_id': dataset_id}, fetch_one=True)
        
        return {
            'total_trainings': result.get('total_trainings', 0) if result else 0,
            'unique_models': result.get('unique_models', 0) if result else 0,
            'last_training': str(result.get('last_training')) if result and result.get('last_training') else None,
            'first_training': str(result.get('first_training')) if result and result.get('first_training') else None
        }
    
    async def delete_training_metadata(self, metadata_id: str) -> bool:
        """Delete training metadata by ID"""
        query = "DELETE FROM training_metadata WHERE id = :id"
        rows_affected = await self._execute(query, {'id': metadata_id})
        return rows_affected > 0
    
    async def get_best_model_for_dataset(self, dataset_id: str, problem_type: str) -> Optional[Dict[str, Any]]:
        """
        Get the best performing model for a dataset based on problem type
        
        Args:
            dataset_id: Dataset ID
            problem_type: 'regression' or 'classification'
        
        Returns:
            Best model metadata or None
        """
        import json
        
        # For regression, best model has highest R2
        # For classification, best model has highest accuracy
        if problem_type == 'regression':
            query = """
            SELECT 
                tm.id, tm.dataset_id, tm.model_type, tm.metrics_json,
                tm.training_duration, tm.created_at
            FROM training_metadata tm
            WHERE tm.dataset_id = :dataset_id 
              AND tm.problem_type = :problem_type
            ORDER BY 
                CAST(JSON_VALUE(tm.metrics_json, '$.r2_score') AS NUMBER) DESC NULLS LAST
            FETCH FIRST 1 ROW ONLY
            """
        else:  # classification
            query = """
            SELECT 
                tm.id, tm.dataset_id, tm.model_type, tm.metrics_json,
                tm.training_duration, tm.created_at
            FROM training_metadata tm
            WHERE tm.dataset_id = :dataset_id 
              AND tm.problem_type = :problem_type
            ORDER BY 
                CAST(JSON_VALUE(tm.metrics_json, '$.accuracy') AS NUMBER) DESC NULLS LAST
            FETCH FIRST 1 ROW ONLY
            """
        
        result = await self._execute(
            query, 
            {'dataset_id': dataset_id, 'problem_type': problem_type}, 
            fetch_one=True
        )
        
        if result and result.get('metrics_json'):
            try:
                result['metrics'] = json.loads(result['metrics_json'])
                del result['metrics_json']
            except:
                result['metrics'] = {}
        
        return result


    # ==================== Workspace Operations ====================
    
    async def create_workspace(self, workspace: Dict[str, Any]) -> str:
        """Create a new workspace"""
        query = """
            INSERT INTO WORKSPACES (ID, NAME, DESCRIPTION, TAGS, CREATED_AT, UPDATED_AT, DATASET_COUNT, TRAINING_COUNT)
            VALUES (:id, :name, :description, :tags, SYSTIMESTAMP, SYSTIMESTAMP, 0, 0)
        """
        tags_json = json.dumps(workspace.get('tags', []))
        await self._execute(query, {
            'id': workspace['id'],
            'name': workspace['name'],
            'description': workspace.get('description', ''),
            'tags': tags_json
        })
        logger.info(f"✅ Created workspace: {workspace['id']}")
        return workspace['id']
    
    async def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace by ID"""
        query = "SELECT * FROM WORKSPACES WHERE ID = :id"
        result = await self._execute(query, {'id': workspace_id}, fetch_one=True)
        if result and result.get('TAGS'):
            try:
                result['tags'] = json.loads(result['TAGS'])
                del result['TAGS']
            except:
                result['tags'] = []
        return result
    
    async def get_workspaces(self) -> List[Dict[str, Any]]:
        """Get all workspaces"""
        query = "SELECT * FROM WORKSPACES ORDER BY CREATED_AT DESC"
        results = await self._execute(query, {})
        for result in results:
            if result.get('TAGS'):
                try:
                    result['tags'] = json.loads(result['TAGS'])
                    del result['TAGS']
                except:
                    result['tags'] = []
        return results
    
    async def get_workspace_datasets(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all datasets in a workspace"""
        query = "SELECT * FROM DATASETS WHERE WORKSPACE_ID = :workspace_id ORDER BY CREATED_AT DESC"
        return await self._execute(query, {'workspace_id': workspace_id})
    
    async def get_workspace_training_history(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get training history for workspace"""
        query = "SELECT * FROM TRAINING_METADATA WHERE WORKSPACE_ID = :workspace_id ORDER BY TIMESTAMP DESC"
        return await self._execute(query, {'workspace_id': workspace_id})
    
    async def increment_workspace_dataset_count(self, workspace_id: str) -> bool:
        """Increment dataset count for workspace"""
        query = """
            UPDATE WORKSPACES 
            SET DATASET_COUNT = DATASET_COUNT + 1, UPDATED_AT = SYSTIMESTAMP
            WHERE ID = :workspace_id
        """
        await self._execute(query, {'workspace_id': workspace_id})
        return True
    
    async def delete_workspace(self, workspace_id: str) -> bool:
        """Delete workspace"""
        query = "DELETE FROM WORKSPACES WHERE ID = :workspace_id"
        await self._execute(query, {'workspace_id': workspace_id})
        logger.info(f"✅ Deleted workspace: {workspace_id}")
        return True

