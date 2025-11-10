# PROMISE AI Platform - Database Structure

Complete database schema documentation for MongoDB and Oracle.

---

## Table of Contents
1. [Overview](#overview)
2. [MongoDB Schema](#mongodb-schema)
3. [Oracle Schema](#oracle-schema)
4. [Data Types & Constraints](#data-types--constraints)
5. [Indexes](#indexes)
6. [Storage & Limitations](#storage--limitations)
7. [Migration Scripts](#migration-scripts)

---

## Overview

### Database Architecture

PROMISE AI supports **dual database architecture**:
- **MongoDB**: NoSQL document database (flexible schema)
- **Oracle 19c**: Relational database (structured schema)

Both databases store identical data with appropriate type mappings.

### Abstract Adapter Pattern

```python
Database Factory
    ↓
[MongoDB Adapter] ←→ [Oracle Adapter]
    ↓                      ↓
  MongoDB              Oracle RDS
```

Seamless switching between databases via environment variable `DB_TYPE`.

---

## MongoDB Schema

### Collections Overview

| Collection | Purpose | Documents | Index |
|------------|---------|-----------|-------|
| `datasets` | Store dataset metadata and preview data | ~1000s | id, name |
| `training_metadata` | ML model training results | ~10000s | dataset_id, workspace_name |
| `workspace_states` | Saved workspace configurations | ~100s | workspace_name, dataset_id |
| `fs.files` (GridFS) | Large dataset files (>5MB) | ~100s | filename, metadata.dataset_id |
| `fs.chunks` (GridFS) | BLOB chunks for large files | ~1000s | files_id |

---

### Collection: `datasets`

**Purpose**: Store uploaded datasets with metadata and preview data

**Schema**:
```javascript
{
  "_id": ObjectId("..."),  // MongoDB internal ID (not used)
  "id": "550e8400-e29b-41d4-a716-446655440000",  // UUID (Primary Key)
  "name": "application_latency.csv",
  "row_count": 10000,
  "column_count": 12,
  "columns": ["timestamp", "latency_ms", "status", ...],
  "dtypes": {
    "timestamp": "datetime64[ns]",
    "latency_ms": "float64",
    "status": "object"
  },
  "data_preview": [  // First 1000 rows for quick display
    {"timestamp": "2024-01-01 10:00:00", "latency_ms": 234.5, ...},
    ...
  ],
  "storage_type": "blob",  // "blob" or "direct"
  "gridfs_file_id": ObjectId("..."),  // If storage_type=blob
  "data": [...],  // If storage_type=direct (small datasets <5MB)
  "source_type": "file_upload",  // "file_upload" or database type
  "source_table": null,  // If from database
  "source_config": {},  // Database connection details
  "created_at": ISODate("2024-11-09T10:00:00Z"),
  "updated_at": ISODate("2024-11-09T10:00:00Z"),
  "storage_format": "csv"
}
```

**Indexes**:
```javascript
db.datasets.createIndex({ "id": 1 }, { unique: true });
db.datasets.createIndex({ "name": 1 });
db.datasets.createIndex({ "created_at": -1 });
```

**Storage**:
- Small datasets (<5MB): Stored directly in `data` field
- Large datasets (>5MB): Stored in GridFS, referenced by `gridfs_file_id`
- Preview data: Always stored for quick access

**Limitations**:
- MongoDB document size: 16MB max (handled via GridFS)
- Preview data: Limited to 1000 rows
- Column limit: Unlimited

---

### Collection: `training_metadata`

**Purpose**: Store ML model training results and metadata

**Schema**:
```javascript
{
  "_id": ObjectId("..."),
  "id": "uuid-string",
  "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
  "workspace_name": "latency_analysis_nov3",
  "model_name": "Random Forest",
  "model_type": "regression",  // or "classification"
  "problem_type": "regression",
  "target_variable": "latency_ms",
  "features": ["cpu_usage", "memory_usage", "request_rate"],
  "metrics": {
    "r2_score": 0.8567,
    "mse": 123.45,
    "rmse": 11.11,
    "mae": 8.92
  },
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 10,
    "min_samples_split": 2
  },
  "feature_importance": {
    "cpu_usage": 0.45,
    "memory_usage": 0.35,
    "request_rate": 0.20
  },
  "training_time": 12.5,  // seconds
  "is_best": true,
  "created_at": ISODate("2024-11-09T10:00:00Z"),
  "analysis_type": "holistic",
  "feedback": {
    "rating": 5,
    "comments": "Excellent model"
  }
}
```

**Indexes**:
```javascript
db.training_metadata.createIndex({ "id": 1 }, { unique: true });
db.training_metadata.createIndex({ "dataset_id": 1 });
db.training_metadata.createIndex({ "workspace_name": 1 });
db.training_metadata.createIndex({ "created_at": -1 });
db.training_metadata.createIndex({ "dataset_id": 1, "workspace_name": 1 });
```

**Storage**: ~5KB per model result

**Limitations**: None (can store unlimited models)

---

### Collection: `workspace_states`

**Purpose**: Save complete workspace state for later restoration

**Schema**:
```javascript
{
  "_id": ObjectId("..."),
  "id": "uuid-string",
  "workspace_name": "latency_analysis_nov3",
  "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
  "predictive_analysis": {  // Cached analysis results
    "ml_models": [...],
    "feature_importance": {...},
    "correlations": {...}
  },
  "visualization": {  // Cached charts
    "charts": [...],
    "custom_charts": [...]
  },
  "variable_selection": {
    "target": "latency_ms",
    "features": ["cpu_usage", "memory_usage"]
  },
  "large_data_blob_id": ObjectId("..."),  // If state >5MB
  "created_at": ISODate("2024-11-09T10:00:00Z"),
  "updated_at": ISODate("2024-11-09T10:00:00Z")
}
```

**Indexes**:
```javascript
db.workspace_states.createIndex({ "workspace_name": 1, "dataset_id": 1 }, { unique: true });
db.workspace_states.createIndex({ "dataset_id": 1 });
```

**Storage**: Variable (1MB-20MB typical, >20MB stored in GridFS)

---

### GridFS Collections: `fs.files` & `fs.chunks`

**Purpose**: Store large binary data (datasets, workspace states)

**fs.files Schema**:
```javascript
{
  "_id": ObjectId("..."),
  "length": 52428800,  // File size in bytes
  "chunkSize": 261120,  // 255KB chunks
  "uploadDate": ISODate("2024-11-09T10:00:00Z"),
  "filename": "application_latency.csv",
  "metadata": {
    "dataset_id": "uuid-string",
    "source_table": "applications",
    "row_count": 50000,
    "column_count": 12
  }
}
```

**fs.chunks Schema**:
```javascript
{
  "_id": ObjectId("..."),
  "files_id": ObjectId("..."),  // Reference to fs.files
  "n": 0,  // Chunk sequence number
  "data": BinData(0, "...base64...")  // Binary data
}
```

**Indexes** (Auto-created by GridFS):
```javascript
db.fs.files.createIndex({ "filename": 1, "uploadDate": 1 });
db.fs.chunks.createIndex({ "files_id": 1, "n": 1 }, { unique: true });
```

**Storage**: Unlimited (cloud storage)

**Limitations**:
- Max file size: 16GB per file (MongoDB limit)
- Chunk size: 255KB (default)

---

## Oracle Schema

### Tables Overview

| Table | Purpose | Rows | Primary Key | Storage |
|-------|---------|------|-------------|--------|
| `DATASETS` | Dataset metadata | ~1000s | id (VARCHAR2) | TABLESPACE |
| `TRAINING_METADATA` | ML training results | ~10000s | id (VARCHAR2) | TABLESPACE |
| `WORKSPACE_STATES` | Workspace configurations | ~100s | id (VARCHAR2) | TABLESPACE |
| `LARGE_DATASETS` | BLOB storage for large files | ~100s | id (VARCHAR2) | BLOB TABLESPACE |

---

### Table: `DATASETS`

**DDL**:
```sql
CREATE TABLE DATASETS (
    id VARCHAR2(255) PRIMARY KEY,
    name VARCHAR2(500) NOT NULL,
    row_count NUMBER DEFAULT 0,
    column_count NUMBER DEFAULT 0,
    columns CLOB CHECK (columns IS JSON),
    dtypes CLOB CHECK (dtypes IS JSON),
    data_preview CLOB CHECK (data_preview IS JSON),
    storage_type VARCHAR2(50) DEFAULT 'direct',
    gridfs_file_id VARCHAR2(255),
    source_type VARCHAR2(100),
    source_table VARCHAR2(255),
    source_config CLOB CHECK (source_config IS JSON),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    storage_format VARCHAR2(50)
);

CREATE INDEX idx_datasets_name ON DATASETS(name);
CREATE INDEX idx_datasets_created_at ON DATASETS(created_at DESC);

COMMENT ON TABLE DATASETS IS 'Stores uploaded dataset metadata and preview data';
COMMENT ON COLUMN DATASETS.id IS 'UUID primary key';
COMMENT ON COLUMN DATASETS.data_preview IS 'JSON array of first 1000 rows for quick display';
COMMENT ON COLUMN DATASETS.storage_type IS 'direct (inline) or blob (separate storage)';
```

**DML Examples**:
```sql
-- Insert dataset
INSERT INTO DATASETS (id, name, row_count, column_count, columns, dtypes, data_preview, storage_type, created_at)
VALUES (
    'uuid-string',
    'application_latency.csv',
    10000,
    12,
    '["timestamp", "latency_ms", "status"]',
    '{"timestamp": "datetime64[ns]", "latency_ms": "float64"}',
    '[{"timestamp": "2024-01-01 10:00:00", "latency_ms": 234.5}]',
    'blob',
    CURRENT_TIMESTAMP
);

-- Query datasets
SELECT id, name, row_count, column_count, created_at
FROM DATASETS
ORDER BY created_at DESC;

-- Update dataset
UPDATE DATASETS
SET updated_at = CURRENT_TIMESTAMP,
    row_count = 15000
WHERE id = 'uuid-string';

-- Delete dataset
DELETE FROM DATASETS WHERE id = 'uuid-string';
```

**Storage**:
- Row size: ~10KB-50KB (with preview data)
- CLOB fields: Up to 4GB each
- Total table size: ~10MB-500MB typical

**Limitations**:
- VARCHAR2 max: 4000 bytes (use CLOB for longer)
- CLOB max: 4GB per field
- Row limit: Unlimited

---

### Table: `TRAINING_METADATA`

**DDL**:
```sql
CREATE TABLE TRAINING_METADATA (
    id VARCHAR2(255) PRIMARY KEY,
    dataset_id VARCHAR2(255) NOT NULL,
    workspace_name VARCHAR2(500),
    model_name VARCHAR2(255) NOT NULL,
    model_type VARCHAR2(50),
    problem_type VARCHAR2(50),
    target_variable VARCHAR2(255),
    features CLOB CHECK (features IS JSON),
    metrics CLOB CHECK (metrics IS JSON),
    hyperparameters CLOB CHECK (hyperparameters IS JSON),
    feature_importance CLOB CHECK (feature_importance IS JSON),
    training_time NUMBER,
    is_best NUMBER(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analysis_type VARCHAR2(100),
    feedback CLOB CHECK (feedback IS JSON),
    CONSTRAINT fk_training_dataset FOREIGN KEY (dataset_id) REFERENCES DATASETS(id) ON DELETE CASCADE
);

CREATE INDEX idx_training_dataset_id ON TRAINING_METADATA(dataset_id);
CREATE INDEX idx_training_workspace ON TRAINING_METADATA(workspace_name);
CREATE INDEX idx_training_created_at ON TRAINING_METADATA(created_at DESC);
CREATE INDEX idx_training_composite ON TRAINING_METADATA(dataset_id, workspace_name);

COMMENT ON TABLE TRAINING_METADATA IS 'Stores ML model training results and performance metrics';
COMMENT ON COLUMN TRAINING_METADATA.is_best IS 'Boolean: 1 if best model for this dataset, 0 otherwise';
```

**DML Examples**:
```sql
-- Insert training result
INSERT INTO TRAINING_METADATA (id, dataset_id, workspace_name, model_name, model_type, metrics, is_best, created_at)
VALUES (
    'uuid-string',
    'dataset-uuid',
    'latency_analysis_nov3',
    'Random Forest',
    'regression',
    '{"r2_score": 0.8567, "rmse": 11.11}',
    1,
    CURRENT_TIMESTAMP
);

-- Query best models
SELECT model_name, metrics, training_time
FROM TRAINING_METADATA
WHERE dataset_id = 'dataset-uuid'
  AND is_best = 1
ORDER BY created_at DESC;

-- Count models by workspace
SELECT workspace_name, COUNT(*) as model_count
FROM TRAINING_METADATA
GROUP BY workspace_name;
```

**Storage**: ~5KB per row

---

### Table: `WORKSPACE_STATES`

**DDL**:
```sql
CREATE TABLE WORKSPACE_STATES (
    id VARCHAR2(255) PRIMARY KEY,
    workspace_name VARCHAR2(500) NOT NULL,
    dataset_id VARCHAR2(255) NOT NULL,
    predictive_analysis CLOB CHECK (predictive_analysis IS JSON),
    visualization CLOB CHECK (visualization IS JSON),
    variable_selection CLOB CHECK (variable_selection IS JSON),
    large_data_blob_id VARCHAR2(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_workspace UNIQUE (workspace_name, dataset_id),
    CONSTRAINT fk_workspace_dataset FOREIGN KEY (dataset_id) REFERENCES DATASETS(id) ON DELETE CASCADE
);

CREATE INDEX idx_workspace_dataset ON WORKSPACE_STATES(dataset_id);

COMMENT ON TABLE WORKSPACE_STATES IS 'Stores complete workspace configurations for restoration';
```

**Storage**: 1MB-20MB per workspace (typical)

---

### Table: `LARGE_DATASETS`

**DDL**:
```sql
CREATE TABLE LARGE_DATASETS (
    id VARCHAR2(255) PRIMARY KEY,
    dataset_id VARCHAR2(255),
    filename VARCHAR2(500),
    file_size NUMBER,
    content_type VARCHAR2(100),
    data_blob BLOB,
    metadata CLOB CHECK (metadata IS JSON),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_large_dataset FOREIGN KEY (dataset_id) REFERENCES DATASETS(id) ON DELETE CASCADE
);

CREATE INDEX idx_large_dataset_id ON LARGE_DATASETS(dataset_id);

COMMENT ON TABLE LARGE_DATASETS IS 'BLOB storage for large dataset files (>5MB)';
COMMENT ON COLUMN LARGE_DATASETS.data_blob IS 'Binary data up to 4GB';
```

**DML Examples**:
```sql
-- Insert BLOB data
INSERT INTO LARGE_DATASETS (id, dataset_id, filename, file_size, data_blob, upload_date)
VALUES (
    'uuid-string',
    'dataset-uuid',
    'large_file.csv',
    52428800,
    EMPTY_BLOB(),
    CURRENT_TIMESTAMP
) RETURNING data_blob INTO :blob_locator;
-- Then write BLOB data using cx_Oracle BLOB operations

-- Query BLOB metadata
SELECT id, filename, file_size, upload_date
FROM LARGE_DATASETS
WHERE dataset_id = 'dataset-uuid';

-- Retrieve BLOB data
SELECT data_blob
FROM LARGE_DATASETS
WHERE id = 'uuid-string';
```

**Storage**:
- BLOB max size: 4GB per field (Oracle limit)
- Stored in separate BLOB tablespace for performance

**Limitations**:
- Max BLOB size: 4GB
- Requires LOB operations for reading/writing

---

## Data Types & Constraints

### MongoDB to Oracle Type Mapping

| MongoDB Type | Oracle Type | Notes |
|--------------|-------------|-------|
| String | VARCHAR2 or CLOB | <4000 chars = VARCHAR2 |
| Number | NUMBER | Handles integers and floats |
| Boolean | NUMBER(1) | 0=false, 1=true |
| Date | TIMESTAMP | ISO format |
| Array | CLOB (JSON) | JSON format |
| Object | CLOB (JSON) | JSON format |
| Binary | BLOB | For large files |
| ObjectId | VARCHAR2(255) | Converted to string |

### JSON Validation in Oracle

```sql
-- Oracle 19c supports JSON validation
ALTER TABLE DATASETS ADD CONSTRAINT check_columns_json
  CHECK (columns IS JSON);

ALTER TABLE TRAINING_METADATA ADD CONSTRAINT check_metrics_json
  CHECK (metrics IS JSON);
```

---

## Indexes

### MongoDB Indexes

```javascript
// Create all indexes
use promise_ai;

// Datasets
db.datasets.createIndex({ "id": 1 }, { unique: true });
db.datasets.createIndex({ "name": 1 });
db.datasets.createIndex({ "created_at": -1 });

// Training Metadata
db.training_metadata.createIndex({ "id": 1 }, { unique: true });
db.training_metadata.createIndex({ "dataset_id": 1 });
db.training_metadata.createIndex({ "workspace_name": 1 });
db.training_metadata.createIndex({ "dataset_id": 1, "workspace_name": 1 });
db.training_metadata.createIndex({ "created_at": -1 });

// Workspace States
db.workspace_states.createIndex({ "workspace_name": 1, "dataset_id": 1 }, { unique: true });
db.workspace_states.createIndex({ "dataset_id": 1 });

// GridFS (auto-created)
db.fs.files.createIndex({ "filename": 1, "uploadDate": 1 });
db.fs.chunks.createIndex({ "files_id": 1, "n": 1 }, { unique: true });
```

### Oracle Indexes

All indexes shown in DDL statements above. Key indexes:
- Primary keys (automatic index)
- Foreign keys (for join performance)
- Composite indexes for common query patterns
- Descending indexes on timestamp columns

---

## Storage & Limitations

### MongoDB Atlas

**Storage Limits**:
- Free Tier (M0): 512MB total
- M10 (Dev): 10GB - 2TB
- M30+ (Prod): Up to 4TB per shard

**Document Limits**:
- Max document size: 16MB
- Max nesting depth: 100 levels
- Max array elements: Unlimited (practical: <100K)

**GridFS**:
- Max file size: 16GB per file
- Chunk size: 255KB (default)
- Storage: Counts toward cluster storage limit

**Performance**:
- Queries: Sub-millisecond for indexed fields
- Writes: ~1000-10000 writes/sec (depends on tier)
- Connections: M10=250, M30=500, M40+=1500

### Oracle RDS 19c

**Storage Limits**:
- Min storage: 20GB
- Max storage: 64TB
- IOPS: Up to 80,000 (io1)

**Row/Column Limits**:
- Max row size: 8KB (inline data)
- Max columns: 1000 per table
- Max CLOB size: 4GB
- Max BLOB size: 4GB

**Performance**:
- Queries: Sub-millisecond for indexed queries
- Connection pool: 10-100 connections (configurable)
- Transactions: ACID compliant

**Tablespace**:
```sql
-- Check tablespace usage
SELECT tablespace_name,
       ROUND(used_space * 8192/1024/1024/1024, 2) AS used_gb,
       ROUND(tablespace_size * 8192/1024/1024/1024, 2) AS total_gb,
       ROUND(used_percent, 2) AS used_percent
FROM dba_tablespace_usage_metrics;
```

---

## Migration Scripts

### MongoDB to Oracle Migration

```python
# backend/migrate_mongo_to_oracle.py
import asyncio
from app.database.adapters.mongodb_adapter import MongoDBAdapter
from app.database.adapters.oracle_adapter import OracleAdapter

async def migrate():
    mongo = MongoDBAdapter()
    oracle = OracleAdapter()
    
    # Migrate datasets
    datasets = await mongo.list_datasets()
    for dataset in datasets:
        await oracle.save_dataset(dataset)
    
    # Migrate training metadata
    # ... similar pattern
    
    print(f"Migrated {len(datasets)} datasets")

if __name__ == "__main__":
    asyncio.run(migrate())
```

### Oracle to MongoDB Migration

```python
# backend/migrate_oracle_to_mongo.py
# Similar reverse migration script
```

---

## Maintenance Queries

### MongoDB Maintenance

```javascript
// Check collection stats
db.datasets.stats();
db.training_metadata.stats();

// Compact collection (reclaim space)
db.runCommand({ compact: 'datasets', force: true });

// Rebuild indexes
db.datasets.reIndex();

// Check index usage
db.datasets.aggregate([
  { $indexStats: {} }
]);
```

### Oracle Maintenance

```sql
-- Gather statistics
EXEC DBMS_STATS.GATHER_SCHEMA_STATS('PROMISE_AI');

-- Check table sizes
SELECT segment_name, bytes/1024/1024 AS size_mb
FROM user_segments
WHERE segment_type = 'TABLE'
ORDER BY bytes DESC;

-- Rebuild indexes
ALTER INDEX idx_datasets_name REBUILD ONLINE;

-- Check fragmentation
SELECT table_name, blocks, empty_blocks
FROM user_tables;

-- Archive old data
DELETE FROM TRAINING_METADATA
WHERE created_at < ADD_MONTHS(CURRENT_TIMESTAMP, -6);
COMMIT;
```

---

For setup instructions, see [LOCAL_SETUP.md](LOCAL_SETUP.md)

For architecture overview, see [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)
