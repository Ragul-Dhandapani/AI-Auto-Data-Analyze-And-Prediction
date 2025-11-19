"""
PROMISE AI - Prediction MCP Tool
High-Performance Data Loading & Prediction with Multi-Threading

This MCP tool can:
1. Load data from files (CSV, Excel, Parquet) or databases (Oracle, PostgreSQL, MySQL, MongoDB)
2. Handle GB-scale data with multi-threading (target: 3-5 minutes for GB datasets)
3. Make predictions using trained ML models
4. Return structured predictions with confidence scores

Performance Features:
- Multi-threaded file reading (up to 8 threads)
- Chunked database queries (batch size: 100K rows)
- Memory-efficient processing (process in chunks)
- Progress tracking
- Automatic data type inference
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
import logging

# Database connectors
import cx_Oracle
import pymongo
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


class PredictionMCP:
    """
    High-Performance Prediction MCP Tool
    
    Usage:
        mcp = PredictionMCP()
        
        # Load from file
        result = mcp.predict_from_file(
            file_path="/path/to/data.csv",
            model_path="/path/to/model.pkl",
            num_threads=8
        )
        
        # Load from database
        result = mcp.predict_from_database(
            db_type="oracle",
            connection_config={...},
            table_name="predictions_table",
            model_path="/path/to/model.pkl"
        )
    """
    
    def __init__(self, chunk_size: int = 100000):
        """
        Initialize Prediction MCP
        
        Args:
            chunk_size: Number of rows to process at once (default: 100K)
        """
        self.chunk_size = chunk_size
        self.supported_db_types = ['oracle', 'postgresql', 'mysql', 'mongodb']
        self.supported_file_types = ['.csv', '.xlsx', '.xls', '.parquet', '.json']
    
    def predict_from_file(
        self,
        file_path: str,
        model_path: str,
        num_threads: int = 8,
        output_path: Optional[str] = None,
        return_confidence: bool = True
    ) -> Dict[str, Any]:
        """
        Load data from file and make predictions (Multi-threaded)
        
        Args:
            file_path: Path to input file (CSV, Excel, Parquet)
            model_path: Path to trained model (.pkl, .joblib)
            num_threads: Number of threads for parallel processing
            output_path: Optional path to save predictions
            return_confidence: Whether to return confidence scores
        
        Returns:
            {
                'predictions': [...],
                'confidence_scores': [...],
                'processing_time_seconds': float,
                'rows_processed': int,
                'throughput_rows_per_second': float
            }
        """
        start_time = time.time()
        
        logger.info(f"🚀 Starting prediction from file: {file_path}")
        logger.info(f"📊 Using {num_threads} threads for processing")
        
        # Load model
        model, feature_names = self._load_model(model_path)
        
        # Determine file type
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in self.supported_file_types:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Load data with multi-threading
        df = self._load_file_multithreaded(file_path, file_ext, num_threads)
        
        logger.info(f"✅ Loaded {len(df):,} rows in {time.time() - start_time:.2f}s")
        
        # Make predictions
        predictions, confidence_scores = self._make_predictions(
            df, model, feature_names, return_confidence
        )
        
        # Calculate metrics
        processing_time = time.time() - start_time
        throughput = len(df) / processing_time
        
        logger.info(f"✅ Predictions complete: {len(predictions):,} rows in {processing_time:.2f}s")
        logger.info(f"📈 Throughput: {throughput:,.0f} rows/second")
        
        # Save predictions if output path provided
        if output_path:
            self._save_predictions(df, predictions, confidence_scores, output_path)
        
        return {
            'predictions': predictions.tolist() if hasattr(predictions, 'tolist') else predictions,
            'confidence_scores': confidence_scores.tolist() if confidence_scores is not None else None,
            'processing_time_seconds': processing_time,
            'rows_processed': len(df),
            'throughput_rows_per_second': throughput,
            'model_features': feature_names,
            'timestamp': datetime.now().isoformat()
        }
    
    def predict_from_database(
        self,
        db_type: str,
        connection_config: Dict[str, str],
        table_name: Optional[str] = None,
        query: Optional[str] = None,
        model_path: str = None,
        batch_size: int = 100000,
        output_table: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load data from database and make predictions (Chunked for large tables)
        
        Args:
            db_type: Database type ('oracle', 'postgresql', 'mysql', 'mongodb')
            connection_config: Database connection parameters
            table_name: Table to load (if not using custom query)
            query: Custom SQL query (optional)
            model_path: Path to trained model
            batch_size: Rows to load per batch
            output_table: Optional table to save predictions
        
        Returns:
            {
                'predictions': [...],
                'processing_time_seconds': float,
                'rows_processed': int,
                'batches_processed': int
            }
        """
        start_time = time.time()
        
        logger.info(f"🚀 Starting prediction from {db_type} database")
        logger.info(f"📊 Batch size: {batch_size:,} rows")
        
        # Load model
        model, feature_names = self._load_model(model_path)
        
        # Connect to database
        connection = self._connect_database(db_type, connection_config)
        
        # Load data in chunks
        all_predictions = []
        all_confidence = []
        batch_count = 0
        total_rows = 0
        
        for chunk_df in self._load_database_chunks(
            connection, db_type, table_name, query, batch_size
        ):
            # Make predictions on chunk
            predictions, confidence_scores = self._make_predictions(
                chunk_df, model, feature_names, return_confidence=True
            )
            
            all_predictions.extend(predictions)
            if confidence_scores is not None:
                all_confidence.extend(confidence_scores)
            
            batch_count += 1
            total_rows += len(chunk_df)
            
            logger.info(f"✅ Batch {batch_count}: Processed {len(chunk_df):,} rows (Total: {total_rows:,})")
        
        processing_time = time.time() - start_time
        throughput = total_rows / processing_time if processing_time > 0 else 0
        
        logger.info(f"✅ All predictions complete: {total_rows:,} rows in {processing_time:.2f}s")
        logger.info(f"📈 Throughput: {throughput:,.0f} rows/second")
        
        # Close connection
        self._close_database_connection(connection, db_type)
        
        return {
            'predictions': all_predictions,
            'confidence_scores': all_confidence if all_confidence else None,
            'processing_time_seconds': processing_time,
            'rows_processed': total_rows,
            'batches_processed': batch_count,
            'throughput_rows_per_second': throughput,
            'model_features': feature_names,
            'timestamp': datetime.now().isoformat()
        }
    
    def _load_model(self, model_path: str):
        """Load trained ML model"""
        try:
            model = joblib.load(model_path)
            
            # Extract feature names if available
            feature_names = None
            if hasattr(model, 'feature_names_in_'):
                feature_names = model.feature_names_in_.tolist()
            elif hasattr(model, 'feature_names'):
                feature_names = model.feature_names
            
            logger.info(f"✅ Model loaded from {model_path}")
            return model, feature_names
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise
    
    def _load_file_multithreaded(
        self, file_path: str, file_ext: str, num_threads: int
    ) -> pd.DataFrame:
        """
        Load file with multi-threading for large files
        
        Strategy:
        - For CSV: Split file into chunks, read in parallel
        - For Excel/Parquet: Use pandas with engine optimizations
        """
        if file_ext == '.csv':
            return self._load_csv_parallel(file_path, num_threads)
        elif file_ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path, engine='openpyxl')
        elif file_ext == '.parquet':
            return pd.read_parquet(file_path, engine='pyarrow')
        elif file_ext == '.json':
            return pd.read_json(file_path, lines=True)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def _load_csv_parallel(self, file_path: str, num_threads: int) -> pd.DataFrame:
        """
        Load large CSV file in parallel using ThreadPoolExecutor
        
        Strategy:
        1. Count total rows
        2. Split into N chunks (based on num_threads)
        3. Read each chunk in parallel
        4. Concatenate results
        """
        # First, get row count (fast scan)
        row_count = sum(1 for _ in open(file_path)) - 1  # Subtract header
        
        chunk_size = max(self.chunk_size, row_count // num_threads)
        
        logger.info(f"📊 File has {row_count:,} rows, splitting into chunks of {chunk_size:,}")
        
        # Read in chunks using ThreadPoolExecutor
        chunks = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            
            for skip_rows in range(0, row_count, chunk_size):
                nrows = min(chunk_size, row_count - skip_rows)
                future = executor.submit(
                    pd.read_csv,
                    file_path,
                    skiprows=range(1, skip_rows + 1) if skip_rows > 0 else None,
                    nrows=nrows
                )
                futures.append(future)
            
            # Collect results
            for i, future in enumerate(as_completed(futures)):
                chunk_df = future.result()
                chunks.append(chunk_df)
                logger.info(f"✅ Chunk {i+1}/{len(futures)} loaded ({len(chunk_df):,} rows)")
        
        # Concatenate all chunks
        df = pd.concat(chunks, ignore_index=True)
        logger.info(f"✅ All chunks merged: {len(df):,} total rows")
        
        return df
    
    def _connect_database(self, db_type: str, config: Dict[str, str]):
        """Connect to database"""
        if db_type == 'oracle':
            dsn = cx_Oracle.makedsn(
                config['host'],
                config['port'],
                service_name=config['service_name']
            )
            return cx_Oracle.connect(
                user=config['username'],
                password=config['password'],
                dsn=dsn
            )
        
        elif db_type in ['postgresql', 'mysql']:
            engine_url = f"{db_type}://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
            return create_engine(engine_url)
        
        elif db_type == 'mongodb':
            client = pymongo.MongoClient(config['connection_string'])
            return client[config['database']]
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _load_database_chunks(
        self, connection, db_type: str, table_name: str, query: str, batch_size: int
    ):
        """
        Generator that yields data chunks from database
        """
        if db_type == 'oracle':
            # Oracle-specific chunked reading
            cursor = connection.cursor()
            
            if query:
                cursor.execute(query)
            else:
                cursor.execute(f"SELECT * FROM {table_name}")
            
            # Fetch in batches
            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break
                
                # Convert to DataFrame
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=columns)
                yield df
            
            cursor.close()
        
        elif db_type in ['postgresql', 'mysql']:
            # SQLAlchemy-based chunked reading
            if query:
                for chunk in pd.read_sql(query, connection, chunksize=batch_size):
                    yield chunk
            else:
                for chunk in pd.read_sql_table(table_name, connection, chunksize=batch_size):
                    yield chunk
        
        elif db_type == 'mongodb':
            # MongoDB-specific chunked reading
            collection = connection[table_name]
            cursor = collection.find().batch_size(batch_size)
            
            batch = []
            for doc in cursor:
                batch.append(doc)
                if len(batch) >= batch_size:
                    yield pd.DataFrame(batch)
                    batch = []
            
            if batch:
                yield pd.DataFrame(batch)
    
    def _make_predictions(
        self, df: pd.DataFrame, model, feature_names: List[str], return_confidence: bool
    ):
        """
        Make predictions on DataFrame
        
        Returns:
            predictions, confidence_scores (or None)
        """
        # Select features
        if feature_names:
            X = df[feature_names]
        else:
            # Use all numeric columns
            X = df.select_dtypes(include=[np.number])
        
        # Make predictions
        predictions = model.predict(X)
        
        # Get confidence scores if available
        confidence_scores = None
        if return_confidence and hasattr(model, 'predict_proba'):
            try:
                proba = model.predict_proba(X)
                confidence_scores = np.max(proba, axis=1)
            except:
                pass
        
        return predictions, confidence_scores
    
    def _save_predictions(
        self, df: pd.DataFrame, predictions, confidence_scores, output_path: str
    ):
        """Save predictions to file"""
        result_df = df.copy()
        result_df['prediction'] = predictions
        
        if confidence_scores is not None:
            result_df['confidence'] = confidence_scores
        
        # Save based on file extension
        file_ext = Path(output_path).suffix.lower()
        
        if file_ext == '.csv':
            result_df.to_csv(output_path, index=False)
        elif file_ext in ['.xlsx', '.xls']:
            result_df.to_excel(output_path, index=False)
        elif file_ext == '.parquet':
            result_df.to_parquet(output_path, index=False)
        elif file_ext == '.json':
            result_df.to_json(output_path, orient='records', lines=True)
        
        logger.info(f"✅ Predictions saved to {output_path}")
    
    def _close_database_connection(self, connection, db_type: str):
        """Close database connection"""
        if db_type == 'oracle':
            connection.close()
        elif db_type in ['postgresql', 'mysql']:
            connection.dispose()
        elif db_type == 'mongodb':
            connection.client.close()


# Example usage
if __name__ == "__main__":
    mcp = PredictionMCP()
    
    # Example 1: Predict from CSV file
    result = mcp.predict_from_file(
        file_path="/path/to/large_dataset.csv",
        model_path="/path/to/trained_model.pkl",
        num_threads=8,
        output_path="/path/to/predictions.csv"
    )
    
    print(f"✅ Processed {result['rows_processed']:,} rows")
    print(f"⏱️  Time: {result['processing_time_seconds']:.2f}s")
    print(f"📈 Throughput: {result['throughput_rows_per_second']:,.0f} rows/sec")
    
    # Example 2: Predict from Oracle database
    result = mcp.predict_from_database(
        db_type="oracle",
        connection_config={
            'host': 'your-oracle-host.rds.amazonaws.com',
            'port': '1521',
            'service_name': 'ORCL',
            'username': 'testuser',
            'password': 'password'
        },
        table_name="prediction_data",
        model_path="/path/to/trained_model.pkl",
        batch_size=100000
    )
    
    print(f"✅ Processed {result['rows_processed']:,} rows in {result['batches_processed']} batches")
