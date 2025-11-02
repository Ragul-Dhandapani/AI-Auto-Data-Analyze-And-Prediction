"""
NLP Service for Text Processing
Handles text columns with TF-IDF, sentiment analysis, and feature extraction
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD


def detect_text_columns(df: pd.DataFrame) -> List[str]:
    """
    Detect columns that contain text data
    """
    text_columns = []
    
    for col in df.columns:
        if df[col].dtype == 'object':
            # Check if column contains text (not categorical with few unique values)
            unique_ratio = df[col].nunique() / len(df[col].dropna())
            avg_length = df[col].dropna().astype(str).str.len().mean()
            
            # Text columns typically have high unique ratio and longer strings
            if unique_ratio > 0.3 and avg_length > 20:
                text_columns.append(col)
    
    return text_columns


def extract_text_features(
    df: pd.DataFrame,
    text_column: str,
    max_features: int = 100,
    n_components: int = 10
) -> pd.DataFrame:
    """
    Extract features from text column using TF-IDF and dimensionality reduction
    
    Args:
        df: DataFrame with text column
        text_column: Name of text column
        max_features: Maximum number of TF-IDF features
        n_components: Number of components for SVD dimensionality reduction
    
    Returns:
        DataFrame with text features added
    """
    try:
        # Fill missing values
        texts = df[text_column].fillna('').astype(str)
        
        # TF-IDF vectorization
        vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Dimensionality reduction with SVD
        svd = TruncatedSVD(n_components=min(n_components, tfidf_matrix.shape[1] - 1))
        text_features = svd.fit_transform(tfidf_matrix)
        
        # Create feature columns
        feature_names = [f"{text_column}_text_feat_{i}" for i in range(text_features.shape[1])]
        text_df = pd.DataFrame(text_features, columns=feature_names, index=df.index)
        
        # Add basic text statistics
        text_df[f"{text_column}_length"] = texts.str.len()
        text_df[f"{text_column}_word_count"] = texts.str.split().str.len()
        
        logging.info(f"Extracted {text_features.shape[1]} text features from {text_column}")
        
        return text_df
    
    except Exception as e:
        logging.error(f"Text feature extraction failed for {text_column}: {str(e)}")
        return pd.DataFrame()


def process_text_columns(
    df: pd.DataFrame,
    text_columns: List[str] = None,
    max_features: int = 50
) -> pd.DataFrame:
    """
    Process all text columns in dataframe and add features
    
    Args:
        df: Input dataframe
        text_columns: List of text columns to process (if None, auto-detect)
        max_features: Maximum features per text column
    
    Returns:
        DataFrame with text features added
    """
    if text_columns is None:
        text_columns = detect_text_columns(df)
    
    if not text_columns:
        logging.info("No text columns detected")
        return df
    
    df_result = df.copy()
    
    for text_col in text_columns:
        if text_col in df_result.columns:
            text_features = extract_text_features(df_result, text_col, max_features=max_features)
            
            if not text_features.empty:
                # Add text features to dataframe
                df_result = pd.concat([df_result, text_features], axis=1)
                
                # Optionally drop original text column for modeling
                # df_result = df_result.drop(columns=[text_col])
    
    return df_result


def extract_datetime_features(df: pd.DataFrame, datetime_columns: List[str]) -> pd.DataFrame:
    """
    Extract features from datetime columns
    
    Args:
        df: Input dataframe
        datetime_columns: List of datetime columns
    
    Returns:
        DataFrame with datetime features added
    """
    df_result = df.copy()
    
    for col in datetime_columns:
        if col not in df_result.columns:
            continue
        
        try:
            # Convert to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(df_result[col]):
                df_result[col] = pd.to_datetime(df_result[col], errors='coerce')
            
            # Extract features
            df_result[f"{col}_year"] = df_result[col].dt.year
            df_result[f"{col}_month"] = df_result[col].dt.month
            df_result[f"{col}_day"] = df_result[col].dt.day
            df_result[f"{col}_dayofweek"] = df_result[col].dt.dayofweek
            df_result[f"{col}_quarter"] = df_result[col].dt.quarter
            df_result[f"{col}_hour"] = df_result[col].dt.hour
            df_result[f"{col}_is_weekend"] = (df_result[col].dt.dayofweek >= 5).astype(int)
            
            logging.info(f"Extracted datetime features from {col}")
        
        except Exception as e:
            logging.error(f"Failed to extract datetime features from {col}: {str(e)}")
    
    return df_result
