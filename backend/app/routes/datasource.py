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
