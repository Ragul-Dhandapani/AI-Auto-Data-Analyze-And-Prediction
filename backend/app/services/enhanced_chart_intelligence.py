"""
Enhanced Chart Intelligence with LLM Integration
Parses natural language requests and maps to chart specifications
"""
import pandas as pd
import re
from typing import Dict, List, Optional, Tuple
from difflib import get_close_matches
import logging

logger = logging.getLogger(__name__)


class EnhancedChartIntelligence:
    """LLM-powered chart request parser"""
    
    @staticmethod
    def parse_chart_request(user_query: str, df: pd.DataFrame) -> Dict:
        """
        Parse natural language chart request using pattern matching and fuzzy column matching
        
        Examples:
            "show me cpu_utilization vs endpoint" → scatter(x=cpu_utilization, y=endpoint)
            "plot latency over time" → line(x=time, y=latency)
            "compare status codes" → bar(x=status_code)
        
        Args:
            user_query: Natural language request
            df: DataFrame with available columns
        
        Returns:
            {
                "chart_type": str,
                "x_column": str,
                "y_column": Optional[str],
                "columns_found": bool,
                "suggestions": List[str],
                "error": Optional[str]
            }
        """
        query_lower = user_query.lower().strip()
        available_columns = df.columns.tolist()
        
        # Extract column names from query using fuzzy matching
        found_columns = EnhancedChartIntelligence._extract_columns_fuzzy(query_lower, available_columns)
        
        # Detect chart type from keywords
        chart_type = EnhancedChartIntelligence._detect_chart_type(query_lower)
        
        # Parse relationships (vs, against, over, by)
        x_col, y_col = EnhancedChartIntelligence._parse_relationships(query_lower, found_columns)
        
        if not x_col and len(found_columns) >= 1:
            x_col = found_columns[0]
        
        if not y_col and len(found_columns) >= 2:
            y_col = found_columns[1]
        
        # Validate results
        if not x_col:
            return {
                "chart_type": chart_type,
                "x_column": None,
                "y_column": None,
                "columns_found": False,
                "suggestions": [f"Available columns: {', '.join(available_columns[:10])}"],
                "error": "❌ Could not identify any columns from your request. Please specify column names clearly."
            }
        
        # Check if columns actually exist
        x_col_validated = EnhancedChartIntelligence._validate_column(x_col, available_columns)
        y_col_validated = EnhancedChartIntelligence._validate_column(y_col, available_columns) if y_col else None
        
        if not x_col_validated:
            matches = get_close_matches(x_col, available_columns, n=3, cutoff=0.6)
            return {
                "chart_type": chart_type,
                "x_column": None,
                "y_column": None,
                "columns_found": False,
                "suggestions": matches,
                "error": f"❌ Column '{x_col}' not found. Did you mean: {', '.join(matches)}?" if matches else f"❌ Column '{x_col}' not found."
            }
        
        return {
            "chart_type": chart_type,
            "x_column": x_col_validated,
            "y_column": y_col_validated,
            "columns_found": True,
            "suggestions": [],
            "error": None
        }
    
    @staticmethod
    def _extract_columns_fuzzy(query: str, available_columns: List[str]) -> List[str]:
        """
        Extract column names from query using fuzzy matching
        Handles underscores, case variations, and typos
        """
        found_columns = []
        
        # Direct exact matches (case insensitive)
        for col in available_columns:
            col_lower = col.lower()
            col_variations = [
                col_lower,
                col_lower.replace('_', ' '),
                col_lower.replace('_', ''),
                col_lower.replace('-', '_'),
            ]
            
            for variation in col_variations:
                if variation in query:
                    found_columns.append(col)
                    break
        
        # Fuzzy matching for remaining terms
        if len(found_columns) < 2:
            # Extract potential column names from query (words with underscores or longer words)
            potential_cols = re.findall(r'\b[a-z_]{3,}\b', query)
            
            for potential in potential_cols:
                if potential not in [c.lower() for c in found_columns]:
                    matches = get_close_matches(potential, available_columns, n=1, cutoff=0.7)
                    if matches:
                        found_columns.append(matches[0])
        
        return list(dict.fromkeys(found_columns))  # Remove duplicates, preserve order
    
    @staticmethod
    def _detect_chart_type(query: str) -> str:
        """Detect chart type from keywords in query"""
        chart_keywords = {
            'scatter': ['scatter', 'vs', 'versus', 'against', 'correlation'],
            'line': ['line', 'trend', 'over time', 'timeline', 'series'],
            'bar': ['bar', 'compare', 'comparison', 'distribution', 'count'],
            'pie': ['pie', 'proportion', 'percentage', 'share'],
            'histogram': ['histogram', 'distribution', 'frequency']
        }
        
        for chart_type, keywords in chart_keywords.items():
            if any(keyword in query for keyword in keywords):
                return chart_type
        
        return 'scatter'  # Default
    
    @staticmethod
    def _parse_relationships(query: str, found_columns: List[str]) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse relationships like 'X vs Y', 'X against Y', 'X over Y'
        """
        if len(found_columns) < 2:
            return (found_columns[0] if found_columns else None, None)
        
        # Patterns: "X vs Y", "X against Y", "X by Y"
        relationship_patterns = [
            (r'(.+?)\s+vs\s+(.+)', 0, 1),
            (r'(.+?)\s+versus\s+(.+)', 0, 1),
            (r'(.+?)\s+against\s+(.+)', 0, 1),
            (r'(.+?)\s+over\s+(.+)', 0, 1),
            (r'(.+?)\s+by\s+(.+)', 0, 1),
        ]
        
        for pattern, x_idx, y_idx in relationship_patterns:
            match = re.search(pattern, query)
            if match:
                part1 = match.group(x_idx + 1).strip()
                part2 = match.group(y_idx + 1).strip()
                
                # Find which columns match which parts
                x_col = None
                y_col = None
                
                for col in found_columns:
                    if col.lower() in part1:
                        x_col = col
                    elif col.lower() in part2:
                        y_col = col
                
                if x_col and y_col:
                    return (x_col, y_col)
        
        # Default: first is X, second is Y
        return (found_columns[0], found_columns[1] if len(found_columns) > 1 else None)
    
    @staticmethod
    def _validate_column(col_name: Optional[str], available_columns: List[str]) -> Optional[str]:
        """Validate column name exists (case insensitive)"""
        if not col_name:
            return None
        
        col_lower = col_name.lower()
        for col in available_columns:
            if col.lower() == col_lower:
                return col
        
        return None


# Global instance
enhanced_chart_intelligence = EnhancedChartIntelligence()
