# PROMISE AI - Database Documentation

## 🗄️ Database Architecture Overview

PROMISE AI supports dual-database architecture with **Oracle RDS 19c** and **MongoDB** as storage backends, providing flexibility for different deployment scenarios.

---

## 🏗️ Architecture Pattern

### Database Adapter Pattern

```
┌─────────────────────────────────────────┐
│         Application Layer                │
│      (FastAPI Routes & Services)         │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│       Database Factory Pattern           │
│   (Selects adapter based on DB_TYPE)    │
└────────────────┬────────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
         ↓               ↓
┌────────────────┐  ┌────────────────┐
│ Oracle Adapter │  │ MongoDB Adapter│
│                │  │                │
│ • Connection   │  │ • Motor Client │
│   Pool         │  │ • GridFS       │
│ • BLOB Storage │  │ • Collections  │
│ • JSON Columns │  │ • Documents    │
└────────┬───────┘  └────────┬───────┘
         │                   │
         ↓                   ↓
┌────────────────┐  ┌────────────────┐
│  Oracle 19c    │  │   MongoDB      │
│  RDS Instance  │  │   Database     │
└────────────────┘  └────────────────┘
```

---

## 📊 Database Schema

### Oracle RDS 19c Schema

#### 1. **DATASETS** Table

**Purpose**: Stores dataset metadata and references.

**DDL (Data Definition Language)**:
```sql
CREATE TABLE datasets (
    id VARCHAR2(36) PRIMARY KEY,
    name VARCHAR2(500) NOT NULL,
    source VARCHAR2(50) DEFAULT 'upload',
    row_count NUMBER(12) DEFAULT 0,
    column_count NUMBER(6) DEFAULT 0,
    
    -- JSON columns for flexible schema (Oracle 12c+ compatible)
    columns_json CLOB CHECK (columns_json IS JSON),
    dtypes_json CLOB CHECK (dtypes_json IS JSON),
    data_preview_json CLOB CHECK (data_preview_json IS JSON),
    
    -- File storage reference
    storage_type VARCHAR2(20) DEFAULT 'direct',
    file_id VARCHAR2(36),
    
    -- Metadata
    training_count NUMBER(6) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_trained_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_storage_type CHECK (storage_type IN ('direct', 'blob'))
);

-- Indexes
CREATE INDEX idx_datasets_created ON datasets(created_at DESC);
CREATE INDEX idx_datasets_name ON datasets(name);
CREATE INDEX idx_datasets_file_id ON datasets(file_id);
```

**DDL Mapping Diagram**:
```
┌─────────────────────────────────────────────────────────────┐
│                      DATASETS Table                          │
├────────────────────┬───────────────┬────────────────────────┤
│ Column Name        │ Data Type     │ Description            │
├────────────────────┼───────────────┼────────────────────────┤
│ id (PK)            │ VARCHAR2(36)  │ UUID of dataset        │
│ name               │ VARCHAR2(500) │ Dataset name           │
│ source             │ VARCHAR2(50)  │ upload/postgresql/etc  │
│ row_count          │ NUMBER(12)    │ Number of rows         │
│ column_count       │ NUMBER(6)     │ Number of columns      │
│ columns_json       │ CLOB (JSON)   │ Column names array     │
│ dtypes_json        │ CLOB (JSON)   │ Data types mapping     │
│ data_preview_json  │ CLOB (JSON)   │ First 5 rows preview   │
│ storage_type       │ VARCHAR2(20)  │ direct/blob            │
│ file_id (FK)       │ VARCHAR2(36)  │ → file_storage.id      │
│ training_count     │ NUMBER(6)     │ Training session count │
│ created_at         │ TIMESTAMP     │ Creation timestamp     │
│ last_trained_at    │ TIMESTAMP     │ Last training time     │
└────────────────────┴───────────────┴────────────────────────┘
```

**Column Details**:
- **id**: Primary key, UUID format (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)
- **columns_json**: JSON array like `["col1", "col2", "col3"]`
- **dtypes_json**: JSON object like `{"col1": "int64", "col2": "float64"}`
- **data_preview_json**: JSON array of row arrays `[[val1, val2], [val3, val4]]`

**DML (Data Manipulation Language) Examples**:

```sql
-- INSERT: Create new dataset
INSERT INTO datasets (
    id, name, source, row_count, column_count,
    columns_json, dtypes_json, data_preview_json,
    storage_type, training_count, created_at
) VALUES (
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'sales_data.csv',
    'upload',
    1000,
    5,
    '["date", "product", "quantity", "price", "revenue"]',
    '{"date": "object", "product": "object", "quantity": "int64", "price": "float64", "revenue": "float64"}',
    '[["2025-01-01", "Widget A", 100, 25.50, 2550.00], ["2025-01-02", "Widget B", 150, 30.00, 4500.00]]',
    'direct',
    0,
    CURRENT_TIMESTAMP
);

-- SELECT: Retrieve dataset by ID
SELECT id, name, row_count, column_count, training_count, 
       created_at, last_trained_at
FROM datasets
WHERE id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';

-- SELECT: Get recent datasets
SELECT id, name, row_count, training_count, created_at
FROM datasets
ORDER BY created_at DESC
FETCH FIRST 10 ROWS ONLY;

-- UPDATE: Increment training count
UPDATE datasets
SET training_count = training_count + 1,
    last_trained_at = CURRENT_TIMESTAMP
WHERE id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';

-- DELETE: Remove dataset
DELETE FROM datasets
WHERE id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';

-- Query JSON columns (Oracle 12c+)
SELECT id, name, 
       JSON_VALUE(columns_json, '$[0]') as first_column,
       JSON_VALUE(dtypes_json, '$.price') as price_dtype
FROM datasets
WHERE JSON_EXISTS(columns_json, '$[?(@=="price")]');
```

---

#### 2. **FILE_STORAGE** Table

**Purpose**: Stores large files (datasets > 1MB) as BLOBs.

**DDL**:
```sql
CREATE SEQUENCE file_storage_seq START WITH 1 INCREMENT BY 1;

CREATE TABLE file_storage (
    id VARCHAR2(36) PRIMARY KEY,
    filename VARCHAR2(500) NOT NULL,
    file_data BLOB,
    
    -- Metadata as JSON
    metadata_json CLOB CHECK (metadata_json IS JSON),
    
    -- File info
    file_size NUMBER(15) DEFAULT 0,
    compressed CHAR(1) DEFAULT 'N',
    original_size NUMBER(15),
    mime_type VARCHAR2(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_compressed CHECK (compressed IN ('Y', 'N'))
);

-- Indexes
CREATE INDEX idx_file_storage_filename ON file_storage(filename);
CREATE INDEX idx_file_storage_created ON file_storage(created_at DESC);
```

**DDL Mapping Diagram**:
```
┌─────────────────────────────────────────────────────────────┐
│                   FILE_STORAGE Table                         │
├────────────────────┬───────────────┬────────────────────────┤
│ Column Name        │ Data Type     │ Description            │
├────────────────────┼───────────────┼────────────────────────┤
│ id (PK)            │ VARCHAR2(36)  │ UUID of file           │
│ filename           │ VARCHAR2(500) │ Original filename      │
│ file_data          │ BLOB          │ Compressed CSV data    │
│ metadata_json      │ CLOB (JSON)   │ File metadata          │
│ file_size          │ NUMBER(15)    │ Compressed size (bytes)│
│ compressed         │ CHAR(1)       │ Y/N compression flag   │
│ original_size      │ NUMBER(15)    │ Original size (bytes)  │
│ mime_type          │ VARCHAR2(100) │ text/csv, etc.         │
│ created_at         │ TIMESTAMP     │ Upload timestamp       │
└────────────────────┴───────────────┴────────────────────────┘
```

**DML Examples**:

```sql
-- INSERT: Store compressed CSV file
INSERT INTO file_storage (
    id, filename, file_data, metadata_json,
    file_size, compressed, original_size, mime_type, created_at
) VALUES (
    'f1a2b3c4-d5e6-7890-abcd-ef1234567890',
    'sales_data.csv',
    :blob_data,  -- BLOB bind variable
    '{"compression": "gzip", "type": "dataset", "encoding": "utf-8"}',
    524288,     -- 512 KB compressed
    'Y',
    2097152,    -- 2 MB original
    'text/csv',
    CURRENT_TIMESTAMP
);

-- SELECT: Retrieve file metadata (not BLOB)
SELECT id, filename, file_size, compressed, original_size, created_at
FROM file_storage
WHERE id = 'f1a2b3c4-d5e6-7890-abcd-ef1234567890';

-- SELECT: Retrieve file with BLOB data
SELECT id, filename, file_data, compressed
FROM file_storage
WHERE id = 'f1a2b3c4-d5e6-7890-abcd-ef1234567890';

-- UPDATE: Update metadata
UPDATE file_storage
SET metadata_json = '{"compression": "gzip", "type": "dataset", "version": 2}'
WHERE id = 'f1a2b3c4-d5e6-7890-abcd-ef1234567890';

-- DELETE: Remove file
DELETE FROM file_storage
WHERE id = 'f1a2b3c4-d5e6-7890-abcd-ef1234567890';
```

**Working with BLOBs in Python**:
```python
import cx_Oracle
import gzip

# Store file as BLOB
def save_file_to_blob(connection, file_id, file_path):
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    compressed_data = gzip.compress(file_data)
    
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO file_storage (id, filename, file_data, compressed, file_size)
        VALUES (:id, :filename, :blob, 'Y', :size)
        """,
        id=file_id,
        filename=file_path,
        blob=compressed_data,
        size=len(compressed_data)
    )
    connection.commit()

# Retrieve BLOB
def get_file_from_blob(connection, file_id):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT file_data, compressed FROM file_storage WHERE id = :id",
        id=file_id
    )
    row = cursor.fetchone()
    
    if row:
        blob_data = row[0].read()  # Read BLOB
        if row[1] == 'Y':
            return gzip.decompress(blob_data)
        return blob_data
```

---

#### 3. **WORKSPACE_STATES** Table

**Purpose**: Stores saved analysis workspaces with results and chat history.

**DDL**:
```sql
CREATE TABLE workspace_states (
    id VARCHAR2(36) PRIMARY KEY,
    dataset_id VARCHAR2(36) NOT NULL,
    state_name VARCHAR2(500) NOT NULL,
    
    -- Storage strategy
    storage_type VARCHAR2(20) DEFAULT 'direct',
    file_id VARCHAR2(36),
    
    -- Direct storage (for small workspaces)
    analysis_data_json CLOB CHECK (analysis_data_json IS JSON),
    chat_history_json CLOB CHECK (chat_history_json IS JSON),
    
    -- Size tracking
    size_bytes NUMBER(15) DEFAULT 0,
    compressed_size NUMBER(15),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_workspace_dataset FOREIGN KEY (dataset_id) 
        REFERENCES datasets(id) ON DELETE CASCADE,
    CONSTRAINT fk_workspace_file FOREIGN KEY (file_id) 
        REFERENCES file_storage(id) ON DELETE SET NULL,
    CONSTRAINT chk_ws_storage_type CHECK (storage_type IN ('direct', 'blob'))
);

-- Indexes
CREATE INDEX idx_workspace_dataset ON workspace_states(dataset_id);
CREATE INDEX idx_workspace_name ON workspace_states(state_name);
CREATE INDEX idx_workspace_created ON workspace_states(created_at DESC);
```

**DDL Mapping Diagram**:
```
┌─────────────────────────────────────────────────────────────┐
│                WORKSPACE_STATES Table                        │
├────────────────────┬───────────────┬────────────────────────┤
│ Column Name        │ Data Type     │ Description            │
├────────────────────┼───────────────┼────────────────────────┤
│ id (PK)            │ VARCHAR2(36)  │ UUID of workspace      │
│ dataset_id (FK)    │ VARCHAR2(36)  │ → datasets.id          │
│ state_name         │ VARCHAR2(500) │ Workspace name         │
│ storage_type       │ VARCHAR2(20)  │ direct/blob            │
│ file_id (FK)       │ VARCHAR2(36)  │ → file_storage.id      │
│ analysis_data_json │ CLOB (JSON)   │ Analysis results       │
│ chat_history_json  │ CLOB (JSON)   │ Chat messages          │
│ size_bytes         │ NUMBER(15)    │ Total size             │
│ compressed_size    │ NUMBER(15)    │ Compressed size        │
│ created_at         │ TIMESTAMP     │ Creation timestamp     │
│ updated_at         │ TIMESTAMP     │ Last update timestamp  │
└────────────────────┴───────────────┴────────────────────────┘

Foreign Keys:
  workspace_states.dataset_id → datasets.id (ON DELETE CASCADE)
  workspace_states.file_id → file_storage.id (ON DELETE SET NULL)
```

**DML Examples**:

```sql
-- INSERT: Save analysis workspace
INSERT INTO workspace_states (
    id, dataset_id, state_name, storage_type,
    analysis_data_json, chat_history_json,
    size_bytes, created_at, updated_at
) VALUES (
    'w1a2b3c4-d5e6-7890-abcd-ef1234567890',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'Sales Analysis - Q1 2025',
    'direct',
    '{"ml_models": [{"name": "XGBoost", "r2_score": 0.92}], "feature_importance": {"price": 0.65}}',
    '[{"role": "user", "content": "Show me top features"}, {"role": "assistant", "content": "Price is most important"}]',
    8192,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- SELECT: Get workspace by ID
SELECT id, dataset_id, state_name, analysis_data_json, 
       chat_history_json, created_at
FROM workspace_states
WHERE id = 'w1a2b3c4-d5e6-7890-abcd-ef1234567890';

-- SELECT: Get all workspaces for a dataset
SELECT id, state_name, size_bytes, created_at, updated_at
FROM workspace_states
WHERE dataset_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
ORDER BY updated_at DESC;

-- UPDATE: Update workspace
UPDATE workspace_states
SET analysis_data_json = '{"ml_models": [...], "updated": true}',
    updated_at = CURRENT_TIMESTAMP
WHERE id = 'w1a2b3c4-d5e6-7890-abcd-ef1234567890';

-- DELETE: Remove workspace (CASCADE deletes from file_storage)
DELETE FROM workspace_states
WHERE id = 'w1a2b3c4-d5e6-7890-abcd-ef1234567890';
```

---

#### 4. **PREDICTION_FEEDBACK** Table

**Purpose**: Stores user feedback on model predictions for active learning.

**DDL**:
```sql
CREATE TABLE prediction_feedback (
    id VARCHAR2(36) PRIMARY KEY,
    prediction_id VARCHAR2(36) UNIQUE NOT NULL,
    dataset_id VARCHAR2(36) NOT NULL,
    model_name VARCHAR2(200) NOT NULL,
    
    is_correct CHAR(1) NOT NULL,
    prediction VARCHAR2(500),
    actual_outcome VARCHAR2(500),
    "comment" CLOB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_feedback_dataset FOREIGN KEY (dataset_id) 
        REFERENCES datasets(id) ON DELETE CASCADE,
    CONSTRAINT chk_is_correct CHECK (is_correct IN ('Y', 'N'))
);

-- Indexes
CREATE INDEX idx_feedback_dataset_model ON prediction_feedback(dataset_id, model_name);
CREATE INDEX idx_feedback_created ON prediction_feedback(created_at DESC);
```

**DDL Mapping Diagram**:
```
┌─────────────────────────────────────────────────────────────┐
│              PREDICTION_FEEDBACK Table                       │
├────────────────────┬───────────────┬────────────────────────┤
│ Column Name        │ Data Type     │ Description            │
├────────────────────┼───────────────┼────────────────────────┤
│ id (PK)            │ VARCHAR2(36)  │ UUID of feedback       │
│ prediction_id (UK) │ VARCHAR2(36)  │ Unique prediction ID   │
│ dataset_id (FK)    │ VARCHAR2(36)  │ → datasets.id          │
│ model_name         │ VARCHAR2(200) │ Model used             │
│ is_correct         │ CHAR(1)       │ Y/N correctness flag   │
│ prediction         │ VARCHAR2(500) │ Predicted value        │
│ actual_outcome     │ VARCHAR2(500) │ Actual value           │
│ comment            │ CLOB          │ User comments          │
│ created_at         │ TIMESTAMP     │ Feedback timestamp     │
└────────────────────┴───────────────┴────────────────────────┘

Foreign Keys:
  prediction_feedback.dataset_id → datasets.id (ON DELETE CASCADE)
```

**DML Examples**:

```sql
-- INSERT: Submit feedback
INSERT INTO prediction_feedback (
    id, prediction_id, dataset_id, model_name,
    is_correct, prediction, actual_outcome, "comment", created_at
) VALUES (
    'fb1a2b3c-d4e5-6789-0abc-def123456789',
    'pred-12345',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'XGBoost',
    'Y',
    '250000',
    '248000',
    'Very close prediction, only 2K off',
    CURRENT_TIMESTAMP
);

-- SELECT: Get feedback for a model
SELECT prediction_id, is_correct, prediction, actual_outcome, 
       "comment", created_at
FROM prediction_feedback
WHERE dataset_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
  AND model_name = 'XGBoost'
ORDER BY created_at DESC;

-- SELECT: Calculate model accuracy from feedback
SELECT model_name,
       COUNT(*) as total_predictions,
       SUM(CASE WHEN is_correct = 'Y' THEN 1 ELSE 0 END) as correct_predictions,
       ROUND(SUM(CASE WHEN is_correct = 'Y' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as accuracy_percentage
FROM prediction_feedback
WHERE dataset_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
GROUP BY model_name;

-- SELECT: Get uncertain predictions (for active learning)
SELECT id, prediction_id, prediction, created_at
FROM prediction_feedback
WHERE is_correct = 'N'
  AND dataset_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
ORDER BY created_at DESC
FETCH FIRST 20 ROWS ONLY;

-- UPDATE: Correct a feedback entry
UPDATE prediction_feedback
SET is_correct = 'N',
    actual_outcome = '260000',
    "comment" = 'Corrected: actual was 260K, not 248K'
WHERE prediction_id = 'pred-12345';

-- DELETE: Remove feedback
DELETE FROM prediction_feedback
WHERE id = 'fb1a2b3c-d4e5-6789-0abc-def123456789';
```

---

### 5. **TRAINING_METADATA** Table

**Purpose**: Tracks all ML training sessions for reproducibility and experiment tracking.

**DDL**:
```sql
CREATE TABLE training_metadata (
    id VARCHAR2(36) PRIMARY KEY,
    dataset_id VARCHAR2(36) NOT NULL,
    problem_type VARCHAR2(50) NOT NULL,
    target_variable VARCHAR2(200) NOT NULL,
    feature_variables CLOB,
    
    model_type VARCHAR2(200) NOT NULL,
    model_params_json CLOB CHECK (model_params_json IS JSON),
    
    metrics_json CLOB CHECK (metrics_json IS JSON),
    training_duration NUMBER(10, 3),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_training_dataset FOREIGN KEY (dataset_id)
        REFERENCES datasets(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_training_dataset ON training_metadata(dataset_id);
CREATE INDEX idx_training_model ON training_metadata(model_type);
CREATE INDEX idx_training_created ON training_metadata(created_at DESC);
```

**DDL Mapping Diagram**:
```
┌─────────────────────────────────────────────────────────────┐
│              TRAINING_METADATA Table                         │
├────────────────────┬───────────────┬────────────────────────┤
│ Column Name        │ Data Type     │ Description            │
├────────────────────┼───────────────┼────────────────────────┤
│ id (PK)            │ VARCHAR2(36)  │ UUID of training       │
│ dataset_id (FK)    │ VARCHAR2(36)  │ → datasets.id          │
│ problem_type       │ VARCHAR2(50)  │ regression/classification│
│ target_variable    │ VARCHAR2(200) │ Target column name     │
│ feature_variables  │ CLOB          │ Feature columns list   │
│ model_type         │ VARCHAR2(200) │ XGBoost, Random Forest │
│ model_params_json  │ CLOB (JSON)   │ Hyperparameters        │
│ metrics_json       │ CLOB (JSON)   │ R², RMSE, Accuracy     │
│ training_duration  │ NUMBER(10,3)  │ Duration in seconds    │
│ created_at         │ TIMESTAMP     │ Training timestamp     │
└────────────────────┴───────────────┴────────────────────────┘

Foreign Keys:
  training_metadata.dataset_id → datasets.id (ON DELETE CASCADE)
```

**DML Examples**:

```sql
-- INSERT: Record training session
INSERT INTO training_metadata (
    id, dataset_id, problem_type, target_variable, feature_variables,
    model_type, model_params_json, metrics_json, training_duration, created_at
) VALUES (
    'tm1a2b3c-d4e5-6789-0abc-def123456789',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'regression',
    'price',
    'sqft, bedrooms, bathrooms, age',
    'XGBoost',
    '{"n_estimators": 200, "max_depth": 20, "learning_rate": 0.1}',
    '{"r2_score": 0.92, "rmse": 15000, "mae": 12000}',
    2.543,
    CURRENT_TIMESTAMP
);

-- SELECT: Get training history for dataset
SELECT id, model_type, problem_type, target_variable,
       JSON_VALUE(metrics_json, '$.r2_score') as r2_score,
       training_duration, created_at
FROM training_metadata
WHERE dataset_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
ORDER BY created_at DESC;

-- SELECT: Compare models across all datasets
SELECT model_type,
       COUNT(*) as training_count,
       AVG(TO_NUMBER(JSON_VALUE(metrics_json, '$.r2_score'))) as avg_r2_score,
       AVG(training_duration) as avg_duration_seconds
FROM training_metadata
WHERE problem_type = 'regression'
GROUP BY model_type
ORDER BY avg_r2_score DESC;

-- SELECT: Get best performing model for a dataset
SELECT model_type, metrics_json, created_at
FROM training_metadata
WHERE dataset_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
  AND problem_type = 'regression'
ORDER BY TO_NUMBER(JSON_VALUE(metrics_json, '$.r2_score')) DESC
FETCH FIRST 1 ROW ONLY;

-- DELETE: Remove old training metadata (older than 90 days)
DELETE FROM training_metadata
WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '90' DAY;
```

---

## 📋 Entity Relationship Diagram (ERD)

```
┌──────────────────────────────────────────────────────────────┐
│                     DATASETS (Parent)                         │
│  • id (PK)                                                    │
│  • name, source, row_count, column_count                      │
│  • columns_json, dtypes_json, data_preview_json               │
│  • training_count, last_trained_at                            │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ 1:N (one-to-many)
                       │
       ┌───────────────┼────────────────────────┬────────────────┐
       │               │                        │                │
       ↓               ↓                        ↓                ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  ┌──────────────┐
│FILE_STORAGE  │  │WORKSPACE_    │  │PREDICTION_       │  │TRAINING_     │
│              │  │STATES        │  │FEEDBACK          │  │METADATA      │
│• id (PK)     │  │• id (PK)     │  │• id (PK)         │  │• id (PK)     │
│• filename    │  │• dataset_id  │  │• dataset_id (FK) │  │• dataset_id  │
│• file_data   │  │  (FK)        │  │• prediction_id   │  │  (FK)        │
│  (BLOB)      │  │• state_name  │  │• model_name      │  │• model_type  │
│• file_size   │  │• analysis_   │  │• is_correct      │  │• metrics_json│
│• compressed  │  │  data_json   │  │• actual_outcome  │  │• training_   │
│              │  │• chat_       │  │                  │  │  duration    │
│              │  │  history_json│  │                  │  │              │
└──────────────┘  └──────────────┘  └──────────────────┘  └──────────────┘
       ↑
       │ 1:1 (optional)
       │
┌──────┴───────┐
│ datasets     │
│ file_id (FK) │
└──────────────┘
```

**Relationships**:
1. **datasets ← file_storage** (1:1 optional): Dataset may reference a file in BLOB storage
2. **datasets → workspace_states** (1:N): One dataset can have multiple saved workspaces
3. **datasets → prediction_feedback** (1:N): One dataset can have multiple feedback entries
4. **datasets → training_metadata** (1:N): One dataset can have multiple training sessions
5. **file_storage ← workspace_states** (1:1 optional): Workspace may store large data in BLOB

---

## 🗃️ MongoDB Schema

### Collections Structure

```javascript
// 1. datasets collection
{
  "_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "sales_data.csv",
  "source": "upload",
  "row_count": 1000,
  "column_count": 5,
  "columns": ["date", "product", "quantity", "price", "revenue"],
  "dtypes": {
    "date": "object",
    "product": "object",
    "quantity": "int64",
    "price": "float64",
    "revenue": "float64"
  },
  "data_preview": [
    ["2025-01-01", "Widget A", 100, 25.50, 2550.00],
    ["2025-01-02", "Widget B", 150, 30.00, 4500.00]
  ],
  "storage_type": "gridfs",
  "file_id": "gridfs_file_id",
  "training_count": 5,
  "created_at": ISODate("2025-01-10T09:00:00Z"),
  "last_trained_at": ISODate("2025-01-15T10:30:00Z")
}

// 2. fs.files (GridFS - stores files)
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "filename": "sales_data.csv",
  "length": 2097152,  // File size in bytes
  "chunkSize": 261120,
  "uploadDate": ISODate("2025-01-10T09:00:00Z"),
  "metadata": {
    "compression": "gzip",
    "type": "dataset",
    "original_size": 4194304
  }
}

// 3. workspace_states collection
{
  "_id": "w1a2b3c4-d5e6-7890-abcd-ef1234567890",
  "dataset_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "state_name": "Sales Analysis - Q1 2025",
  "storage_type": "direct",
  "analysis_data": {
    "ml_models": [
      {
        "name": "XGBoost",
        "r2_score": 0.92,
        "rmse": 15000
      }
    ],
    "feature_importance": {
      "price": 0.65,
      "quantity": 0.25
    }
  },
  "chat_history": [
    {"role": "user", "content": "Show me top features"},
    {"role": "assistant", "content": "Price is most important"}
  ],
  "size_bytes": 8192,
  "created_at": ISODate("2025-01-15T11:00:00Z"),
  "updated_at": ISODate("2025-01-15T11:30:00Z")
}

// 4. prediction_feedback collection
{
  "_id": "fb1a2b3c-d4e5-6789-0abc-def123456789",
  "prediction_id": "pred-12345",
  "dataset_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "model_name": "XGBoost",
  "is_correct": true,
  "prediction": "250000",
  "actual_outcome": "248000",
  "comment": "Very close prediction, only 2K off",
  "created_at": ISODate("2025-01-15T12:00:00Z")
}

// 5. training_metadata collection
{
  "_id": "tm1a2b3c-d4e5-6789-0abc-def123456789",
  "dataset_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "problem_type": "regression",
  "target_variable": "price",
  "feature_variables": ["sqft", "bedrooms", "bathrooms", "age"],
  "model_type": "XGBoost",
  "model_params": {
    "n_estimators": 200,
    "max_depth": 20,
    "learning_rate": 0.1
  },
  "metrics": {
    "r2_score": 0.92,
    "rmse": 15000,
    "mae": 12000
  },
  "training_duration": 2.543,
  "created_at": ISODate("2025-01-15T10:30:00Z")
}
```

### MongoDB Queries

```javascript
// Find recent datasets
db.datasets.find().sort({ created_at: -1 }).limit(10);

// Find dataset by ID
db.datasets.findOne({ _id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890" });

// Update training count
db.datasets.updateOne(
  { _id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890" },
  { 
    $inc: { training_count: 1 },
    $set: { last_trained_at: new Date() }
  }
);

// Get training metadata for dataset
db.training_metadata.find({ 
  dataset_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890" 
}).sort({ created_at: -1 });

// Aggregate: Average R² score by model type
db.training_metadata.aggregate([
  { $match: { problem_type: "regression" } },
  { $group: {
      _id: "$model_type",
      avg_r2: { $avg: "$metrics.r2_score" },
      count: { $sum: 1 }
  }},
  { $sort: { avg_r2: -1 } }
]);

// Find feedback for model
db.prediction_feedback.find({
  dataset_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  model_name: "XGBoost"
}).sort({ created_at: -1 });

// Delete old training metadata (90+ days)
db.training_metadata.deleteMany({
  created_at: { $lt: new Date(Date.now() - 90*24*60*60*1000) }
});
```

---

## 🔧 Database Configuration

### Environment Variables

**Oracle**:
```env
DB_TYPE=oracle
ORACLE_DSN=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=host.rds.amazonaws.com)(PORT=1521))(CONNECT_DATA=(SID=ORCL)))
ORACLE_USER=admin
ORACLE_PASSWORD=your_password
ORACLE_POOL_MIN=2
ORACLE_POOL_MAX=10
```

**MongoDB**:
```env
DB_TYPE=mongodb
MONGO_URL=mongodb://localhost:27017/promise_ai
```

---

## 🚀 Initialization Scripts

### Oracle Schema Initialization

**File**: `init_oracle_schema.py`

```python
import cx_Oracle
import os
from dotenv import load_dotenv

load_dotenv()

def init_oracle_schema():
    dsn = os.getenv('ORACLE_DSN')
    user = os.getenv('ORACLE_USER')
    password = os.getenv('ORACLE_PASSWORD')
    
    connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
    
    with open('app/database/oracle_schema.sql', 'r') as f:
        schema_sql = f.read()
    
    cursor = connection.cursor()
    
    # Execute each statement
    for statement in schema_sql.split('/'):
        statement = statement.strip()
        if statement and not statement.startswith('--'):
            cursor.execute(statement)
    
    connection.commit()
    print("✅ Oracle schema initialized successfully")
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    init_oracle_schema()
```

### MongoDB Indexes

**File**: `create_indexes.py`

```python
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio

async def create_indexes():
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.promise_ai
    
    # Datasets indexes
    await db.datasets.create_index([("created_at", -1)])
    await db.datasets.create_index([("name", 1)])
    
    # Training metadata indexes
    await db.training_metadata.create_index([("dataset_id", 1)])
    await db.training_metadata.create_index([("created_at", -1)])
    await db.training_metadata.create_index([("model_type", 1)])
    
    # Workspace states indexes
    await db.workspace_states.create_index([("dataset_id", 1)])
    await db.workspace_states.create_index([("created_at", -1)])
    
    # Prediction feedback indexes
    await db.prediction_feedback.create_index([("dataset_id", 1), ("model_name", 1)])
    await db.prediction_feedback.create_index([("prediction_id", 1)], unique=True)
    
    print("✅ MongoDB indexes created successfully")
    client.close()

if __name__ == "__main__":
    asyncio.run(create_indexes())
```

---

## 📊 Performance Optimization

### Oracle Performance Tips

1. **Connection Pooling**: Use 2-10 connections for optimal performance
2. **JSON Indexing**: Create functional indexes on JSON columns for frequent queries
3. **Partitioning**: Partition large tables by date for faster queries
4. **Statistics**: Run `DBMS_STATS.GATHER_TABLE_STATS` regularly

```sql
-- Create functional index on JSON column
CREATE INDEX idx_datasets_columns_price 
ON datasets (JSON_EXISTS(columns_json, '$[?(@=="price")]'));

-- Gather statistics
EXEC DBMS_STATS.GATHER_TABLE_STATS(USER, 'DATASETS');
```

### MongoDB Performance Tips

1. **Indexes**: Create indexes on frequently queried fields
2. **Projection**: Use projection to return only needed fields
3. **Limit**: Always use `.limit()` for pagination
4. **Aggregation Pipeline**: Use for complex queries

```javascript
// Good: Use projection
db.datasets.find({}, { name: 1, row_count: 1, created_at: 1 });

// Good: Use limit for pagination
db.datasets.find().sort({ created_at: -1 }).limit(20);
```

---

## 🔐 Backup & Recovery

### Oracle Backup

```bash
# Export schema
exp userid=admin/password@ORCL file=promise_ai_backup.dmp full=y

# Import schema
imp userid=admin/password@ORCL file=promise_ai_backup.dmp full=y
```

### MongoDB Backup

```bash
# Backup database
mongodump --uri="mongodb://localhost:27017/promise_ai" --out=/backup/

# Restore database
mongorestore --uri="mongodb://localhost:27017/promise_ai" /backup/promise_ai/
```

---

## 📚 Additional Resources

- **Oracle Documentation**: https://docs.oracle.com/en/database/oracle/oracle-database/19/
- **MongoDB Documentation**: https://www.mongodb.com/docs/
- **cx_Oracle**: https://cx-oracle.readthedocs.io
- **Motor (MongoDB)**: https://motor.readthedocs.io

---

For backend API documentation, see `BACKEND.md`  
For frontend documentation, see `FRONTEND.md`
