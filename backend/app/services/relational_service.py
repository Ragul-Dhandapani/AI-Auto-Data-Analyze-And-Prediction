"""
Relational Data Handling Service
Supports multi-table joins and foreign key relationship management
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
import logging


def detect_foreign_keys(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    threshold: float = 0.8
) -> List[Tuple[str, str]]:
    """
    Automatically detect potential foreign key relationships between two dataframes
    
    Args:
        left_df: First dataframe
        right_df: Second dataframe
        threshold: Match threshold for considering columns as foreign keys
    
    Returns:
        List of tuples (left_column, right_column) representing potential FK relationships
    """
    potential_fks = []
    
    for left_col in left_df.columns:
        for right_col in right_df.columns:
            # Check if column names are similar
            if left_col.lower() == right_col.lower() or \
               left_col.lower().endswith('_id') and right_col.lower() == 'id':
                
                # Check if values overlap significantly
                left_values = set(left_df[left_col].dropna().unique())
                right_values = set(right_df[right_col].dropna().unique())
                
                if len(left_values) > 0 and len(right_values) > 0:
                    overlap = len(left_values.intersection(right_values))
                    match_ratio = overlap / min(len(left_values), len(right_values))
                    
                    if match_ratio >= threshold:
                        potential_fks.append((left_col, right_col))
                        logging.info(f"Detected potential FK: {left_col} <-> {right_col} (match: {match_ratio:.2f})")
    
    return potential_fks


def join_tables(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    left_on: str,
    right_on: str,
    how: str = 'inner',
    suffixes: Tuple[str, str] = ('_left', '_right')
) -> pd.DataFrame:
    """
    Join two dataframes on specified columns
    
    Args:
        left_df: First dataframe
        right_df: Second dataframe
        left_on: Column name in left dataframe
        right_on: Column name in right dataframe
        how: Join type ('inner', 'left', 'right', 'outer')
        suffixes: Suffixes for overlapping column names
    
    Returns:
        Joined dataframe
    """
    try:
        result = left_df.merge(
            right_df,
            left_on=left_on,
            right_on=right_on,
            how=how,
            suffixes=suffixes
        )
        
        logging.info(f"Joined tables: {len(left_df)} x {len(right_df)} -> {len(result)} rows")
        
        return result
    
    except Exception as e:
        logging.error(f"Table join failed: {str(e)}")
        raise


def optimize_join(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    left_on: str,
    right_on: str,
    sample_size: int = 10000
) -> pd.DataFrame:
    """
    Optimize join operation for large datasets by sampling
    
    Args:
        left_df: First dataframe
        right_df: Second dataframe
        left_on: Column name in left dataframe
        right_on: Column name in right dataframe
        sample_size: Maximum rows to keep from each table
    
    Returns:
        Joined and optimized dataframe
    """
    # Sample if datasets are too large
    if len(left_df) > sample_size:
        left_df_sampled = left_df.sample(n=sample_size, random_state=42)
        logging.info(f"Sampled left table: {len(left_df)} -> {sample_size} rows")
    else:
        left_df_sampled = left_df
    
    if len(right_df) > sample_size:
        right_df_sampled = right_df.sample(n=sample_size, random_state=42)
        logging.info(f"Sampled right table: {len(right_df)} -> {sample_size} rows")
    else:
        right_df_sampled = right_df
    
    return join_tables(left_df_sampled, right_df_sampled, left_on, right_on)


def join_multiple_tables(
    tables: List[pd.DataFrame],
    join_keys: List[Tuple[str, str]],
    table_names: List[str] = None
) -> pd.DataFrame:
    """
    Join multiple tables sequentially
    
    Args:
        tables: List of dataframes to join
        join_keys: List of (left_key, right_key) tuples for each join
        table_names: Optional names for tables (used in suffixes)
    
    Returns:
        Final joined dataframe
    """
    if len(tables) < 2:
        return tables[0] if tables else pd.DataFrame()
    
    if table_names is None:
        table_names = [f"table_{i}" for i in range(len(tables))]
    
    # Start with first table
    result = tables[0]
    
    # Join each subsequent table
    for i in range(1, len(tables)):
        if i - 1 < len(join_keys):
            left_key, right_key = join_keys[i - 1]
            suffixes = (f"_{table_names[i-1]}", f"_{table_names[i]}")
            
            result = join_tables(
                result,
                tables[i],
                left_on=left_key,
                right_on=right_key,
                suffixes=suffixes
            )
    
    return result
