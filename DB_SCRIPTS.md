# Database Scripts for PROMISE AI

This document contains the complete database schema and setup scripts for both **MongoDB** and **Oracle** databases to support the new workspace-first workflow with 30-day model tracking.

---

## MongoDB Setup

### Collections Overview

1. **workspaces** - Organize datasets and track projects
2. **datasets** - Store dataset metadata with workspace references
3. **training_metadata** - Track all training runs with workspace linkage
4. **saved_states** - User analysis states
5. **prediction_feedback** - User feedback on predictions
6. **fs.files** & **fs.chunks** - GridFS for large file storage

---

### MongoDB Collection Schemas

#### 1. Workspaces Collection

```javascript
db.workspaces.insertOne({
  id: "uuid-string",
  name: "Sales Forecasting Q4 2024",
  description: "Quarterly sales prediction models",
  tags: ["sales", "forecasting", "Q4"],
  created_at: "2024-01-01T00:00:00.000Z",
  updated_at: "2024-01-01T00:00:00.000Z",
  dataset_count: 0,
  training_count: 0
});

// Create indexes for workspaces
db.workspaces.createIndex({ id: 1 }, { unique: true });
db.workspaces.createIndex({ created_at: -1 });
db.workspaces.createIndex({ name: 1 });
```

#### 2. Datasets Collection (Updated with workspace_id)

```javascript
db.datasets.insertOne({
  id: "uuid-string",
  workspace_id: "workspace-uuid",  // NEW: Link to workspace
  name: "sales_data_2024.csv",
  row_count: 10000,
  column_count: 15,
  columns: ["date", "revenue", "region", "product"],
  dtypes: {
    date: "datetime64[ns]",
    revenue: "float64",
    region: "object",
    product: "object"
  },
  data_preview: [
    { date: "2024-01-01", revenue: 15000, region: "North", product: "A" }
    // ... first 1000 rows
  ],
  created_at: "2024-01-01T00:00:00.000Z",
  updated_at: "2024-01-01T00:00:00.000Z",
  file_size: 524288,
  source_type: "file_upload",  // or "database_query"
  storage_type: "blob",  // or "direct"
  gridfs_file_id: "gridfs-object-id",  // For blob storage
  training_count: 0,
  last_trained_at: null
});

// Create indexes for datasets
db.datasets.createIndex({ id: 1 }, { unique: true });
db.datasets.createIndex({ workspace_id: 1 });  // NEW: For workspace queries
db.datasets.createIndex({ created_at: -1 });
db.datasets.createIndex({ name: 1 });
```

#### 3. Training Metadata Collection (Updated)

```javascript
db.training_metadata.insertOne({
  id: "training-uuid",
  dataset_id: "dataset-uuid",
  workspace_id: "workspace-uuid",  // NEW: Direct workspace link
  model_type: "RandomForest",
  problem_type: "regression",
  target_variable: "revenue",
  feature_variables: ["region", "product", "date"],
  metrics: {
    r2_score: 0.85,
    rmse: 1250.50,
    mae: 980.25,
    mse: 1563750.25
  },
  model_params: {
    n_estimators: 200,
    max_depth: 20,
    min_samples_split: 5
  },
  training_time: 12.5,  // seconds
  timestamp: "2024-01-01T00:00:00.000Z",
  created_at: "2024-01-01T00:00:00.000Z",
  automl_enabled: false,  // NEW: Track if AutoML was used
  hyperparameters_tuned: []  // NEW: List of tuned parameters
});

// Create indexes for training_metadata
db.training_metadata.createIndex({ id: 1 }, { unique: true });
db.training_metadata.createIndex({ dataset_id: 1 });
db.training_metadata.createIndex({ workspace_id: 1 });  // NEW: For 30-day tracking
db.training_metadata.createIndex({ timestamp: -1 });
db.training_metadata.createIndex({ model_type: 1 });
db.training_metadata.createIndex({ 
  workspace_id: 1, 
  timestamp: -1 
});  // NEW: Composite for performance trends
```

#### 4. Saved States Collection

```javascript
db.saved_states.insertOne({
  id: "state-uuid",
  workspace_name: "Sales Forecasting Q4 2024",  // Optional workspace link
  dataset_id: "dataset-uuid",
  created_at: "2024-01-01T00:00:00.000Z",
  analysis_results: {
    // Full analysis results object
  }
});

// Create indexes for saved_states
db.saved_states.createIndex({ id: 1 }, { unique: true });
db.saved_states.createIndex({ dataset_id: 1 });
db.saved_states.createIndex({ workspace_name: 1 });
db.saved_states.createIndex({ created_at: -1 });
```

#### 5. Prediction Feedback Collection

```javascript
db.prediction_feedback.insertOne({
  id: "feedback-uuid",
  dataset_id: "dataset-uuid",
  model_type: "RandomForest",
  prediction_value: 15000,
  actual_value: 14800,
  feedback: "accurate",  // or "inaccurate"
  user_comment: "Prediction was close",
  created_at: "2024-01-01T00:00:00.000Z"
});

// Create indexes for prediction_feedback
db.prediction_feedback.createIndex({ id: 1 }, { unique: true });
db.prediction_feedback.createIndex({ dataset_id: 1 });
db.prediction_feedback.createIndex({ created_at: -1 });
```

---

### MongoDB Initialization Script

```javascript
// Run this in MongoDB shell or MongoDB Compass

use test_database;

// Create collections if they don't exist
db.createCollection("workspaces");
db.createCollection("datasets");
db.createCollection("training_metadata");
db.createCollection("saved_states");
db.createCollection("prediction_feedback");

// Create all indexes
print("Creating indexes for workspaces...");
db.workspaces.createIndex({ id: 1 }, { unique: true });
db.workspaces.createIndex({ created_at: -1 });
db.workspaces.createIndex({ name: 1 });

print("Creating indexes for datasets...");
db.datasets.createIndex({ id: 1 }, { unique: true });
db.datasets.createIndex({ workspace_id: 1 });
db.datasets.createIndex({ created_at: -1 });
db.datasets.createIndex({ name: 1 });

print("Creating indexes for training_metadata...");
db.training_metadata.createIndex({ id: 1 }, { unique: true });
db.training_metadata.createIndex({ dataset_id: 1 });
db.training_metadata.createIndex({ workspace_id: 1 });
db.training_metadata.createIndex({ timestamp: -1 });
db.training_metadata.createIndex({ model_type: 1 });
db.training_metadata.createIndex({ workspace_id: 1, timestamp: -1 });

print("Creating indexes for saved_states...");
db.saved_states.createIndex({ id: 1 }, { unique: true });
db.saved_states.createIndex({ dataset_id: 1 });
db.saved_states.createIndex({ workspace_name: 1 });
db.saved_states.createIndex({ created_at: -1 });

print("Creating indexes for prediction_feedback...");
db.prediction_feedback.createIndex({ id: 1 }, { unique: true });
db.prediction_feedback.createIndex({ dataset_id: 1 });
db.prediction_feedback.createIndex({ created_at: -1 });

print("✅ MongoDB database initialized successfully!");
```

---

## Oracle Setup

### Tables Overview

1. **WORKSPACES** - Organize datasets and track projects
2. **DATASETS** - Store dataset metadata with workspace references
3. **TRAINING_METADATA** - Track all training runs
4. **SAVED_STATES** - User analysis states
5. **PREDICTION_FEEDBACK** - User feedback
6. **DATASET_BLOBS** - Large file storage

---

### Oracle Table Creation Scripts

```sql
-- =====================================================
-- 1. WORKSPACES TABLE
-- =====================================================
CREATE TABLE WORKSPACES (
    ID VARCHAR2(255) PRIMARY KEY,
    NAME VARCHAR2(500) NOT NULL,
    DESCRIPTION CLOB,
    TAGS CLOB,  -- Store as JSON array string
    CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
    DATASET_COUNT NUMBER DEFAULT 0,
    TRAINING_COUNT NUMBER DEFAULT 0
);

CREATE INDEX idx_workspaces_created ON WORKSPACES(CREATED_AT DESC);
CREATE INDEX idx_workspaces_name ON WORKSPACES(NAME);

-- =====================================================
-- 2. DATASETS TABLE (Updated)
-- =====================================================
CREATE TABLE DATASETS (
    ID VARCHAR2(255) PRIMARY KEY,
    WORKSPACE_ID VARCHAR2(255),  -- NEW: Foreign key to WORKSPACES
    NAME VARCHAR2(500) NOT NULL,
    ROW_COUNT NUMBER,
    COLUMN_COUNT NUMBER,
    COLUMNS CLOB,  -- JSON array of column names
    DTYPES CLOB,  -- JSON object of column types
    DATA_PREVIEW CLOB,  -- JSON array of first 1000 rows
    CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
    FILE_SIZE NUMBER,
    SOURCE_TYPE VARCHAR2(50),
    STORAGE_TYPE VARCHAR2(50),
    GRIDFS_FILE_ID VARCHAR2(255),
    TRAINING_COUNT NUMBER DEFAULT 0,
    LAST_TRAINED_AT TIMESTAMP,
    CONSTRAINT fk_dataset_workspace FOREIGN KEY (WORKSPACE_ID) 
        REFERENCES WORKSPACES(ID) ON DELETE SET NULL
);

CREATE INDEX idx_datasets_created ON DATASETS(CREATED_AT DESC);
CREATE INDEX idx_datasets_workspace ON DATASETS(WORKSPACE_ID);  -- NEW
CREATE INDEX idx_datasets_name ON DATASETS(NAME);

-- =====================================================
-- 3. TRAINING_METADATA TABLE (Updated)
-- =====================================================
CREATE TABLE TRAINING_METADATA (
    ID VARCHAR2(255) PRIMARY KEY,
    DATASET_ID VARCHAR2(255) NOT NULL,
    WORKSPACE_ID VARCHAR2(255),  -- NEW: Direct workspace link
    MODEL_TYPE VARCHAR2(100),
    PROBLEM_TYPE VARCHAR2(50),
    TARGET_VARIABLE VARCHAR2(255),
    FEATURE_VARIABLES CLOB,  -- JSON array
    METRICS CLOB,  -- JSON object
    MODEL_PARAMS CLOB,  -- JSON object
    TRAINING_TIME NUMBER,
    TIMESTAMP TIMESTAMP DEFAULT SYSTIMESTAMP,
    CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
    AUTOML_ENABLED NUMBER(1) DEFAULT 0,  -- NEW: Boolean (0/1)
    HYPERPARAMETERS_TUNED CLOB,  -- NEW: JSON array
    CONSTRAINT fk_training_dataset FOREIGN KEY (DATASET_ID) 
        REFERENCES DATASETS(ID) ON DELETE CASCADE,
    CONSTRAINT fk_training_workspace FOREIGN KEY (WORKSPACE_ID) 
        REFERENCES WORKSPACES(ID) ON DELETE SET NULL
);

CREATE INDEX idx_training_dataset ON TRAINING_METADATA(DATASET_ID);
CREATE INDEX idx_training_workspace ON TRAINING_METADATA(WORKSPACE_ID);  -- NEW
CREATE INDEX idx_training_timestamp ON TRAINING_METADATA(TIMESTAMP DESC);
CREATE INDEX idx_training_model_type ON TRAINING_METADATA(MODEL_TYPE);
CREATE INDEX idx_training_workspace_time ON TRAINING_METADATA(WORKSPACE_ID, TIMESTAMP DESC);  -- NEW

-- =====================================================
-- 4. SAVED_STATES TABLE
-- =====================================================
CREATE TABLE SAVED_STATES (
    ID VARCHAR2(255) PRIMARY KEY,
    WORKSPACE_NAME VARCHAR2(500),
    DATASET_ID VARCHAR2(255),
    CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
    ANALYSIS_RESULTS CLOB,  -- JSON object
    CONSTRAINT fk_state_dataset FOREIGN KEY (DATASET_ID) 
        REFERENCES DATASETS(ID) ON DELETE CASCADE
);

CREATE INDEX idx_states_dataset ON SAVED_STATES(DATASET_ID);
CREATE INDEX idx_states_workspace ON SAVED_STATES(WORKSPACE_NAME);
CREATE INDEX idx_states_created ON SAVED_STATES(CREATED_AT DESC);

-- =====================================================
-- 5. PREDICTION_FEEDBACK TABLE
-- =====================================================
CREATE TABLE PREDICTION_FEEDBACK (
    ID VARCHAR2(255) PRIMARY KEY,
    DATASET_ID VARCHAR2(255),
    MODEL_TYPE VARCHAR2(100),
    PREDICTION_VALUE NUMBER,
    ACTUAL_VALUE NUMBER,
    FEEDBACK VARCHAR2(50),
    USER_COMMENT CLOB,
    CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT fk_feedback_dataset FOREIGN KEY (DATASET_ID) 
        REFERENCES DATASETS(ID) ON DELETE CASCADE
);

CREATE INDEX idx_feedback_dataset ON PREDICTION_FEEDBACK(DATASET_ID);
CREATE INDEX idx_feedback_created ON PREDICTION_FEEDBACK(CREATED_AT DESC);

-- =====================================================
-- 6. DATASET_BLOBS TABLE (For large file storage)
-- =====================================================
CREATE TABLE DATASET_BLOBS (
    ID VARCHAR2(255) PRIMARY KEY,
    DATASET_ID VARCHAR2(255) NOT NULL,
    FILENAME VARCHAR2(500),
    CONTENT_TYPE VARCHAR2(100),
    FILE_DATA BLOB,
    CREATED_AT TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT fk_blob_dataset FOREIGN KEY (DATASET_ID) 
        REFERENCES DATASETS(ID) ON DELETE CASCADE
);

CREATE INDEX idx_blobs_dataset ON DATASET_BLOBS(DATASET_ID);

-- =====================================================
-- Grant permissions (adjust user as needed)
-- =====================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON WORKSPACES TO testuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON DATASETS TO testuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON TRAINING_METADATA TO testuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON SAVED_STATES TO testuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON PREDICTION_FEEDBACK TO testuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON DATASET_BLOBS TO testuser;

COMMIT;
```

---

### Oracle Initialization Verification

```sql
-- Verify all tables were created
SELECT TABLE_NAME FROM USER_TABLES 
WHERE TABLE_NAME IN (
    'WORKSPACES', 
    'DATASETS', 
    'TRAINING_METADATA', 
    'SAVED_STATES', 
    'PREDICTION_FEEDBACK',
    'DATASET_BLOBS'
)
ORDER BY TABLE_NAME;

-- Check indexes
SELECT INDEX_NAME, TABLE_NAME 
FROM USER_INDEXES 
WHERE TABLE_NAME IN (
    'WORKSPACES', 
    'DATASETS', 
    'TRAINING_METADATA'
)
ORDER BY TABLE_NAME, INDEX_NAME;

-- Verify foreign key constraints
SELECT CONSTRAINT_NAME, TABLE_NAME, CONSTRAINT_TYPE, STATUS
FROM USER_CONSTRAINTS
WHERE CONSTRAINT_TYPE = 'R'  -- Foreign keys
AND TABLE_NAME IN ('DATASETS', 'TRAINING_METADATA', 'SAVED_STATES');
```

---

## Migration Scripts

### Migrating Existing Data to Include Workspace Support

#### MongoDB Migration

```javascript
// Run this if you have existing datasets without workspace_id

db.datasets.updateMany(
  { workspace_id: { $exists: false } },
  { $set: { workspace_id: null } }
);

db.training_metadata.updateMany(
  { workspace_id: { $exists: false } },
  { $set: { workspace_id: null, automl_enabled: false, hyperparameters_tuned: [] } }
);

print("✅ Migration complete: Added workspace fields to existing records");
```

#### Oracle Migration

```sql
-- Add workspace_id column if it doesn't exist (for existing installations)

-- For DATASETS table
BEGIN
    EXECUTE IMMEDIATE 'ALTER TABLE DATASETS ADD (WORKSPACE_ID VARCHAR2(255))';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE = -1430 THEN  -- Column already exists
            NULL;
        ELSE
            RAISE;
        END IF;
END;
/

-- For TRAINING_METADATA table
BEGIN
    EXECUTE IMMEDIATE 'ALTER TABLE TRAINING_METADATA ADD (
        WORKSPACE_ID VARCHAR2(255),
        AUTOML_ENABLED NUMBER(1) DEFAULT 0,
        HYPERPARAMETERS_TUNED CLOB
    )';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE = -1430 THEN
            NULL;
        ELSE
            RAISE;
        END IF;
END;
/

-- Create indexes for new columns
CREATE INDEX idx_datasets_workspace ON DATASETS(WORKSPACE_ID);
CREATE INDEX idx_training_workspace ON TRAINING_METADATA(WORKSPACE_ID);
CREATE INDEX idx_training_workspace_time ON TRAINING_METADATA(WORKSPACE_ID, TIMESTAMP DESC);

COMMIT;

DBMS_OUTPUT.PUT_LINE('✅ Migration complete: Added workspace support');
```

---

## Key Schema Changes Summary

### New Fields Added:

**Datasets:**
- `workspace_id` (VARCHAR/String) - Links dataset to workspace

**Training Metadata:**
- `workspace_id` (VARCHAR/String) - Direct link for 30-day tracking
- `automl_enabled` (Boolean/Number) - Track if AutoML was used
- `hyperparameters_tuned` (JSON/CLOB) - List of optimized parameters

**New Table:**
- `WORKSPACES` - Complete workspace management

### New Indexes for Performance:

- `idx_datasets_workspace` - Fast workspace→datasets queries
- `idx_training_workspace` - Fast workspace→training history
- `idx_training_workspace_time` - Optimized 30-day trend queries

---

## Usage Examples

### Create Workspace and Link Dataset (MongoDB)

```javascript
// 1. Create workspace
const workspaceId = "ws-" + new Date().getTime();
db.workspaces.insertOne({
  id: workspaceId,
  name: "Q4 Sales Analysis",
  description: "Quarterly sales forecasting",
  tags: ["sales", "Q4"],
  created_at: new Date().toISOString(),
  dataset_count: 0,
  training_count: 0
});

// 2. Create dataset linked to workspace
db.datasets.insertOne({
  id: "ds-" + new Date().getTime(),
  workspace_id: workspaceId,  // Link here!
  name: "sales_q4.csv",
  // ... other fields
});

// 3. Track training with workspace
db.training_metadata.insertOne({
  id: "train-" + new Date().getTime(),
  dataset_id: "ds-123",
  workspace_id: workspaceId,  // Direct link for fast queries
  model_type: "RandomForest",
  // ... other fields
});
```

### Query 30-Day Performance Trends (MongoDB)

```javascript
// Get all training runs in workspace from last 30 days
const thirtyDaysAgo = new Date();
thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

db.training_metadata.find({
  workspace_id: "ws-123",
  timestamp: { $gte: thirtyDaysAgo.toISOString() }
}).sort({ timestamp: -1 });

// Get best model by average performance
db.training_metadata.aggregate([
  { $match: { workspace_id: "ws-123" } },
  { $group: {
      _id: "$model_type",
      avg_r2: { $avg: "$metrics.r2_score" },
      count: { $sum: 1 }
  }},
  { $sort: { avg_r2: -1 } },
  { $limit: 1 }
]);
```

---

## Testing the Setup

### MongoDB Test

```bash
mongo test_database --eval "
  db.workspaces.insertOne({id: 'test-ws', name: 'Test Workspace'});
  db.datasets.insertOne({id: 'test-ds', workspace_id: 'test-ws', name: 'test.csv'});
  print('✅ MongoDB test successful');
  db.workspaces.deleteOne({id: 'test-ws'});
  db.datasets.deleteOne({id: 'test-ds'});
"
```

### Oracle Test

```sql
-- Test workspace and dataset creation
INSERT INTO WORKSPACES (ID, NAME) VALUES ('test-ws', 'Test Workspace');
INSERT INTO DATASETS (ID, WORKSPACE_ID, NAME) VALUES ('test-ds', 'test-ws', 'test.csv');

-- Verify
SELECT * FROM DATASETS WHERE WORKSPACE_ID = 'test-ws';

-- Cleanup
DELETE FROM DATASETS WHERE ID = 'test-ds';
DELETE FROM WORKSPACES WHERE ID = 'test-ws';
COMMIT;
```

---

## Backup and Restore

### MongoDB Backup

```bash
mongodump --db test_database --out /backup/mongodb/
```

### Oracle Backup

```bash
exp testuser/DbPasswordTest@ORCL file=promise_ai_backup.dmp full=y
```

---

**End of DB Scripts Document**
