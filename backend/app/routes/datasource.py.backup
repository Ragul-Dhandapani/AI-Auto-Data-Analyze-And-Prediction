"""
Data Source Routes
Handles file upload, database connections, and data loading
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List
import pandas as pd
import uuid
from datetime import datetime, timezone
import io
import os
import psycopg2
import pymysql

from app.models.pydantic_models import DataSourceConfig, DataSourceTest
from app.database.mongodb import db, fs
from app.database.connections import (
    test_oracle_connection, test_postgresql_connection, test_mysql_connection,
    test_sqlserver_connection, get_oracle_tables, get_postgresql_tables,
    get_mysql_tables, get_sqlserver_tables, load_table_data, parse_connection_string
)
from app.services.data_service import generate_data_profile

router = APIRouter(prefix="/datasource", tags=["datasource"])


def create_db_connection(db_type: str, config: dict):
    """
    Create database connection with Kerberos support
    
    Args:
        db_type: Database type (postgresql, mysql, oracle, sqlserver)
        config: Connection configuration with optional use_kerberos flag
    
    Returns:
        Database connection object
    """
    use_kerberos = config.get('use_kerberos', False)
    
    if db_type == "postgresql":
        import psycopg2
        if use_kerberos:
            return psycopg2.connect(
                host=config.get("host"),
                port=config.get("port", 5432),
                user=config.get("username"),
                database=config.get("database"),
                gssencmode='prefer'  # Use GSSAPI/Kerberos
            )
        else:
            return psycopg2.connect(
                host=config.get("host"),
                port=config.get("port", 5432),
                user=config.get("username"),
                password=config.get("password"),
                database=config.get("database")
            )
    
    elif db_type == "mysql":
        import pymysql
        if use_kerberos:
            return pymysql.connect(
                host=config.get("host"),
                port=int(config.get("port", 3306)),
                user=config.get("username"),
                database=config.get("database"),
                auth_plugin='authentication_kerberos_client'  # Kerberos plugin
            )
        else:
            return pymysql.connect(
                host=config.get("host"),
                port=int(config.get("port", 3306)),
                user=config.get("username"),
                password=config.get("password"),
                database=config.get("database")
            )
    
    elif db_type == "oracle":
        import cx_Oracle
        dsn = cx_Oracle.makedsn(
            config.get("host"),
            config.get("port", 1521),
            service_name=config.get("service_name")
        )
        if use_kerberos:
            # Oracle Kerberos via external authentication
            return cx_Oracle.connect(
                user=config.get("username") + '/',  # External auth format
                dsn=dsn
            )
        else:
            return cx_Oracle.connect(
                user=config.get("username"),
                password=config.get("password"),
                dsn=dsn
            )
    
    elif db_type == "sqlserver":
        import pyodbc
        if use_kerberos:
            # SQL Server with Kerberos/Windows Integrated Authentication
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={config.get('host')},{config.get('port', 1433)};"
                f"DATABASE={config.get('database')};"
                f"Trusted_Connection=yes;"
            )
        else:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={config.get('host')},{config.get('port', 1433)};"
                f"DATABASE={config.get('database')};"
                f"UID={config.get('username')};"
                f"PWD={config.get('password')}"
            )
        return pyodbc.connect(conn_str)
    
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload and preview data file using GridFS for large files"""
    try:
        # Read file content
        contents = await file.read()
        file_size = len(contents)
        
        # Read into DataFrame
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(400, "Unsupported file format. Please upload CSV or Excel files.")
        
        # Generate unique dataset ID
        dataset_id = str(uuid.uuid4())
        
        # Handle duplicate filenames
        filename = file.filename
        existing = await db.datasets.find_one({"name": filename})
        if existing:
            name_parts = filename.rsplit('.', 1)
            counter = 1
            while existing:
                if len(name_parts) == 2:
                    filename = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                else:
                    filename = f"{filename}_{counter}"
                existing = await db.datasets.find_one({"name": filename})
                counter += 1
        
        # Prepare dataset metadata
        dataset_doc = {
            "id": dataset_id,
            "name": filename,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "file_size": file_size,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store based on size
        if file_size > 5 * 1024 * 1024:  # 5MB threshold
            # Store in GridFS
            file_id = await fs.upload_from_stream(
                filename,
                io.BytesIO(contents),
                metadata={"dataset_id": dataset_id, "type": "dataset"}
            )
            dataset_doc["storage_type"] = "gridfs"
            dataset_doc["gridfs_file_id"] = str(file_id)
            dataset_doc["data_preview"] = df.head(10).to_dict('records')
        else:
            # Store directly
            dataset_doc["storage_type"] = "direct"
            dataset_doc["data"] = df.to_dict('records')
            dataset_doc["data_preview"] = df.head(10).to_dict('records')
        
        # Save to database
        await db.datasets.insert_one(dataset_doc)
        
        # Remove _id for response
        dataset_doc.pop("_id", None)
        
        return dataset_doc
        
    except pd.errors.EmptyDataError:
        raise HTTPException(400, "File is empty or invalid")
    except Exception as e:
        raise HTTPException(500, f"Failed to process file: {str(e)}")


@router.post("/test-connection")
async def test_connection(request: DataSourceTest):
    """Test database connection"""
    try:
        if request.source_type == 'oracle':
            result = test_oracle_connection(request.config)
        elif request.source_type == 'postgresql':
            result = test_postgresql_connection(request.config)
        elif request.source_type == 'mysql':
            result = test_mysql_connection(request.config)
        elif request.source_type == 'sqlserver':
            result = test_sqlserver_connection(request.config)
        elif request.source_type == 'mongodb':
            await db.command('ping')
            result = {"success": True, "message": "Connection successful"}
        else:
            result = {"success": False, "message": "Unsupported database type"}
        
        return result
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/list-tables")
async def list_tables(request: DataSourceTest):
    """List available tables/collections"""
    try:
        if request.source_type == 'oracle':
            tables = get_oracle_tables(request.config)
        elif request.source_type == 'postgresql':
            tables = get_postgresql_tables(request.config)
        elif request.source_type == 'mysql':
            tables = get_mysql_tables(request.config)
        elif request.source_type == 'sqlserver':
            tables = get_sqlserver_tables(request.config)
        elif request.source_type == 'mongodb':
            collections = await db.list_collection_names()
            tables = [c for c in collections if not c.startswith('system.')]
        else:
            raise HTTPException(400, "Unsupported database type")
        
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(500, f"Failed to list tables: {str(e)}")


@router.post("/parse-connection-string")
async def parse_conn_string(source_type: str = Form(...), connection_string: str = Form(...)):
    """Parse connection string into config parameters"""
    try:
        config = parse_connection_string(source_type, connection_string)
        return {"success": True, "config": config}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/load-table")
async def load_table_endpoint(request: DataSourceTest, table_name: str):
    """Load data from database table with GridFS support for large datasets"""
    try:
        # Load data from database
        df = load_table_data(request.source_type, request.config, table_name)
        
        if df.empty:
            raise HTTPException(400, f"Table '{table_name}' is empty or does not exist")
        
        # Convert datetime columns to ISO format strings (for JSON serialization)
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)
        
        # Generate dataset ID
        dataset_id = str(uuid.uuid4())
        
        # Convert DataFrame to records
        data_dict = df.to_dict('records')
        
        # Check data size
        import json
        try:
            data_json = json.dumps(data_dict, default=str)  # Use default=str for non-serializable types
            data_size_mb = len(data_json.encode('utf-8')) / (1024 * 1024)
        except Exception as e:
            # If JSON serialization fails, treat as large dataset
            print(f"JSON serialization warning: {e}")
            data_size_mb = 15  # Force GridFS
        
        # Prepare dataset document
        dataset_doc = {
            "id": dataset_id,
            "name": f"{request.source_type}_{table_name}",
            "source_type": "database",
            "db_type": request.source_type,
            "table_name": table_name,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "data_preview": df.head(10).to_dict('records'),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Storage decision based on size
        if data_size_mb < 10:
            # Direct storage for small datasets
            dataset_doc["data"] = data_dict
            dataset_doc["storage_type"] = "direct"
            dataset_doc["gridfs_file_id"] = None
        else:
            # GridFS storage for large datasets
            file_id = await fs.upload_from_stream(
                f"table_{dataset_id}.json",
                data_json.encode('utf-8'),
                metadata={"dataset_id": dataset_id, "type": "table_data"}
            )
            dataset_doc["data"] = None
            dataset_doc["storage_type"] = "gridfs"
            dataset_doc["gridfs_file_id"] = str(file_id)
        
        # Save to database
        await db.datasets.insert_one(dataset_doc)
        dataset_doc.pop("_id", None)
        
        return {
            **dataset_doc,
            "message": f"Table loaded successfully ({data_size_mb:.2f} MB)",
            "storage_type": dataset_doc["storage_type"]
        }
        
    except HTTPException:
        raise
    except psycopg2.Error as e:
        raise HTTPException(500, f"PostgreSQL error: {str(e)}")
    except pymysql.Error as e:
        raise HTTPException(500, f"MySQL error: {str(e)}")
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error loading table: {error_detail}")
        raise HTTPException(500, f"Failed to load table: {str(e)}")



def remove_nested_data_fields(obj):
    """Recursively remove 'data' fields from nested structures to reduce response size"""
    if isinstance(obj, dict):
        # Remove 'data' key if present
        if 'data' in obj:
            del obj['data']
        # Recursively process all values
        for key, value in list(obj.items()):
            obj[key] = remove_nested_data_fields(value)
    elif isinstance(obj, list):
        # Recursively process all items in list
        return [remove_nested_data_fields(item) for item in obj]
    return obj


@router.get("/recent")
async def get_recent_datasets(limit: int = 10):
    """Get recent datasets - returns only metadata, excludes full data array for performance"""
    import json
    import math
    from fastapi.responses import Response
    
    try:
        # Exclude _id and data fields to reduce response size and improve frontend performance
        cursor = db.datasets.find({}, {"_id": 0, "data": 0}).sort("created_at", -1).limit(limit)
        datasets = await cursor.to_list(length=limit)
        
        # Remove any nested 'data' fields from data_preview or other nested structures
        datasets = remove_nested_data_fields(datasets)
        
        # Custom JSON encoder that handles NaN and Infinity
        class NanInfEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, float):
                    if math.isnan(obj) or math.isinf(obj):
                        return None
                return super().default(obj)
        
        # Serialize with custom encoder
        json_str = json.dumps({"datasets": datasets}, cls=NanInfEncoder)
        
        # Return as Response with proper content type
        return Response(content=json_str, media_type="application/json")
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch datasets: {str(e)}")


# Alias for backward compatibility
@router.get("/datasets")
async def get_datasets_alias(limit: int = 10):
    """Backward compatibility endpoint"""
    return await get_recent_datasets(limit)


@router.get("/{dataset_id}")
async def get_dataset(dataset_id: str):
    """Get dataset by ID"""
    try:
        dataset = await db.datasets.find_one({"id": dataset_id}, {"_id": 0})
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        
        # If stored in GridFS, load the data
        if dataset.get("storage_type") == "gridfs":
            from bson import ObjectId
            gridfs_file_id = dataset.get("gridfs_file_id")
            if gridfs_file_id:
                grid_out = await fs.open_download_stream(ObjectId(gridfs_file_id))
                data = await grid_out.read()
                # Parse based on file type
                if dataset["name"].endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(data))
                else:
                    df = pd.read_excel(io.BytesIO(data))
                dataset["data"] = df.to_dict('records')
        
        return dataset
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch dataset: {str(e)}")



@router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """Delete a dataset and its associated workspaces"""
    try:
        # Find dataset
        dataset = await db.datasets.find_one({"id": dataset_id}, {"_id": 0})
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        
        # Delete GridFS file if exists
        if dataset.get("storage_type") == "gridfs":
            from bson import ObjectId
            gridfs_file_id = dataset.get("gridfs_file_id")
            if gridfs_file_id:
                try:
                    await fs.delete(ObjectId(gridfs_file_id))
                except Exception as e:
                    print(f"Warning: Failed to delete GridFS file: {str(e)}")
        
        # Delete all saved workspaces for this dataset
        workspaces_result = await db.saved_states.delete_many({"dataset_id": dataset_id})
        print(f"Deleted {workspaces_result.deleted_count} workspaces for dataset {dataset_id}")
        
        # Delete the dataset itself
        result = await db.datasets.delete_one({"id": dataset_id})
        
        if result.deleted_count == 0:
            raise HTTPException(404, "Dataset not found")
        
        return {
            "success": True,
            "message": "Dataset and associated workspaces deleted successfully",
            "workspaces_deleted": workspaces_result.deleted_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to delete dataset: {str(e)}")


@router.post("/execute-query")
async def execute_custom_query(config: dict):
    """
    Execute custom SQL query and load results for analysis
    Supports complex queries including JOINs, WHERE clauses, etc.
    """
    try:
        db_type = config.get("db_type")
        query = config.get("query", "").strip()
        
        if not query:
            raise HTTPException(400, "Query cannot be empty")
        
        if not db_type:
            raise HTTPException(400, "Database type is required")
        
        # Execute query based on database type using helper function
        if db_type == "mongodb":
            # For MongoDB, query should be a collection name since SQL doesn't apply
            from pymongo import MongoClient
            client = MongoClient(
                host=config.get("host"),
                port=config.get("port", 27017),
                username=config.get("username"),
                password=config.get("password")
            )
            db_mongo = client[config.get("database")]
            collection = db_mongo[query]  # Use query as collection name
            data = list(collection.find().limit(10000))
            if data and '_id' in data[0]:
                for doc in data:
                    doc['_id'] = str(doc['_id'])
            df = pd.DataFrame(data)
            client.close()
        else:
            conn = create_db_connection(db_type, config)
            df = pd.read_sql_query(query, conn)
            conn.close()
        
        if df.empty:
            raise HTTPException(400, "Query returned no results")
        
        # Generate unique dataset ID
        dataset_id = str(uuid.uuid4())
        
        # Prepare dataset name
        query_preview = query[:50] + "..." if len(query) > 50 else query
        dataset_name = f"Query: {query_preview}"
        
        # Convert DataFrame to records
        data_dict = df.to_dict('records')
        
        # Check size for storage decision
        data_size_mb = len(str(data_dict).encode('utf-8')) / (1024 * 1024)
        
        dataset_doc = {
            "id": dataset_id,
            "name": dataset_name,
            "query": query,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "data_preview": data_dict[:10],
            "source_type": "database_query",
            "db_type": db_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Storage decision based on size
        if data_size_mb < 10:
            # Direct storage for small datasets
            dataset_doc["data"] = data_dict
            dataset_doc["storage_type"] = "direct"
            dataset_doc["gridfs_file_id"] = None
        else:
            # GridFS storage for large datasets
            import json
            data_json = json.dumps(data_dict)
            file_id = await fs.upload_from_stream(
                f"query_{dataset_id}.json",
                data_json.encode('utf-8'),
                metadata={"dataset_id": dataset_id, "type": "query_results"}
            )
            dataset_doc["data"] = None
            dataset_doc["storage_type"] = "gridfs"
            dataset_doc["gridfs_file_id"] = str(file_id)
        
        # Save to MongoDB
        await db.datasets.insert_one(dataset_doc)
        
        # Remove MongoDB-specific fields from response
        dataset_doc.pop("_id", None)
        
        return {
            **dataset_doc,
            "message": "Query executed successfully",
            "size_mb": round(data_size_mb, 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to execute query: {str(e)}")



@router.post("/execute-query-preview")
async def execute_query_preview(config: dict):
    """
    Execute custom SQL query and return preview without saving as dataset
    Used to validate query before user names and loads the dataset
    """
    try:
        db_type = config.get("db_type")
        query = config.get("query", "").strip()
        
        if not query:
            raise HTTPException(400, "Query cannot be empty")
        
        if not db_type:
            raise HTTPException(400, "Database type is required")
        
        # Execute query based on database type using helper function
        if db_type == "mongodb":
            from pymongo import MongoClient
            client = MongoClient(
                host=config.get("host"),
                port=config.get("port", 27017),
                username=config.get("username"),
                password=config.get("password"),
                serverSelectionTimeoutMS=10000
            )
            db_mongo = client[config.get("database")]
            collection = db_mongo[query]
            data = list(collection.find().limit(10000))
            if data and '_id' in data[0]:
                for doc in data:
                    doc['_id'] = str(doc['_id'])
            df = pd.DataFrame(data)
            client.close()
        else:
            conn = create_db_connection(db_type, config)
            df = pd.read_sql_query(query, conn)
            conn.close()
        
        if df.empty:
            raise HTTPException(400, "Query returned no results")
        
        # Convert to records for preview
        data_dict = df.to_dict('records')
        
        return {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "data_preview": data_dict[:10],  # Return first 10 rows as preview
            "message": "Query executed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to execute query: {str(e)}")


@router.post("/save-query-dataset")
async def save_query_dataset(config: dict):
    """
    Execute query and save results as a named dataset
    Called after user provides a custom name for the query results
    """
    try:
        db_type = config.get("db_type")
        query = config.get("query", "").strip()
        dataset_name = config.get("dataset_name", "").strip()
        
        if not query:
            raise HTTPException(400, "Query cannot be empty")
        
        if not db_type:
            raise HTTPException(400, "Database type is required")
        
        if not dataset_name:
            raise HTTPException(400, "Dataset name is required")
        
        # Execute query based on database type using helper function
        if db_type == "mongodb":
            from pymongo import MongoClient
            client = MongoClient(
                host=config.get("host"),
                port=config.get("port", 27017),
                username=config.get("username"),
                password=config.get("password"),
                serverSelectionTimeoutMS=10000
            )
            db_mongo = client[config.get("database")]
            collection = db_mongo[query]
            data = list(collection.find().limit(10000))
            if data and '_id' in data[0]:
                for doc in data:
                    doc['_id'] = str(doc['_id'])
            df = pd.DataFrame(data)
            client.close()
        else:
            conn = create_db_connection(db_type, config)
            df = pd.read_sql_query(query, conn)
            conn.close()
        
        if df.empty:
            raise HTTPException(400, "Query returned no results")
        
        # Generate unique dataset ID
        dataset_id = str(uuid.uuid4())
        
        # Use user-provided dataset name
        
        # Convert DataFrame to records
        data_dict = df.to_dict('records')
        
        # Check size for storage decision
        data_size_mb = len(str(data_dict).encode('utf-8')) / (1024 * 1024)
        
        dataset_doc = {
            "id": dataset_id,
            "name": dataset_name,  # User-provided name
            "query": query,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "data_preview": data_dict[:10],
            "source_type": "database_query",
            "db_type": db_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Storage decision based on size
        if data_size_mb < 10:
            # Direct storage for small datasets
            dataset_doc["data"] = data_dict
            dataset_doc["storage_type"] = "direct"
            dataset_doc["gridfs_file_id"] = None
        else:
            # GridFS storage for large datasets
            import json
            data_json = json.dumps(data_dict)
            file_id = await fs.upload_from_stream(
                f"query_{dataset_id}.json",
                data_json.encode('utf-8'),
                metadata={"dataset_id": dataset_id, "type": "query_results"}
            )
            dataset_doc["data"] = None
            dataset_doc["storage_type"] = "gridfs"
            dataset_doc["gridfs_file_id"] = str(file_id)
        
        # Save to MongoDB
        await db.datasets.insert_one(dataset_doc)
        
        # Remove MongoDB-specific fields from response
        dataset_doc.pop("_id", None)
        
        return {
            **dataset_doc,
            "message": f"Dataset '{dataset_name}' saved successfully",
            "size_mb": round(data_size_mb, 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to save dataset: {str(e)}")




@router.post("/suggest-features")
async def suggest_features(request: dict):
    """
    AI-powered feature selection endpoint
    
    Request body:
    {
        "dataset_id": "uuid",
        "target_column": "column_name",
        "top_n": 10  (optional)
    }
    
    Returns suggested features with explanations
    """
    try:
        from app.services.feature_selection_service import suggest_features_ai, detect_variable_types
        
        dataset_id = request.get('dataset_id')
        target_column = request.get('target_column')
        top_n = request.get('top_n', 10)
        
        if not dataset_id or not target_column:
            raise HTTPException(400, "dataset_id and target_column are required")
        
        # Fetch dataset from MongoDB
        dataset = await db.datasets.find_one({"id": dataset_id})
        if not dataset:
            raise HTTPException(404, f"Dataset not found: {dataset_id}")
        
        # Load data
        if dataset.get('storage_type') == 'gridfs' and dataset.get('gridfs_file_id'):
            # Load from GridFS
            file_data = await fs.download_to_stream(dataset['gridfs_file_id'], io.BytesIO())
            file_data.seek(0)
            df = pd.read_json(file_data, orient='records')
        else:
            # Load from direct storage
            df = pd.DataFrame(dataset['data'])
        
        # Validate target column exists
        if target_column not in df.columns:
            raise HTTPException(400, f"Target column '{target_column}' not found in dataset")
        
        # Detect variable types
        var_types = detect_variable_types(df)
        
        # Get AI suggestions
        suggestions = suggest_features_ai(df, target_column, top_n)
        
        return {
            **suggestions,
            'variable_types': var_types,
            'total_columns': len(df.columns),
            'dataset_shape': {'rows': len(df), 'columns': len(df.columns)}
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Feature suggestion failed: {str(e)}")

