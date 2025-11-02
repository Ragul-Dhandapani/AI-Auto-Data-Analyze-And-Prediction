"""
Chart Intelligence Service
Validates chart requests and provides intelligent suggestions
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ChartIntelligenceService:
    """AI-powered chart validation and suggestion service"""
    
    @staticmethod
    def validate_chart_request(
        df: pd.DataFrame, 
        chart_type: str, 
        column: str,
        y_column: Optional[str] = None
    ) -> Dict:
        """
        Validate if a chart request is feasible
        
        Args:
            df: DataFrame with data
            chart_type: Type of chart requested (pie, line, scatter, bar, etc.)
            column: Primary column for chart
            y_column: Secondary column (for scatter, etc.)
            
        Returns:
            {
                "feasible": bool,
                "reason": str,
                "suggestion": str,
                "alternative_charts": List[Dict]
            }
        """
        try:
            # Check if column exists
            if column not in df.columns:
                return {
                    "feasible": False,
                    "reason": f"Column '{column}' not found in dataset. Available columns: {', '.join(df.columns.tolist()[:5])}...",
                    "suggestion": "Please choose a valid column name.",
                    "alternative_charts": []
                }
            
            col_data = df[column]
            
            # Check data quality
            null_percentage = (col_data.isnull().sum() / len(df)) * 100
            if null_percentage > 80:
                return {
                    "feasible": False,
                    "reason": f"Column '{column}' has {null_percentage:.1f}% missing values. Too sparse for reliable visualization.",
                    "suggestion": "Consider cleaning the data first or choosing a column with fewer missing values.",
                    "alternative_charts": []
                }
            
            # Validate based on chart type
            if chart_type.lower() in ['pie', 'pie_chart', 'piechart']:
                return ChartIntelligenceService._validate_pie_chart(df, column)
            
            elif chart_type.lower() in ['scatter', 'scatter_plot', 'scatterplot']:
                if not y_column:
                    return {
                        "feasible": False,
                        "reason": "Scatter plots require both X and Y columns.",
                        "suggestion": "Please specify both columns for scatter plot.",
                        "alternative_charts": []
                    }
                return ChartIntelligenceService._validate_scatter_plot(df, column, y_column)
            
            elif chart_type.lower() in ['line', 'line_chart', 'linechart']:
                return ChartIntelligenceService._validate_line_chart(df, column)
            
            elif chart_type.lower() in ['bar', 'bar_chart', 'barchart']:
                return ChartIntelligenceService._validate_bar_chart(df, column)
            
            elif chart_type.lower() in ['histogram', 'hist']:
                return ChartIntelligenceService._validate_histogram(df, column)
            
            else:
                # Generic validation for other chart types
                return {
                    "feasible": True,
                    "reason": f"Chart type '{chart_type}' appears valid.",
                    "suggestion": "",
                    "alternative_charts": []
                }
                
        except Exception as e:
            logger.error(f"Error validating chart request: {str(e)}")
            return {
                "feasible": False,
                "reason": f"Error analyzing data: {str(e)}",
                "suggestion": "Please check your data and try again.",
                "alternative_charts": []
            }
    
    @staticmethod
    def _validate_pie_chart(df: pd.DataFrame, column: str) -> Dict:
        """Validate pie chart request"""
        col_data = df[column]
        unique_count = col_data.nunique()
        is_numeric = pd.api.types.is_numeric_dtype(col_data)
        
        # Check if it's continuous numeric data
        if is_numeric and unique_count > 20:
            alternatives = [
                {
                    "type": "histogram",
                    "title": "Histogram",
                    "description": f"Show distribution of {column} values in bins",
                    "suitability": "excellent"
                },
                {
                    "type": "line_chart",
                    "title": "Line Chart",
                    "description": f"Show {column} trends over time (if time-series data)",
                    "suitability": "good"
                },
                {
                    "type": "box_plot",
                    "title": "Box Plot",
                    "description": f"Show quartiles and outliers in {column}",
                    "suitability": "good"
                }
            ]
            
            return {
                "feasible": False,
                "reason": f"Column '{column}' contains continuous numeric values with {unique_count} unique values. Pie charts work best for categorical data with 3-10 categories, not continuous numeric values.",
                "suggestion": f"For continuous numeric data like '{column}', consider using a histogram to show distribution, a line chart for trends, or a box plot for statistical summary.",
                "alternative_charts": alternatives
            }
        
        # Check if too few categories
        if unique_count < 2:
            return {
                "feasible": False,
                "reason": f"Column '{column}' has only {unique_count} unique value(s). Need at least 2 categories for a meaningful pie chart.",
                "suggestion": "Choose a column with more variety in values.",
                "alternative_charts": []
            }
        
        # Check if too many categories
        if unique_count > 15:
            alternatives = [
                {
                    "type": "bar_chart",
                    "title": "Bar Chart",
                    "description": f"Better for comparing {unique_count} categories",
                    "suitability": "excellent"
                }
            ]
            return {
                "feasible": False,
                "reason": f"Column '{column}' has {unique_count} unique values. Pie charts with more than 10-15 slices become hard to read.",
                "suggestion": "Consider a bar chart instead, or group some categories together.",
                "alternative_charts": alternatives
            }
        
        # Valid for pie chart
        return {
            "feasible": True,
            "reason": f"Column '{column}' has {unique_count} categories, perfect for a pie chart visualization.",
            "suggestion": "",
            "alternative_charts": []
        }
    
    @staticmethod
    def _validate_scatter_plot(df: pd.DataFrame, x_col: str, y_col: str) -> Dict:
        """Validate scatter plot request"""
        x_data = df[x_col]
        y_data = df[y_col]
        
        x_numeric = pd.api.types.is_numeric_dtype(x_data)
        y_numeric = pd.api.types.is_numeric_dtype(y_data)
        
        if not x_numeric or not y_numeric:
            non_numeric = []
            if not x_numeric:
                non_numeric.append(x_col)
            if not y_numeric:
                non_numeric.append(y_col)
            
            return {
                "feasible": False,
                "reason": f"Scatter plots require numeric data on both axes. Column(s) '{', '.join(non_numeric)}' is/are not numeric.",
                "suggestion": "Choose numeric columns for both X and Y axes.",
                "alternative_charts": []
            }
        
        # Check for zero variance
        if x_data.std() == 0:
            return {
                "feasible": False,
                "reason": f"Column '{x_col}' has zero variance (all values are the same: {x_data.iloc[0]}).",
                "suggestion": "Choose a column with varying values.",
                "alternative_charts": []
            }
        
        if y_data.std() == 0:
            return {
                "feasible": False,
                "reason": f"Column '{y_col}' has zero variance (all values are the same: {y_data.iloc[0]}).",
                "suggestion": "Choose a column with varying values.",
                "alternative_charts": []
            }
        
        return {
            "feasible": True,
            "reason": f"Both '{x_col}' and '{y_col}' are numeric with good variance. Suitable for scatter plot.",
            "suggestion": "",
            "alternative_charts": []
        }
    
    @staticmethod
    def _validate_line_chart(df: pd.DataFrame, column: str) -> Dict:
        """Validate line chart request"""
        col_data = df[column]
        
        if not pd.api.types.is_numeric_dtype(col_data):
            return {
                "feasible": False,
                "reason": f"Column '{column}' is not numeric. Line charts require numeric data for the Y-axis.",
                "suggestion": "Choose a numeric column for line chart.",
                "alternative_charts": []
            }
        
        # Check for sufficient data points
        if len(col_data.dropna()) < 3:
            return {
                "feasible": False,
                "reason": f"Only {len(col_data.dropna())} data points available. Need at least 3 points for a line chart.",
                "suggestion": "Need more data points for meaningful line chart.",
                "alternative_charts": []
            }
        
        return {
            "feasible": True,
            "reason": f"Column '{column}' is numeric with {len(col_data.dropna())} data points. Suitable for line chart.",
            "suggestion": "",
            "alternative_charts": []
        }
    
    @staticmethod
    def _validate_bar_chart(df: pd.DataFrame, column: str) -> Dict:
        """Validate bar chart request"""
        col_data = df[column]
        unique_count = col_data.nunique()
        
        if unique_count > 50:
            return {
                "feasible": False,
                "reason": f"Column '{column}' has {unique_count} unique values. Bar charts become cluttered with more than 50 categories.",
                "suggestion": "Consider grouping categories or using a different visualization.",
                "alternative_charts": [
                    {
                        "type": "histogram",
                        "title": "Histogram",
                        "description": "If data is numeric, histogram can bin values",
                        "suitability": "good"
                    }
                ]
            }
        
        return {
            "feasible": True,
            "reason": f"Column '{column}' has {unique_count} categories, suitable for bar chart.",
            "suggestion": "",
            "alternative_charts": []
        }
    
    @staticmethod
    def _validate_histogram(df: pd.DataFrame, column: str) -> Dict:
        """Validate histogram request"""
        col_data = df[column]
        
        if not pd.api.types.is_numeric_dtype(col_data):
            return {
                "feasible": False,
                "reason": f"Column '{column}' is not numeric. Histograms require numeric data.",
                "suggestion": "Choose a numeric column for histogram, or use bar chart for categorical data.",
                "alternative_charts": [
                    {
                        "type": "bar_chart",
                        "title": "Bar Chart",
                        "description": "For categorical data",
                        "suitability": "excellent"
                    }
                ]
            }
        
        unique_count = col_data.nunique()
        if unique_count < 5:
            return {
                "feasible": False,
                "reason": f"Column '{column}' has only {unique_count} unique values. Histograms work best with more varied continuous data.",
                "suggestion": "Use a bar chart instead for discrete values.",
                "alternative_charts": [
                    {
                        "type": "bar_chart",
                        "title": "Bar Chart",
                        "description": "Better for few discrete values",
                        "suitability": "excellent"
                    }
                ]
            }
        
        return {
            "feasible": True,
            "reason": f"Column '{column}' is numeric with good distribution. Suitable for histogram.",
            "suggestion": "",
            "alternative_charts": []
        }


# Singleton instance
chart_intelligence = ChartIntelligenceService()
