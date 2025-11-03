# PROMISE AI - Database Schema Documentation

Complete MongoDB database structure for PROMISE AI.

**Database Name**: `autopredict_db` (configurable via `DB_NAME` env variable)

## 📋 Table of Contents

- [Collections Overview](#collections-overview)
- [Collection Schemas](#collection-schemas)
- [Indexes](#indexes)
- [GridFS Collections](#gridfs-collections)
- [Data Types Reference](#data-types-reference)

## 🗂 Collections Overview

| Collection Name | Purpose | Typical Size | Indexed Fields |
|----------------|---------|--------------|----------------|
| `datasets` | Store dataset metadata | ~1KB per doc | id, created_at, name |
| `saved_states` | Store workspace/analysis states | 2-10MB per doc | id, dataset_id, state_name |
| `prediction_feedback` | Store user feedback on predictions | ~500B per doc | prediction_id, dataset_id |
| `fs.files` | GridFS file metadata | ~500B per doc | metadata.dataset_id |
| `fs.chunks` | GridFS file chunks | 255KB per chunk | files_id |

## 📊 Collection Schemas

### 1. datasets Collection

**Purpose**: Stores metadata about uploaded datasets and query results

**Schema**:

```javascript
{
  "_id": ObjectId,              // MongoDB internal ID (not used in API)
  "id": String,                 // UUID - Primary identifier
  "name": String,               // Dataset name (e.g., "sales_data.csv")
  "source": String,             // "upload" | "database_query"
  "row_count": Integer,         // Number of rows in dataset
  "column_count": Integer,      // Number of columns
  "columns": Array<String>,     // List of column names
  "dtypes": Object,             // Column data types {"col1": "int64", "col2": "float64"}
  "storage_type": String,       // "gridfs" | "direct"
  "gridfs_file_id": String,     // GridFS file ID (if storage_type="gridfs")
  "data_preview": Array<Object>, // First 5 rows preview
  "created_at": String,         // ISO 8601 timestamp
  "training_count": Integer,    // Number of times trained (default: 0)
  "last_trained_at": String     // ISO 8601 timestamp of last training
}
```

**Field Details**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | String (UUID) | Yes | Unique dataset identifier | "f9bdac89-8e44-44a8-9c2e-123456789abc" |
| `name` | String | Yes | User-friendly dataset name | "sales_data.csv" |
| `source` | String | Yes | Origin of dataset | "upload" or "database_query" |
| `row_count` | Integer | Yes | Total number of rows | 5000 |
| `column_count` | Integer | Yes | Total number of columns | 10 |
| `columns` | Array | Yes | Column names | ["date", "sales", "region"] |
| `dtypes` | Object | Yes | Data types per column | {"sales": "float64", "date": "object"} |
| `storage_type` | String | Yes | Where data is stored | "gridfs" or "direct" |
| `gridfs_file_id` | String | Conditional | GridFS file reference | "507f1f77bcf86cd799439011" |
| `data_preview` | Array | Yes | Sample rows | [{"date": "2025-01-01", "sales": 1000}] |
| `created_at` | String (ISO) | Yes | Creation timestamp | "2025-01-01T12:00:00.000Z" |
| `training_count` | Integer | No | Training iterations | 3 |
| `last_trained_at` | String (ISO) | No | Last training time | "2025-01-02T15:30:00.000Z" |

**Example Document**:

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "id": "f9bdac89-8e44-44a8-9c2e-a6f86993c92e",
  "name": "sales_data.csv",
  "source": "upload",
  "row_count": 5000,
  "column_count": 10,
  "columns": ["date", "sales", "region", "product", "quantity"],
  "dtypes": {
    "date": "object",
    "sales": "float64",
    "region": "object",
    "product": "object",
    "quantity": "int64"
  },
  "storage_type": "gridfs",
  "gridfs_file_id": "507f1f77bcf86cd799439012",
  "data_preview": [
    {"date": "2025-01-01", "sales": 1000, "region": "North", "product": "A", "quantity": 50},
    {"date": "2025-01-02", "sales": 1200, "region": "South", "product": "B", "quantity": 60}
  ],
  "created_at": "2025-01-01T12:00:00.000Z",
  "training_count": 3,
  "last_trained_at": "2025-01-02T15:30:00.000Z"
}
```

**Storage Logic**:
- Datasets < 1MB: Stored directly in `datasets` collection
- Datasets >= 1MB: Stored in GridFS, metadata in `datasets`

---

### 2. saved_states Collection

**Purpose**: Stores saved analysis workspaces with results and chat history

**Schema**:

```javascript
{
  "_id": ObjectId,              // MongoDB internal ID
  "id": String,                 // UUID - Workspace identifier
  "dataset_id": String,         // Foreign key to datasets.id
  "state_name": String,         // User-defined workspace name
  "storage_type": String,       // "direct" | "gridfs"
  "analysis_data": Object,      // Analysis results (if storage_type="direct")
  "chat_history": Array<Object>, // Chat messages (if storage_type="direct")
  "gridfs_file_id": String,     // GridFS file ID (if storage_type="gridfs")
  "size_bytes": Integer,        // Uncompressed size in bytes
  "compressed_size": Integer,   // Compressed size (if applicable)
  "created_at": String,         // ISO 8601 timestamp
  "updated_at": String          // ISO 8601 timestamp
}
```

**Field Details**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | String (UUID) | Yes | Unique workspace ID | "abc-def-123" |
| `dataset_id` | String (UUID) | Yes | Reference to dataset | "f9bdac89-8e44-44a8" |
| `state_name` | String | Yes | Workspace name | "Sales Analysis - Q1 2025" |
| `storage_type` | String | Yes | Storage method | "direct" or "gridfs" |
| `analysis_data` | Object | Conditional | ML results | {ml_models: [], charts: []} |
| `chat_history` | Array | Conditional | Chat messages | [{role: "user", content: "..."}] |
| `gridfs_file_id` | String | Conditional | GridFS reference | "507f..." |
| `size_bytes` | Integer | Yes | Original size | 5242880 (5MB) |
| `compressed_size` | Integer | No | Compressed size | 1048576 (1MB) |
| `created_at` | String (ISO) | Yes | Creation time | "2025-01-01T12:00:00Z" |
| `updated_at` | String (ISO) | Yes | Last update | "2025-01-02T15:30:00Z" |

**analysis_data Object Structure**:

```javascript
{
  "ml_models": [
    {
      "model_name": String,
      "r2_score": Float,
      "rmse": Float,
      "accuracy": Float,
      "f1_score": Float,
      "feature_importance": Array<Object>
    }
  ],
  "auto_charts": [
    {
      "chart_type": String,
      "title": String,
      "description": String
    }
  ],
  "ai_insights": Array<Object>,
  "business_recommendations": Array<Object>,
  "correlations": Object,
  "profile": Object
}
```

**Example Document**:

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439013"),
  "id": "workspace-uuid-123",
  "dataset_id": "f9bdac89-8e44-44a8-9c2e-a6f86993c92e",
  "state_name": "Sales Analysis - Q1 2025",
  "storage_type": "gridfs",
  "gridfs_file_id": "507f1f77bcf86cd799439014",
  "size_bytes": 5242880,
  "compressed_size": 1048576,
  "created_at": "2025-01-01T12:00:00.000Z",
  "updated_at": "2025-01-01T12:05:00.000Z"
}
```

**Optimization**:
- Workspaces < 2MB: Stored directly in collection
- Workspaces >= 2MB: GZIP compressed and stored in GridFS
- Only top 10 feature importance values stored
- Only first 5 charts stored
- Last 50 chat messages stored

---

### 3. prediction_feedback Collection

**Purpose**: Stores user feedback on model predictions for active learning

**Schema**:

```javascript
{
  "_id": ObjectId,              // MongoDB internal ID
  "prediction_id": String,      // UUID - Unique prediction identifier
  "dataset_id": String,         // Foreign key to datasets.id
  "model_name": String,         // Name of the model
  "is_correct": Boolean,        // Whether prediction was correct
  "prediction": String,         // Predicted value
  "actual_outcome": String,     // Actual value (optional)
  "comment": String,            // User comment (optional)
  "timestamp": String           // ISO 8601 timestamp
}
```

**Field Details**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `prediction_id` | String (UUID) | Yes | Unique prediction ID | "pred-uuid-123" |
| `dataset_id` | String (UUID) | Yes | Dataset reference | "f9bdac89-8e44..." |
| `model_name` | String | Yes | Model that made prediction | "Random Forest" |
| `is_correct` | Boolean | Yes | Feedback result | true or false |
| `prediction` | String | Yes | Predicted value | "1500" |
| `actual_outcome` | String | No | Real value | "1480" |
| `comment` | String | No | User notes | "Very close estimate" |
| `timestamp` | String (ISO) | Yes | Feedback time | "2025-01-01T12:00:00Z" |

**Example Document**:

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439015"),
  "prediction_id": "pred-abc-123",
  "dataset_id": "f9bdac89-8e44-44a8-9c2e-a6f86993c92e",
  "model_name": "Random Forest",
  "is_correct": true,
  "prediction": "1500",
  "actual_outcome": "1480",
  "comment": "Prediction was within 2% margin",
  "timestamp": "2025-01-01T12:00:00.000Z"
}
```

---

## 🗂 GridFS Collections

GridFS is used for storing large files (datasets > 1MB, workspaces > 2MB).

### fs.files Collection

**Purpose**: Stores metadata for GridFS files

**Schema**:

```javascript
{
  "_id": ObjectId,              // GridFS file ID
  "length": Integer,            // File size in bytes
  "chunkSize": Integer,         // Chunk size (255KB default)
  "uploadDate": Date,           // Upload timestamp
  "filename": String,           // File name
  "metadata": {                 // Custom metadata
    "type": String,             // "dataset" | "workspace_state"
    "dataset_id": String,       // Reference to dataset
    "state_id": String,         // Reference to workspace (if type="workspace_state")
    "state_name": String,       // Workspace name
    "compressed": Boolean,      // Is file compressed?
    "original_size": Integer,   // Original size before compression
    "compressed_size": Integer  // Size after compression
  }
}
```

**Example Document**:

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439016"),
  "length": 1048576,
  "chunkSize": 261120,
  "uploadDate": ISODate("2025-01-01T12:00:00.000Z"),
  "filename": "workspace_abc-123.json.gz",
  "metadata": {
    "type": "workspace_state",
    "dataset_id": "f9bdac89-8e44-44a8",
    "state_id": "abc-123",
    "state_name": "Sales Analysis - Q1",
    "compressed": true,
    "original_size": 5242880,
    "compressed_size": 1048576
  }
}
```

### fs.chunks Collection

**Purpose**: Stores actual file data in 255KB chunks

**Schema**:

```javascript
{
  "_id": ObjectId,              // Chunk ID
  "files_id": ObjectId,         // Reference to fs.files._id
  "n": Integer,                 // Chunk sequence number (0, 1, 2...)
  "data": Binary                // Binary data (max 255KB)
}
```

**Example Document**:

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439017"),
  "files_id": ObjectId("507f1f77bcf86cd799439016"),
  "n": 0,
  "data": Binary("...")
}
```

---

## 🔍 Indexes

MongoDB indexes for optimal query performance:

### datasets Collection Indexes

```javascript
// Primary key (unique)
db.datasets.createIndex({ "id": 1 }, { unique: true })

// Created timestamp for sorting
db.datasets.createIndex({ "created_at": 1 })

// Name + timestamp for searches
db.datasets.createIndex({ "name": 1, "created_at": -1 })
```

### saved_states Collection Indexes

```javascript
// Primary key (unique)
db.saved_states.createIndex({ "id": 1 }, { unique: true })

// Dataset reference for lookups
db.saved_states.createIndex({ "dataset_id": 1 })

// Dataset + timestamp compound index
db.saved_states.createIndex({ "dataset_id": 1, "created_at": -1 })

// Workspace name for searches
db.saved_states.createIndex({ "state_name": 1 })

// Storage type for filtering
db.saved_states.createIndex({ "storage_type": 1 })
```

### prediction_feedback Collection Indexes

```javascript
// Primary key (unique)
db.prediction_feedback.createIndex({ "prediction_id": 1 }, { unique: true })

// Dataset + model compound index
db.prediction_feedback.createIndex({ "dataset_id": 1, "model_name": 1 })

// Timestamp for sorting
db.prediction_feedback.createIndex({ "timestamp": 1 })
```

### GridFS Collection Indexes

```javascript
// GridFS metadata indexes
db.fs.files.createIndex({ "metadata.dataset_id": 1 })
db.fs.files.createIndex({ "metadata.type": 1 })

// Default GridFS indexes (auto-created)
db.fs.chunks.createIndex({ "files_id": 1, "n": 1 })
```

**Create All Indexes**:

```bash
cd backend
python create_indexes.py
```

---

## 📊 Data Types Reference

### Python → MongoDB Type Mapping

| Python Type | MongoDB Type | Example |
|-------------|--------------|---------|
| str | String | "sales_data.csv" |
| int | Integer (Int32/Int64) | 5000 |
| float | Double | 123.45 |
| bool | Boolean | true |
| dict | Object | {"key": "value"} |
| list | Array | [1, 2, 3] |
| datetime | String (ISO 8601) | "2025-01-01T12:00:00Z" |
| uuid.UUID | String | "f9bdac89-8e44..." |
| bytes | Binary | Binary("...") |

### pandas dtype → MongoDB Type Mapping

| pandas dtype | MongoDB Type | Notes |
|--------------|--------------|-------|
| int64 | String ("int64") | Stored as string in dtypes field |
| float64 | String ("float64") | Stored as string in dtypes field |
| object | String ("object") | Usually strings or mixed |
| datetime64 | String ("datetime64") | Date/time columns |
| bool | String ("bool") | Boolean columns |
| category | String ("category") | Categorical data |

---

## 💾 Storage Optimization

### Size Limits

| Item | Threshold | Action |
|------|-----------|--------|
| Small dataset | < 1MB | Store directly in `datasets` |
| Large dataset | >= 1MB | Store in GridFS |
| Small workspace | < 2MB | Store directly in `saved_states` |
| Large workspace | >= 2MB | GZIP compress + GridFS |

### Compression Ratios

Typical compression achieved:

- **Workspaces**: 70-90% size reduction
- **Datasets**: Not compressed (already in binary format)
- **JSON data**: 60-80% compression

### Data Retention

- **Datasets**: No automatic deletion
- **Workspaces**: No automatic deletion
- **Feedback**: No automatic deletion
- **GridFS**: Orphaned files cleaned on dataset deletion

---

## 🔗 Relationships

### Foreign Key Relationships

```
datasets (id)
    ↓
    ├── saved_states (dataset_id)
    ├── prediction_feedback (dataset_id)
    └── fs.files (metadata.dataset_id)

saved_states (id)
    ↓
    └── fs.files (metadata.state_id)

fs.files (_id)
    ↓
    └── fs.chunks (files_id)
```

### Cascade Deletion

When a dataset is deleted:
1. All `saved_states` for that dataset
2. All `prediction_feedback` for that dataset
3. All GridFS files with `metadata.dataset_id` matching
4. All chunks for deleted GridFS files

---

## 🔒 Data Integrity

### Constraints

1. **Unique Constraints**:
   - `datasets.id` (UUID)
   - `saved_states.id` (UUID)
   - `prediction_feedback.prediction_id` (UUID)

2. **Required Fields**: See individual collection schemas

3. **Referential Integrity**: Application-level (MongoDB doesn't enforce FK)

### Validation

MongoDB schema validation is not enforced (application handles validation).

---

## 📈 Performance Considerations

### Query Performance

- All primary keys indexed (< 10ms lookup)
- Compound indexes for common queries
- GridFS optimized for large files

### Write Performance

- Async writes with Motor driver
- GridFS streaming for large uploads
- Bulk operations where applicable

### Storage Efficiency

- GridFS avoids 16MB document limit
- GZIP compression for large workspaces
- Efficient binary storage

---

## 🛠 Maintenance

### Backup

```bash
# Backup entire database
mongodump --db autopredict_db --out /backup/

# Restore database
mongorestore --db autopredict_db /backup/autopredict_db/
```

### Cleanup

```bash
# Remove all data
cd backend
python clear_metadata.py

# Recreate indexes
python create_indexes.py
```

### Monitor Size

```bash
# Check database size
mongosh
use autopredict_db
db.stats()

# Check collection sizes
db.datasets.stats()
db.saved_states.stats()
db.fs.files.stats()
db.fs.chunks.stats()
```

---

## 🔗 Related Documentation

- [API Documentation](API_DOCUMENTATION.md) - How APIs interact with database
- [Setup Guide](SETUP_GUIDE.md) - MongoDB installation
- [MCP Server](MCP_SERVER.md) - External access to data

---

**Database Version**: MongoDB 5.0+
**Schema Version**: 1.0.0
**Last Updated**: 2025-01-03
