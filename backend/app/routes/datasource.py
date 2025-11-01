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

from app.models.pydantic_models import DataSourceConfig, DataSourceTest
from app.database.mongodb import db, fs
from app.database.connections import (
    test_oracle_connection, test_postgresql_connection, test_mysql_connection,
    test_sqlserver_connection, get_oracle_tables, get_postgresql_tables,
    get_mysql_tables, get_sqlserver_tables, load_table_data, parse_connection_string
)
from app.services.data_service import generate_data_profile

router = APIRouter(prefix="/datasource", tags=["datasource"])


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
    """Load data from database table"""
    try:
        # Load data from database
        df = load_table_data(request.source_type, request.config, table_name)
        
        # Generate dataset ID
        dataset_id = str(uuid.uuid4())
        
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
            "data": df.to_dict('records'),
            "data_preview": df.head(10).to_dict('records'),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Save to database
        await db.datasets.insert_one(dataset_doc)
        dataset_doc.pop("_id", None)
        
        return dataset_doc
        
    except Exception as e:
        raise HTTPException(500, f"Failed to load table: {str(e)}")


@router.get("/recent")
async def get_recent_datasets(limit: int = 10):
    """Get recent datasets"""
    try:
        cursor = db.datasets.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
        datasets = await cursor.to_list(length=limit)
        return {"datasets": datasets}
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
        
        # Execute query based on database type
        if db_type == "postgresql":
            import psycopg2
            conn = psycopg2.connect(
                host=config.get("host"),
                port=config.get("port", 5432),
                user=config.get("username"),
                password=config.get("password"),
                database=config.get("database")
            )
            df = pd.read_sql_query(query, conn)
            conn.close()
            
        elif db_type == "mysql":
            import pymysql
            conn = pymysql.connect(
                host=config.get("host"),
                port=config.get("port", 3306),
                user=config.get("username"),
                password=config.get("password"),
                database=config.get("database")
            )
            df = pd.read_sql_query(query, conn)
            conn.close()
            
        elif db_type == "oracle":
            import cx_Oracle
            dsn = cx_Oracle.makedsn(
                config.get("host"),
                config.get("port", 1521),
                service_name=config.get("service_name")
            )
            conn = cx_Oracle.connect(
                user=config.get("username"),
                password=config.get("password"),
                dsn=dsn
            )
            df = pd.read_sql_query(query, conn)
            conn.close()
            
        elif db_type == "sqlserver":
            import pyodbc
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={config.get('host')},{config.get('port', 1433)};"
                f"DATABASE={config.get('database')};"
                f"UID={config.get('username')};"
                f"PWD={config.get('password')}"
            )
            conn = pyodbc.connect(conn_str)
            df = pd.read_sql_query(query, conn)
            conn.close()
            
        elif db_type == "mongodb":
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
            raise HTTPException(400, f"Unsupported database type: {db_type}")
        
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

