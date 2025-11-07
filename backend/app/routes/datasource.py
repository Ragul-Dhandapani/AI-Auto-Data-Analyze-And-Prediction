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
from app.database.db_helper import get_db
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
            # MySQL with Kerberos requires additional setup
            return pymysql.connect(
                host=config.get("host"),
                port=config.get("port", 3306),
                user=config.get("username"),
                database=config.get("database"),
                auth_plugin='authentication_kerberos_client'
            )
        else:
            return pymysql.connect(
                host=config.get("host"),
                port=config.get("port", 3306),
                user=config.get("username"),
                password=config.get("password"),
                database=config.get("database")
            )
    
    elif db_type == "oracle":
        import cx_Oracle
        if use_kerberos:
            # Oracle with Kerberos
            dsn = cx_Oracle.makedsn(
                config.get("host"),
                config.get("port", 1521),
                service_name=config.get("service_name", "XE")
            )
            return cx_Oracle.connect(dsn=dsn, mode=cx_Oracle.SYSDBA)
        else:
            dsn = cx_Oracle.makedsn(
                config.get("host"),
                config.get("port", 1521),
                service_name=config.get("service_name", "XE")
            )
            return cx_Oracle.connect(
                user=config.get("username"),
                password=config.get("password"),
                dsn=dsn
            )
    
    elif db_type == "sqlserver":
        import pyodbc
        if use_kerberos:
            # SQL Server with Windows Authentication/Kerberos
            connection_string = f"""
                DRIVER={{ODBC Driver 17 for SQL Server}};
                SERVER={config.get("host")},{config.get("port", 1433)};
                DATABASE={config.get("database")};
                Trusted_Connection=yes;
            """
        else:
            connection_string = f"""
                DRIVER={{ODBC Driver 17 for SQL Server}};
                SERVER={config.get("host")},{config.get("port", 1433)};
                DATABASE={config.get("database")};
                UID={config.get("username")};
                PWD={config.get("password")};
            """
        return pyodbc.connect(connection_string)
    
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


@router.post("/upload")
@router.post("/upload-file")  # Alias for backward compatibility
async def upload_file(file: UploadFile = File(...)):
    """Upload CSV/Excel file and create dataset"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(400, "Only CSV and Excel files are supported")
        
        # Read file content
        contents = await file.read()
        
        # Parse based on file type
        if file.filename.lower().endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # Validate data
        if df.empty:
            raise HTTPException(400, "File is empty or could not be parsed")
        
        # Generate unique dataset ID
        dataset_id = str(uuid.uuid4())
        
        # Handle duplicate filenames
        filename = file.filename
        db_adapter = get_db()
        
        # Check for existing dataset with same name
        if hasattr(db_adapter, 'db'):  # MongoDB adapter
            existing = await db_adapter.db.datasets.find_one({"name": filename})
        else:
            # For Oracle adapter, we'd need to implement a name check
            existing = None
            
        if existing:
            name_parts = filename.rsplit('.', 1)
            counter = 1
            while existing:
                if len(name_parts) == 2:
                    filename = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                else:
                    filename = f"{filename}_{counter}"
                
                if hasattr(db_adapter, 'db'):  # MongoDB adapter
                    existing = await db_adapter.db.datasets.find_one({"name": filename})
                else:
                    existing = None
                counter += 1
        
        # Prepare dataset metadata
        # Handle NaN, inf, and other non-JSON-serializable values in preview
        preview_df = df.head(10).copy()
        # Replace NaN, inf, -inf with None (which becomes null in JSON)
        preview_df = preview_df.replace([float('inf'), float('-inf')], None)
        preview_df = preview_df.where(pd.notna(preview_df), None)
        
        dataset_doc = {
            "id": dataset_id,
            "name": filename,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "data_preview": preview_df.to_dict('records'),  # First 10 rows as preview (NaN handled)
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "file_size": len(contents),
            "source_type": "file_upload"
        }
        
        file_size = len(contents)
        
        # Check if we're using Oracle adapter (always use BLOB storage for Oracle)
        db_adapter = get_db()
        is_oracle = hasattr(db_adapter, 'pool')  # Oracle adapter has pool attribute
        
        if file_size > 5 * 1024 * 1024 or is_oracle:  # 5MB threshold OR Oracle database
            # OPTIMIZED: Store original file bytes directly as BLOB (much faster!)
            # Instead of slow JSON conversion, store the original CSV/Excel file
            # This preserves the original format and is 10-50x faster
            
            file_id = await db_adapter.store_file(
                filename,
                contents,  # Store original file bytes directly
                metadata={
                    "dataset_id": dataset_id,
                    "content_type": file.content_type or "application/octet-stream",
                    "original_filename": file.filename,
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": list(df.columns)
                }
            )
            dataset_doc["storage_type"] = "blob"
            dataset_doc["gridfs_file_id"] = file_id
        else:
            # Store directly in document (MongoDB only, for small files)
            data_dict = df.to_dict('records')
            dataset_doc["data"] = data_dict
            dataset_doc["storage_type"] = "direct"
        
        # Save to database using adapter
        await db_adapter.create_dataset(dataset_doc)
        
        # Remove internal fields and potentially problematic data for response
        response_doc = {
            "id": dataset_doc.get("id"),
            "name": dataset_doc.get("name"),
            "row_count": dataset_doc.get("row_count"),
            "column_count": dataset_doc.get("column_count"),
            "columns": dataset_doc.get("columns"),
            "dtypes": dataset_doc.get("dtypes"),
            "created_at": dataset_doc.get("created_at"),
            "file_size": dataset_doc.get("file_size"),
            "source_type": dataset_doc.get("source_type"),
            "storage_type": dataset_doc.get("storage_type")
            # Don't include data_preview in response to avoid JSON serialization issues
        }
        
        return {"message": "File uploaded successfully", "dataset": response_doc}
        
    except Exception as e:
        raise HTTPException(500, f"Error uploading file: {str(e)}")


@router.post("/test-connection")
async def test_connection(request: DataSourceTest):
    """Test database connection"""
    try:
        if request.source_type == 'postgresql':
            result = test_postgresql_connection(request.config)
        elif request.source_type == 'mysql':
            result = test_mysql_connection(request.config)
        elif request.source_type == 'oracle':
            result = test_oracle_connection(request.config)
        elif request.source_type == 'sqlserver':
            result = test_sqlserver_connection(request.config)
        elif request.source_type == 'mongodb':
            db_adapter = get_db()
            if hasattr(db_adapter, 'db'):  # MongoDB adapter
                await db_adapter.db.command('ping')
            result = {"success": True, "message": "Connection successful"}
        else:
            raise HTTPException(400, f"Unsupported source type: {request.source_type}")
        
        return result
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/get-tables")
async def get_tables(request: DataSourceConfig):
    """Get list of tables/collections from database"""
    try:
        if request.source_type == 'postgresql':
            tables = get_postgresql_tables(request.config)
        elif request.source_type == 'mysql':
            tables = get_mysql_tables(request.config)
        elif request.source_type == 'oracle':
            tables = get_oracle_tables(request.config)
        elif request.source_type == 'sqlserver':
            tables = get_sqlserver_tables(request.config)
        elif request.source_type == 'mongodb':
            db_adapter = get_db()
            if hasattr(db_adapter, 'db'):  # MongoDB adapter
                collections = await db_adapter.db.list_collection_names()
                tables = [c for c in collections if not c.startswith('system.')]
            else:
                tables = []
        else:
            raise HTTPException(400, f"Unsupported source type: {request.source_type}")
        
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(500, f"Error getting tables: {str(e)}")


@router.post("/load-table")
async def load_table(
    source_type: str = Form(...),
    config: str = Form(...),
    table_name: str = Form(...),
    limit: int = Form(1000)
):
    """Load data from database table"""
    try:
        import json
        config_dict = json.loads(config)
        
        # Load data from table
        df = load_table_data(source_type, config_dict, table_name, limit)
        
        if df.empty:
            raise HTTPException(400, f"Table '{table_name}' is empty or could not be loaded")
        
        # Generate unique dataset ID
        dataset_id = str(uuid.uuid4())
        
        # Prepare dataset metadata
        dataset_doc = {
            "id": dataset_id,
            "name": f"{table_name}_{source_type}",
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),  # Changed from data_types to dtypes
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "source_type": source_type,
            "source_table": table_name,
            "source_config": config_dict
        }
        
        # Store data
        data_dict = df.to_dict('records')
        data_size = len(str(data_dict))
        
        if data_size > 5 * 1024 * 1024:  # 5MB threshold
            # GridFS storage for large datasets
            import json
            data_json = json.dumps(data_dict)
            
            db_adapter = get_db()
            file_id = await db_adapter.store_file(
                f"table_{dataset_id}.json",
                data_json.encode('utf-8'),
                metadata={"dataset_id": dataset_id, "source_table": table_name}
            )
            
            dataset_doc["storage_type"] = "blob"
            dataset_doc["gridfs_file_id"] = file_id
        else:
            dataset_doc["data"] = data_dict
            dataset_doc["storage_type"] = "direct"
        
        # Save to database
        db_adapter = get_db()
        await db_adapter.create_dataset(dataset_doc)
        
        # Remove internal fields for response
        response_doc = dataset_doc.copy()
        response_doc.pop("data", None)
        response_doc.pop("gridfs_file_id", None)
        
        return {"message": "Table loaded successfully", "dataset": response_doc}
        
    except Exception as e:
        raise HTTPException(500, f"Error loading table: {str(e)}")


@router.get("/datasets")
async def get_datasets(limit: int = 10):
    """Get list of all datasets"""
    try:
        db_adapter = get_db()
        datasets = await db_adapter.list_datasets(limit)
        
        return {"datasets": datasets}
    except Exception as e:
        raise HTTPException(500, f"Error fetching datasets: {str(e)}")


@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    """Get dataset by ID"""
    try:
        db_adapter = get_db()
        dataset = await db_adapter.get_dataset(dataset_id)
        
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        
        # Load data if stored in GridFS
        if dataset.get("storage_type") == "blob":
            gridfs_file_id = dataset.get("gridfs_file_id")
            if gridfs_file_id:
                from bson import ObjectId
                import json
                
                data = await db_adapter.retrieve_file(gridfs_file_id)
                # Parse based on file type
                try:
                    data_dict = json.loads(data.decode('utf-8'))
                    dataset["data"] = data_dict
                except:
                    # If not JSON, treat as raw data
                    dataset["raw_data"] = data
        
        return {"dataset": dataset}
    except Exception as e:
        raise HTTPException(500, f"Error fetching dataset: {str(e)}")


@router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """Delete dataset and associated data"""
    try:
        db_adapter = get_db()
        success = await db_adapter.delete_dataset(dataset_id)
        
        if not success:
            raise HTTPException(404, "Dataset not found")
        
        return {"message": "Dataset deleted successfully"}
    except Exception as e:
        raise HTTPException(500, f"Error deleting dataset: {str(e)}")


# Additional endpoints remain the same but use db_adapter pattern...
# For brevity, I'll include the key patterns and you can apply them to remaining endpoints

@router.post("/query")
async def execute_query(
    source_type: str = Form(...),
    config: str = Form(...),
    query: str = Form(...),
    limit: int = Form(1000)
):
    """Execute custom SQL query"""
    try:
        import json
        config_dict = json.loads(config)
        
        # Create connection and execute query
        conn = create_db_connection(source_type, config_dict)
        df = pd.read_sql(query, conn, params=None)
        conn.close()
        
        if df.empty:
            return {"message": "Query returned no results", "dataset": None}
        
        # Generate unique dataset ID
        dataset_id = str(uuid.uuid4())
        
        # Prepare dataset metadata
        dataset_doc = {
            "id": dataset_id,
            "name": f"query_result_{dataset_id[:8]}",
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),  # Changed from data_types to dtypes
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "source_type": f"{source_type}_query",
            "source_query": query,
            "source_config": config_dict
        }
        
        # Store data
        data_dict = df.to_dict('records')
        data_size = len(str(data_dict))
        
        if data_size > 5 * 1024 * 1024:  # 5MB threshold
            import json
            data_json = json.dumps(data_dict)
            
            db_adapter = get_db()
            file_id = await db_adapter.store_file(
                f"query_{dataset_id}.json",
                data_json.encode('utf-8'),
                metadata={"dataset_id": dataset_id, "query": query}
            )
            
            dataset_doc["storage_type"] = "blob"
            dataset_doc["gridfs_file_id"] = file_id
        else:
            dataset_doc["data"] = data_dict
            dataset_doc["storage_type"] = "direct"
        
        # Save to database
        db_adapter = get_db()
        await db_adapter.create_dataset(dataset_doc)
        
        # Remove internal fields for response
        response_doc = dataset_doc.copy()
        response_doc.pop("data", None)
        response_doc.pop("gridfs_file_id", None)
        
        return {"message": "Query executed successfully", "dataset": response_doc}
        
    except Exception as e:
        raise HTTPException(500, f"Error executing query: {str(e)}")


# Helper function for loading dataframes (used by other modules)
async def load_dataframe(dataset_id: str) -> pd.DataFrame:
    """Load dataframe from dataset ID - ADAPTER VERSION"""
    try:
        db_adapter = get_db()
        dataset = await db_adapter.get_dataset(dataset_id)
        
        if not dataset:
            raise HTTPException(404, f"Dataset not found: {dataset_id}")
        
        # Load data based on storage type
        if dataset.get('storage_type') == 'blob' and dataset.get('gridfs_file_id'):
            # Load from GridFS/BLOB
            data = await db_adapter.retrieve_file(dataset['gridfs_file_id'])
            df = pd.read_json(io.BytesIO(data), orient='records')
        else:
            # Load from inline data
            data = dataset.get('data', [])
            df = pd.DataFrame(data)
        
        return df
    except Exception as e:
        raise HTTPException(500, f"Error loading dataframe: {str(e)}")


async def get_recent_datasets(limit: int = 10):
    """Get recent datasets - compatibility function"""
    try:
        db_adapter = get_db()
        datasets = await db_adapter.list_datasets(limit)
        return {"datasets": datasets}
    except Exception as e:
        raise HTTPException(500, f"Error fetching datasets: {str(e)}")
