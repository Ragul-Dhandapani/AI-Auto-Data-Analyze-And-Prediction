"""
LLM-Powered Chart Intelligence Service
Uses Azure OpenAI for intelligent chart request parsing
"""
import pandas as pd
import json
import os
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# Azure OpenAI integration
try:
    from openai import AzureOpenAI
    HAS_AZURE_OPENAI = True
except ImportError:
    HAS_AZURE_OPENAI = False
    logger.warning("openai library not available - LLM chat features disabled")


class LLMChartIntelligence:
    """Azure OpenAI-powered chart request parser with intelligent variable mapping"""
    
    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        
        if not self.endpoint or not self.api_key:
            logger.warning("Azure OpenAI not configured - chart intelligence will be limited")
            self.client = None
        else:
            try:
                self.client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_key=self.api_key,
                    api_version=self.api_version
                )
                logger.info("✅ Azure OpenAI initialized for chart intelligence")
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI: {e}")
                self.client = None
    
    async def parse_chart_request(self, user_query: str, df: pd.DataFrame) -> Dict:
        """
        Parse natural language chart request using Azure OpenAI
        
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
                "error": Optional[str],
                "explanation": str
            }
        """
        if not self.client:
            return self._fallback_parsing(user_query, df)
        
        try:
            return await self._azure_parse(user_query, df)
        except Exception as e:
            logger.error(f"Azure OpenAI parsing failed: {str(e)}")
            return self._fallback_parsing(user_query, df)
    
    async def _azure_parse(self, user_query: str, df: pd.DataFrame) -> Dict:
        """Use Azure OpenAI to intelligently parse chart request"""
        
        available_columns = df.columns.tolist()
        column_types = {col: str(df[col].dtype) for col in available_columns}
        
        # Create prompt
        prompt = f"""You are an intelligent chart assistant. Parse this chart request.

Available columns in the dataset:
{json.dumps(column_types, indent=2)}

User request: "{user_query}"

Respond ONLY with valid JSON in this exact format:
{{
    "chart_type": "scatter|line|bar|histogram|pie|box",
    "x_column": "exact_column_name_or_null",
    "y_column": "exact_column_name_or_null",
    "columns_found": true/false,
    "error": "error_message_if_columns_not_found",
    "explanation": "brief_explanation"
}}

Rules:
1. Use ONLY column names from the available list
2. Match columns even if user uses variations/typos
3. For "X vs Y", X is x_column, Y is y_column
4. If columns don't exist, set columns_found=false and suggest alternatives"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a data visualization expert. Respond ONLY with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            ai_response = response.choices[0].message.content
            
            # Extract JSON from response
            json_str = ai_response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            parsed = json.loads(json_str)
            logger.info(f"✅ Azure OpenAI parsed chart request: {parsed}")
            return parsed
            
        except Exception as e:
            logger.error(f"Azure OpenAI parsing error: {str(e)}")
            return self._fallback_parsing(user_query, df)
    
    def _fallback_parsing(self, user_query: str, df: pd.DataFrame) -> Dict:
        """Fallback to pattern matching when Azure OpenAI unavailable"""
        
        query_lower = user_query.lower()
        available_columns = df.columns.tolist()
        
        # Detect chart type
        chart_type = "bar"
        if any(word in query_lower for word in ['scatter', 'vs', 'versus', 'against']):
            chart_type = "scatter"
        elif any(word in query_lower for word in ['line', 'trend', 'over time']):
            chart_type = "line"
        elif any(word in query_lower for word in ['histogram', 'distribution']):
            chart_type = "histogram"
        elif any(word in query_lower for word in ['pie', 'breakdown']):
            chart_type = "pie"
        
        # Try to find columns
        found_columns = []
        for col in available_columns:
            if col.lower() in query_lower or col.lower().replace('_', ' ') in query_lower:
                found_columns.append(col)
        
        if len(found_columns) >= 1:
            return {
                "chart_type": chart_type,
                "x_column": found_columns[0],
                "y_column": found_columns[1] if len(found_columns) > 1 else None,
                "columns_found": True,
                "explanation": f"Pattern-matched columns: {', '.join(found_columns)}"
            }
        else:
            return {
                "chart_type": chart_type,
                "x_column": None,
                "y_column": None,
                "columns_found": False,
                "error": f"Could not find matching columns. Available: {', '.join(available_columns[:10])}",
                "explanation": "Pattern matching failed - please specify exact column names"
            }


# Singleton instance
_llm_chart_intelligence = None

def get_llm_chart_intelligence() -> LLMChartIntelligence:
    """Get or create LLM chart intelligence instance"""
    global _llm_chart_intelligence
    if _llm_chart_intelligence is None:
        _llm_chart_intelligence = LLMChartIntelligence()
    return _llm_chart_intelligence
