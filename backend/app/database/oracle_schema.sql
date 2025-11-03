-- =====================================================
-- PROMISE AI - Oracle 23 Database Schema
-- Supports all features: Datasets, Workspaces, Feedback
-- Uses JSON columns for flexibility
-- =====================================================

-- Drop existing tables (for fresh install)
DROP TABLE IF EXISTS prediction_feedback CASCADE CONSTRAINTS;
DROP TABLE IF EXISTS workspace_states CASCADE CONSTRAINTS;
DROP TABLE IF EXISTS file_storage CASCADE CONSTRAINTS;
DROP TABLE IF EXISTS datasets CASCADE CONSTRAINTS;
DROP SEQUENCE IF EXISTS file_storage_seq;

-- =====================================================
-- 1. DATASETS Table
-- =====================================================
CREATE TABLE datasets (
    id VARCHAR2(36) PRIMARY KEY,
    name VARCHAR2(500) NOT NULL,
    source VARCHAR2(50) DEFAULT 'upload',
    row_count NUMBER(12) DEFAULT 0,
    column_count NUMBER(6) DEFAULT 0,
    
    -- JSON columns for flexible schema (Oracle 23 native JSON)
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
    
    -- Indexes
    CONSTRAINT chk_storage_type CHECK (storage_type IN ('direct', 'blob'))
);

CREATE INDEX idx_datasets_created ON datasets(created_at DESC);
CREATE INDEX idx_datasets_name ON datasets(name);
CREATE INDEX idx_datasets_file_id ON datasets(file_id);

-- =====================================================
-- 2. FILE_STORAGE Table (Replaces GridFS)
-- =====================================================
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

CREATE INDEX idx_file_storage_filename ON file_storage(filename);
CREATE INDEX idx_file_storage_created ON file_storage(created_at DESC);

-- =====================================================
-- 3. WORKSPACE_STATES Table
-- =====================================================
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

CREATE INDEX idx_workspace_dataset ON workspace_states(dataset_id);
CREATE INDEX idx_workspace_name ON workspace_states(state_name);
CREATE INDEX idx_workspace_created ON workspace_states(created_at DESC);

-- =====================================================
-- 4. PREDICTION_FEEDBACK Table
-- =====================================================
CREATE TABLE prediction_feedback (
    id VARCHAR2(36) PRIMARY KEY,
    prediction_id VARCHAR2(36) UNIQUE NOT NULL,
    dataset_id VARCHAR2(36) NOT NULL,
    model_name VARCHAR2(200) NOT NULL,
    
    is_correct CHAR(1) NOT NULL,
    prediction VARCHAR2(500),
    actual_outcome VARCHAR2(500),
    comment CLOB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_feedback_dataset FOREIGN KEY (dataset_id) 
        REFERENCES datasets(id) ON DELETE CASCADE,
    CONSTRAINT chk_is_correct CHECK (is_correct IN ('Y', 'N'))
);

CREATE INDEX idx_feedback_prediction ON prediction_feedback(prediction_id);
CREATE INDEX idx_feedback_dataset_model ON prediction_feedback(dataset_id, model_name);
CREATE INDEX idx_feedback_created ON prediction_feedback(created_at DESC);

-- =====================================================
-- 5. JSON SEARCH INDEXES (Oracle 23 Feature)
-- =====================================================

-- Enable JSON search on columns_json
CREATE SEARCH INDEX idx_datasets_columns_json_search 
    ON datasets(columns_json) 
    FOR JSON;

-- Enable JSON search on dtypes_json
CREATE SEARCH INDEX idx_datasets_dtypes_json_search 
    ON datasets(dtypes_json) 
    FOR JSON;

-- =====================================================
-- 6. STATISTICS & COMMENTS
-- =====================================================

-- Gather statistics for optimizer
BEGIN
    DBMS_STATS.GATHER_TABLE_STATS(USER, 'DATASETS');
    DBMS_STATS.GATHER_TABLE_STATS(USER, 'FILE_STORAGE');
    DBMS_STATS.GATHER_TABLE_STATS(USER, 'WORKSPACE_STATES');
    DBMS_STATS.GATHER_TABLE_STATS(USER, 'PREDICTION_FEEDBACK');
END;
/

-- Add table comments
COMMENT ON TABLE datasets IS 'Stores dataset metadata and references to file storage';
COMMENT ON TABLE file_storage IS 'Stores large files (datasets > 1MB, workspaces > 2MB) as BLOBs';
COMMENT ON TABLE workspace_states IS 'Stores saved analysis workspaces with results and chat history';
COMMENT ON TABLE prediction_feedback IS 'Stores user feedback on model predictions for active learning';

-- Add column comments
COMMENT ON COLUMN datasets.columns_json IS 'JSON array of column names';
COMMENT ON COLUMN datasets.dtypes_json IS 'JSON object mapping column names to data types';
COMMENT ON COLUMN datasets.data_preview_json IS 'JSON array of first 5 rows';
COMMENT ON COLUMN file_storage.metadata_json IS 'JSON metadata including type, compression info, etc.';

-- =====================================================
-- 7. SAMPLE QUERIES (for testing)
-- =====================================================

-- Query datasets with JSON extraction
-- SELECT id, name, 
--        JSON_VALUE(columns_json, '$[0]') as first_column,
--        JSON_VALUE(dtypes_json, '$.col1') as col1_dtype
-- FROM datasets;

-- Query workspaces for a dataset
-- SELECT id, state_name, created_at, size_bytes
-- FROM workspace_states
-- WHERE dataset_id = 'some-uuid'
-- ORDER BY created_at DESC;

-- Get feedback statistics
-- SELECT 
--     model_name,
--     COUNT(*) as total_feedback,
--     SUM(CASE WHEN is_correct = 'Y' THEN 1 ELSE 0 END) as correct_count,
--     ROUND(SUM(CASE WHEN is_correct = 'Y' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as accuracy_pct
-- FROM prediction_feedback
-- WHERE dataset_id = 'some-uuid'
-- GROUP BY model_name;

-- =====================================================
-- SCHEMA CREATION COMPLETE
-- =====================================================

SELECT 'Oracle 23 schema created successfully for PROMISE AI' as status FROM dual;
