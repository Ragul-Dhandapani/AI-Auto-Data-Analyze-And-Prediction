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
import logging

from app.models.pydantic_models import DataSourceConfig, DataSourceTest
from app.database.db_helper import get_db
from app.database.connections import (
    test_oracle_connection, test_postgresql_connection, test_mysql_connection,
    test_sqlserver_connection, get_oracle_tables, get_postgresql_tables,
    get_mysql_tables, get_sqlserver_tables, load_table_data, parse_connection_string
)
from app.services.data_service import generate_data_profile

router = APIRouter(prefix="/datasource", tags=["datasource"])
logger = logging.getLogger(__name__)


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
        # Show up to 1000 records for preview (balance between completeness and performance)
        preview_df = df.head(1000).copy()  # First 1000 auto-cleaned records
        
        # CRITICAL: Clean all non-JSON-serializable values
        # Replace inf/-inf with None first
        preview_df = preview_df.replace([float('inf'), float('-inf')], None)
        # Replace NaN with None
        preview_df = preview_df.where(pd.notna(preview_df), None)
        
        # Convert to dict and ensure all values are JSON-serializable
        data_preview = preview_df.to_dict('records')
        
        # Double-check: clean any remaining NaN/inf values
        import math
        for row in data_preview:
            for key, value in row.items():
                if isinstance(value, float):
                    if math.isnan(value) or math.isinf(value):
                        row[key] = None
        
        # Check for duplicate dataset names and make unique
        db_adapter = get_db()
        existing_datasets = await db_adapter.list_datasets()
        existing_names = [ds.get('name') for ds in existing_datasets]
        
        unique_filename = filename
        if unique_filename in existing_names:
            # Append number to make unique
            base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
            extension = '.' + filename.rsplit('.', 1)[1] if '.' in filename else ''
            counter = 1
            while unique_filename in existing_names:
                unique_filename = f"{base_name} ({counter}){extension}"
                counter += 1
            logger.info(f"Duplicate dataset name detected. Renamed '{filename}' to '{unique_filename}'")
        
        dataset_doc = {
            "id": dataset_id,
            "name": unique_filename,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "data_preview": data_preview,  # First 10 rows as preview (fully cleaned)
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "file_size": len(contents),
            "source_type": "file_upload"
        }
        
        file_size = len(contents)
        
        # Check if we're using Oracle adapter (already retrieved above)
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
            "storage_type": dataset_doc.get("storage_type"),
            "data_preview": dataset_doc.get("data_preview", [])  # Include preview (already JSON-serialized)
        }
        
        return {"message": "File uploaded successfully", "dataset": response_doc}
        
    except Exception as e:
        raise HTTPException(500, f"Error uploading file: {str(e)}")


@router.post("/parse-connection-string")
async def parse_connection_string_endpoint(
    source_type: str = Form(...),
    connection_string: str = Form(...)
):
    """Parse database connection string into config object"""
    try:
        config = parse_connection_string(source_type, connection_string)
        return {"success": True, "config": config}
    except Exception as e:
        logger.error(f"Failed to parse connection string: {str(e)}")
        return {"success": False, "message": str(e)}


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


async def _get_tables_impl(request: DataSourceConfig):
    """Internal implementation for getting tables/collections from database"""
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


@router.post("/list-tables")
async def list_tables(request: DataSourceConfig):
    """Get list of tables/collections from database (primary endpoint)"""
    try:
        return await _get_tables_impl(request)
    except Exception as e:
        logger.error(f"Error getting tables: {str(e)}")
        raise HTTPException(500, f"Error getting tables: {str(e)}")


@router.post("/get-tables")
async def get_tables(request: DataSourceConfig):
    """Get list of tables/collections from database (backward compatibility)"""
    try:
        return await _get_tables_impl(request)
    except Exception as e:
        logger.error(f"Error getting tables: {str(e)}")
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



@router.post("/suggest-features")
async def suggest_features(request: dict):
    """
    AI-powered feature suggestion for predictive analysis
    
    Request format:
    {
        "dataset_id": "string",
        "columns": ["col1", "col2", ...],
        "problem_type": "regression" | "classification" (optional)
    }
    """
    try:
        dataset_id = request.get("dataset_id")
        columns = request.get("columns", [])
        problem_type = request.get("problem_type")
        
        if not dataset_id or not columns:
            raise HTTPException(400, "Missing required parameters: dataset_id and columns")
        
        # Simple heuristic-based feature suggestions
        # Can be enhanced with AI in the future
        
        numeric_cols = []
        categorical_cols = []
        datetime_cols = []
        
        # Load dataset to analyze column types
        try:
            db_adapter = get_db()
            dataset = await db_adapter.get_dataset(dataset_id)
            
            if not dataset:
                raise HTTPException(404, "Dataset not found")
            
            # Load data to infer types
            import numpy as np
            from app.routes.analysis import load_dataframe
            
            df = await load_dataframe(dataset_id)
            
            for col in columns:
                if col in df.columns:
                    dtype = df[col].dtype
                    
                    if pd.api.types.is_numeric_dtype(dtype):
                        numeric_cols.append(col)
                    elif pd.api.types.is_datetime64_any_dtype(dtype):
                        datetime_cols.append(col)
                    else:
                        # Check if it's low cardinality (likely categorical)
                        unique_ratio = df[col].nunique() / len(df)
                        if unique_ratio < 0.05:  # Less than 5% unique values
                            categorical_cols.append(col)
                        else:
                            categorical_cols.append(col)
            
            # Generate suggestions based on problem type
            suggestions = {
                "recommended_target": None,
                "recommended_features": [],
                "feature_groups": {
                    "numeric": numeric_cols,
                    "categorical": categorical_cols,
                    "datetime": datetime_cols
                },
                "suggestions": []
            }
            
            # Suggest target based on problem type
            if problem_type == "classification":
                # Prefer categorical columns with reasonable cardinality
                categorical_targets = [c for c in categorical_cols if 2 <= df[c].nunique() <= 20]
                if categorical_targets:
                    suggestions["recommended_target"] = categorical_targets[0]
                    suggestions["suggestions"].append(
                        f"Recommended target: '{categorical_targets[0]}' (categorical with {df[categorical_targets[0]].nunique()} classes)"
                    )
            elif problem_type == "regression":
                # Prefer numeric columns
                if numeric_cols:
                    suggestions["recommended_target"] = numeric_cols[-1]
                    suggestions["suggestions"].append(
                        f"Recommended target: '{numeric_cols[-1]}' (numeric)"
                    )
            
            # Suggest features (all columns except target)
            if suggestions["recommended_target"]:
                suggestions["recommended_features"] = [
                    c for c in columns if c != suggestions["recommended_target"]
                ]
            else:
                suggestions["recommended_features"] = columns
            
            # Add general suggestions
            if datetime_cols:
                suggestions["suggestions"].append(
                    f"Consider extracting features from datetime columns: {', '.join(datetime_cols)}"
                )
            
            if len(categorical_cols) > 0:
                suggestions["suggestions"].append(
                    f"Categorical columns may need encoding: {', '.join(categorical_cols[:3])}"
                )
            
            return {
                "success": True,
                "suggestions": suggestions
            }
            
        except Exception as e:
            # Fallback to simple type-based suggestions without loading data
            return {
                "success": True,
                "suggestions": {
                    "recommended_target": columns[-1] if columns else None,
                    "recommended_features": columns[:-1] if len(columns) > 1 else [],
                    "feature_groups": {
                        "numeric": [],
                        "categorical": [],
                        "datetime": []
                    },
                    "suggestions": [
                        "Unable to analyze column types. Please select target and features manually."
                    ]
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error suggesting features: {str(e)}")

