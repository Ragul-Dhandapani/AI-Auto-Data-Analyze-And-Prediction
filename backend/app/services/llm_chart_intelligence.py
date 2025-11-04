"""
LLM-Powered Chart Intelligence Service
Uses Emergent LLM key or Azure OpenAI for intelligent chart request parsing
"""
import pandas as pd
import json
import os
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Import emergentintegrations
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    HAS_EMERGENT = True
except ImportError:
    HAS_EMERGENT = False
    logger.warning("emergentintegrations not available - LLM chat features disabled")

# TODO: For Azure OpenAI integration, uncomment below and comment out Emergent LLM key
# from openai import AzureOpenAI
# AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
# AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
# 
# client = AzureOpenAI(
#     azure_endpoint=AZURE_OPENAI_ENDPOINT,
#     api_key=AZURE_OPENAI_KEY,
#     api_version="2024-02-01"
# )


class LLMChartIntelligence:
    """LLM-powered chart request parser with intelligent variable mapping"""
    
    def __init__(self):
        self.api_key = os.getenv("EMERGENT_LLM_KEY")
        # TODO: For Azure OpenAI, set self.api_key = AZURE_OPENAI_KEY
        
        if not self.api_key:
            logger.warning("No LLM API key found - chart intelligence will be limited")
    
    async def parse_chart_request(self, user_query: str, df: pd.DataFrame) -> Dict:
        """
        Parse natural language chart request using LLM
        
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
        if not HAS_EMERGENT or not self.api_key:
            return self._fallback_parsing(user_query, df)
        
        try:
            return await self._llm_parse(user_query, df)
        except Exception as e:
            logger.error(f"LLM parsing failed: {str(e)}")
            return self._fallback_parsing(user_query, df)
    
    async def _llm_parse(self, user_query: str, df: pd.DataFrame) -> Dict:
        """Use LLM to intelligently parse chart request"""
        
        available_columns = df.columns.tolist()
        column_types = {col: str(df[col].dtype) for col in available_columns}
        
        # Create system message
        system_message = f"""You are an intelligent chart assistant. Parse user requests for data visualizations.

Available columns in the dataset:
{json.dumps(column_types, indent=2)}

Your task:
1. Identify which columns the user wants to visualize
2. Determine the appropriate chart type
3. Map column names accurately (handle typos, variations, underscores)
4. Validate columns exist in the dataset

Respond in JSON format:
{{
    "chart_type": "scatter|line|bar|histogram|pie|box",
    "x_column": "exact_column_name",
    "y_column": "exact_column_name or null",
    "columns_found": true/false,
    "error": "error message if columns don't exist",
    "explanation": "brief explanation of the chart"
}}

Rules:
- Use EXACT column names from the dataset
- If column doesn't exist, set columns_found=false and suggest alternatives
- For "X vs Y" requests, X goes to x_column, Y to y_column
- For time series, use line charts
- For categorical comparisons, use bar charts"""
        
        # Create chat instance
        # Using Emergent LLM key
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"chart_parse_{id(df)}",
            system_message=system_message
        ).with_model("openai", "gpt-4o-mini")  # Fast and cost-effective
        
        # TODO: For Azure OpenAI, use:
        # response = client.chat.completions.create(
        #     model=AZURE_OPENAI_DEPLOYMENT,
        #     messages=[
        #         {"role": "system", "content": system_message},
        #         {"role": "user", "content": user_query}
        #     ],
        #     temperature=0.3,
        #     max_tokens=500
        # )
        # llm_response = response.choices[0].message.content
        
        # Send message
        user_message = UserMessage(text=user_query)
        llm_response = await chat.send_message(user_message)
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_str = llm_response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            result = json.loads(json_str)
            
            # Validate columns exist
            if result.get("x_column") and result["x_column"] not in available_columns:
                result["columns_found"] = False
                result["error"] = f"❌ Column '{result['x_column']}' not found in dataset. Available columns: {', '.join(available_columns[:5])}..."
            
            if result.get("y_column") and result["y_column"] not in available_columns:
                result["columns_found"] = False
                result["error"] = f"❌ Column '{result['y_column']}' not found in dataset. Available columns: {', '.join(available_columns[:5])}..."
            
            return result
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response as JSON: {llm_response}")
            return self._fallback_parsing(user_query, df)
    
    def _fallback_parsing(self, user_query: str, df: pd.DataFrame) -> Dict:
        """Fallback to basic pattern matching when LLM is unavailable"""
        from difflib import get_close_matches
        
        query_lower = user_query.lower().strip()
        available_columns = df.columns.tolist()
        
        # Simple keyword extraction
        found_columns = []
        for col in available_columns:
            col_lower = col.lower().replace('_', ' ')
            if col_lower in query_lower or col.lower() in query_lower:
                found_columns.append(col)
        
        # Detect chart type
        chart_type = "scatter"
        if any(word in query_lower for word in ["line", "trend", "over time", "timeline"]):
            chart_type = "line"
        elif any(word in query_lower for word in ["bar", "compare", "comparison"]):
            chart_type = "bar"
        elif any(word in query_lower for word in ["histogram", "distribution"]):
            chart_type = "histogram"
        elif any(word in query_lower for word in ["pie", "proportion", "percentage"]):
            chart_type = "pie"
        
        # Parse relationships
        x_col = found_columns[0] if len(found_columns) >= 1 else None
        y_col = found_columns[1] if len(found_columns) >= 2 else None
        
        if not x_col:
            # Try fuzzy matching
            words = query_lower.split()
            for word in words:
                matches = get_close_matches(word, [c.lower() for c in available_columns], n=1, cutoff=0.7)
                if matches:
                    idx = [c.lower() for c in available_columns].index(matches[0])
                    x_col = available_columns[idx]
                    break
        
        if not x_col:
            return {
                "chart_type": chart_type,
                "x_column": None,
                "y_column": None,
                "columns_found": False,
                "suggestions": available_columns[:5],
                "error": f"❌ Could not identify columns from your request. Available columns: {', '.join(available_columns[:10])}",
                "explanation": "Please specify column names more clearly."
            }
        
        return {
            "chart_type": chart_type,
            "x_column": x_col,
            "y_column": y_col,
            "columns_found": True,
            "suggestions": [],
            "error": None,
            "explanation": f"Creating {chart_type} chart with {x_col}" + (f" vs {y_col}" if y_col else "")
        }


# Singleton instance
_llm_chart_intelligence = None

def get_llm_chart_intelligence() -> LLMChartIntelligence:
    """Get or create singleton LLM chart intelligence instance"""
    global _llm_chart_intelligence
    if _llm_chart_intelligence is None:
        _llm_chart_intelligence = LLMChartIntelligence()
    return _llm_chart_intelligence
