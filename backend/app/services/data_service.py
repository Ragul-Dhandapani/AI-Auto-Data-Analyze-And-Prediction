"""
Data Processing and Profiling Service
Handles data ingestion, cleaning, and profiling
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging


def generate_data_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate comprehensive data profiling report"""
    
    # Calculate missing values
    total_missing = int(df.isnull().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    
    # Build columns info for frontend compatibility
    columns_info = []
    columns = []
    
    for col in df.columns:
        col_info = {
            "name": col,
            "dtype": str(df[col].dtype),
            "unique_values": int(df[col].nunique()),
            "missing_count": int(df[col].isnull().sum()),
            "missing_percentage": float(df[col].isnull().sum() / len(df) * 100)
        }
        
        # Numeric column statistics
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info["statistics"] = {
                "mean": float(df[col].mean()) if not df[col].isna().all() else None,
                "median": float(df[col].median()) if not df[col].isna().all() else None,
                "std": float(df[col].std()) if not df[col].isna().all() else None,
                "min": float(df[col].min()) if not df[col].isna().all() else None,
                "max": float(df[col].max()) if not df[col].isna().all() else None,
                "q25": float(df[col].quantile(0.25)) if not df[col].isna().all() else None,
                "q75": float(df[col].quantile(0.75)) if not df[col].isna().all() else None
            }
        else:
            # Categorical column info
            col_info["top_values"] = df[col].value_counts().head(5).to_dict()
        
        columns.append(col_info)
        columns_info.append(col_info)  # Frontend expects columns_info
    
    profile = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "missing_values_total": total_missing,  # Frontend expects this field
        "duplicate_rows": duplicate_rows,  # Frontend expects this field
        "columns": columns,
        "columns_info": columns_info,  # Frontend expects this field
        "missing_data_summary": {
            "total_missing": total_missing,
            "columns_with_missing": [
                {
                    "column": col_info["name"],
                    "count": col_info["missing_count"],
                    "percentage": col_info["missing_percentage"]
                }
                for col_info in columns_info
                if col_info["missing_count"] > 0
            ]
        },
        "numeric_summary": {},
        "categorical_summary": {}
    }
    
    # Numeric summary
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        profile["numeric_summary"] = df[numeric_cols].describe().to_dict()
    
    # Categorical summary
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        profile["categorical_summary"] = {
            col: df[col].value_counts().head(10).to_dict()
            for col in categorical_cols
        }
    
    return profile


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Basic data cleaning operations"""
    # Remove duplicate rows
    df = df.drop_duplicates()
    
    # Handle numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        # Fill missing values with median
        if df[col].isnull().sum() > 0:
            df[col].fillna(df[col].median(), inplace=True)
    
    # Handle categorical columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in categorical_cols:
        # Fill missing values with mode
        if df[col].isnull().sum() > 0:
            mode_value = df[col].mode()[0] if len(df[col].mode()) > 0 else "Unknown"
            df[col].fillna(mode_value, inplace=True)
    
    return df


def clean_data(df: pd.DataFrame) -> tuple:
    """Clean data and return cleaning report"""
    cleaning_report = []
    original_rows = len(df)
    
    # 1. Remove duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        df = df.drop_duplicates()
        cleaning_report.append({
            "action": "Removed duplicate rows",
            "details": f"Removed {duplicates} duplicate rows"
        })
    
    # 2. Handle missing values in numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            cleaning_report.append({
                "action": f"Filled missing values in '{col}'",
                "details": f"Filled {missing_count} missing values with median ({median_val:.2f})"
            })
    
    # 3. Handle missing values in categorical columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in categorical_cols:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            mode_value = df[col].mode()[0] if len(df[col].mode()) > 0 else "Unknown"
            df[col].fillna(mode_value, inplace=True)
            cleaning_report.append({
                "action": f"Filled missing values in '{col}'",
                "details": f"Filled {missing_count} missing values with mode ('{mode_value}')"
            })
    
    return df, cleaning_report


def detect_outliers(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Detect outliers using IQR method"""
    if not pd.api.types.is_numeric_dtype(df[column]):
        return {"outliers": [], "count": 0}
    
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)][column]
    
    return {
        "column": column,
        "outlier_count": len(outliers),
        "outlier_percentage": (len(outliers) / len(df)) * 100,
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound),
        "outlier_values": outliers.tolist()[:100]  # Limit to first 100
    }


def get_correlation_matrix(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate correlation matrix for numeric columns"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) < 2:
        return {"correlations": [], "matrix": {}}
    
    corr_matrix = df[numeric_cols].corr()
    
    # Extract significant correlations
    correlations = []
    for i in range(len(numeric_cols)):
        for j in range(i + 1, len(numeric_cols)):
            corr_value = corr_matrix.iloc[i, j]
            if abs(corr_value) > 0.1:  # Only significant correlations
                correlations.append({
                    "feature1": numeric_cols[i],
                    "feature2": numeric_cols[j],
                    "correlation": float(corr_value),
                    "strength": "strong" if abs(corr_value) > 0.7 else "moderate" if abs(corr_value) > 0.4 else "weak",
                    "direction": "positive" if corr_value > 0 else "negative"
                })
    
    # Sort by absolute correlation value
    correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
    
    return {
        "correlations": correlations,
        "matrix": corr_matrix.to_dict()
    }
