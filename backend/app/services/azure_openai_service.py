"""
Azure OpenAI Service - Enterprise AI Integration
Provides advanced AI capabilities for PROMISE AI platform
"""
import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from openai import AzureOpenAI
from dotenv import load_dotenv
import json

# Standardized .env loading
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)


class AzureOpenAIService:
    """Enterprise AI service using Azure OpenAI"""
    
    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-01")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        
        if not self.endpoint or not self.api_key:
            logger.warning("Azure OpenAI credentials not configured")
            self.client = None
        else:
            try:
                self.client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_key=self.api_key,
                    api_version=self.api_version
                )
                logger.info("✅ Azure OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI: {str(e)}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if Azure OpenAI is available"""
        return self.client is not None
    
    async def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_message: str = None,
        json_mode: bool = False
    ) -> str:
        """
        Generate a completion from Azure OpenAI
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            system_message: Optional system message
            json_mode: Enable JSON mode for strict JSON output
        
        Returns:
            Generated text response
        """
        if not self.is_available():
            raise Exception("Azure OpenAI not available")
        
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            # Prepare request parameters
            request_params = {
                "model": self.deployment,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Enable JSON mode if requested (Azure OpenAI 2024-12-01-preview+)
            if json_mode:
                request_params["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**request_params)
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Azure OpenAI completion error: {str(e)}")
            raise
    
    async def generate_insights(
        self,
        data_summary: Dict,
        analysis_results: Dict,
        context: str = "general",
        user_expectation: str = None
    ) -> str:
        """
        Generate AI-powered insights about the analysis
        
        Args:
            data_summary: Summary of the dataset
            analysis_results: ML model results
            context: Context for insights (general, business, technical)
            user_expectation: User's natural language description of what they want to predict (NEW)
        
        Returns:
            AI-generated insights tailored to user's prediction goals
        """
        if not self.is_available():
            return "AI insights unavailable - Azure OpenAI not configured"
        
        try:
            # Build context-aware prompt
            user_context_section = ""
            if user_expectation:
                user_context_section = f"""

🎯 USER'S PREDICTION GOAL:
"{user_expectation}"

IMPORTANT: Frame all insights, recommendations, and explanations in the context of helping the user achieve this specific goal."""
            
            prompt = f"""You are an expert data scientist analyzing results for a business user.
{user_context_section}

Dataset Summary:
- Rows: {data_summary.get('row_count', 'N/A')}
- Columns: {data_summary.get('column_count', 'N/A')}
- Target Variable: {analysis_results.get('target_column', 'N/A')}
- Problem Type: {analysis_results.get('problem_type', 'N/A')}

Model Results:
{json.dumps(analysis_results.get('ml_models', [])[:3], indent=2)}

Provide:
1. Key findings from the analysis{' specifically related to the user\'s goal' if user_expectation else ''}
2. Business recommendations{' aligned with their prediction objective' if user_expectation else ''}
3. Model performance interpretation{' in context of what they want to predict' if user_expectation else ''}
4. Actionable next steps{' to improve predictions for their use case' if user_expectation else ''}

Be concise, professional, and business-focused. If user provided a prediction goal, make sure every insight directly addresses that goal."""

            system_message = "You are an expert data scientist providing business insights."
            if user_expectation:
                system_message += f" Always consider the user's prediction goal: \"{user_expectation}\" when generating insights."

            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000  # Increased for context-aware insights
            )
            
            insights = response.choices[0].message.content
            logger.info(f"✅ AI insights generated successfully{' with user expectation context' if user_expectation else ''}")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {str(e)}")
            return f"Error generating insights: {str(e)}"
    
    async def chat_with_data(
        self,
        user_message: str,
        data_context: Dict,
        conversation_history: List[Dict] = None
    ) -> Dict:
        """
        Intelligent chat about data and analysis
        
        Args:
            user_message: User's question or request
            data_context: Context about the dataset and analysis
            conversation_history: Previous messages
        
        Returns:
            Response dictionary with message and action
        """
        if not self.is_available():
            return {
                "message": "AI chat unavailable - Azure OpenAI not configured",
                "type": "error"
            }
        
        try:
            # Build context
            context = f"""Dataset Context:
- Columns: {', '.join(data_context.get('columns', [])[:10])}
- Rows: {data_context.get('row_count', 'N/A')}
- Problem Type: {data_context.get('problem_type', 'N/A')}

Available Chart Types: scatter, line, bar, histogram, pie, box

User can ask for:
1. Data insights and explanations
2. Chart creation (respond with JSON format)
3. Model recommendations
4. Feature analysis"""

            messages = [
                {"role": "system", "content": f"You are a helpful data analysis assistant. {context}"}
            ]
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # Add current message
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            # Check if response is asking for chart creation
            if any(keyword in user_message.lower() for keyword in ['chart', 'plot', 'graph', 'visualize']):
                return {
                    "message": ai_response,
                    "type": "chart_request",
                    "requires_parsing": True
                }
            
            return {
                "message": ai_response,
                "type": "response"
            }
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return {
                "message": f"Error in chat: {str(e)}",
                "type": "error"
            }
    
    async def parse_chart_request(
        self,
        user_message: str,
        available_columns: List[str]
    ) -> Dict:
        """
        Parse natural language chart request using AI
        
        Args:
            user_message: User's chart request
            available_columns: Available column names
        
        Returns:
            Parsed chart specification
        """
        if not self.is_available():
            return {"error": "AI unavailable", "columns_found": False}
        
        try:
            prompt = f"""Parse this chart request into a structured format.

Available columns: {', '.join(available_columns)}

User request: "{user_message}"

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
            logger.info(f"✅ Chart request parsed: {parsed}")
            return parsed
            
        except Exception as e:
            logger.error(f"Failed to parse chart request: {str(e)}")
            return {
                "error": f"Parsing error: {str(e)}",
                "columns_found": False
            }
    
    async def recommend_models(
        self,
        data_summary: Dict,
        problem_type: str
    ) -> Dict:
        """
        AI-powered model recommendations
        
        Args:
            data_summary: Dataset characteristics
            problem_type: classification or regression
        
        Returns:
            Model recommendations with reasoning
        """
        if not self.is_available():
            return {"recommendations": [], "reasoning": "AI unavailable"}
        
        try:
            prompt = f"""As an ML expert, recommend the best models for this dataset:

Dataset:
- Rows: {data_summary.get('row_count')}
- Features: {data_summary.get('feature_count')}
- Problem: {problem_type}
- Missing Data: {data_summary.get('missing_percentage', 0)}%
- Feature Types: {data_summary.get('feature_types', {})}

Available models for {problem_type}:
{self._get_available_models_list(problem_type)}

Recommend 3-5 best models and explain why.
Respond in JSON format:
{{
  "recommendations": ["model1", "model2", "model3"],
  "reasoning": "explanation",
  "expected_performance": "high|medium|low"
}}"""

            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are an ML model selection expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=400
            )
            
            ai_response = response.choices[0].message.content
            
            # Extract JSON
            json_str = ai_response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            recommendations = json.loads(json_str)
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to recommend models: {str(e)}")
            return {
                "recommendations": [],
                "reasoning": f"Error: {str(e)}"
            }
    
    def _get_available_models_list(self, problem_type: str) -> str:
        """Get formatted list of available models"""
        if problem_type == 'classification':
            models = [
                "Logistic Regression", "Decision Tree", "Random Forest",
                "SVM", "k-NN", "Naive Bayes", "XGBoost", "LightGBM",
                "Gradient Boosting", "Neural Network (MLP)", "QDA", "SGD"
            ]
        else:  # regression
            models = [
                "Linear Regression", "Ridge", "Lasso", "ElasticNet",
                "Decision Tree", "Random Forest", "SVR", "k-NN",
                "Gaussian Process", "XGBoost", "Gradient Boosting", "Bayesian Ridge"
            ]
        return ", ".join(models)


# Singleton instance
_azure_openai_service = None

def get_azure_openai_service() -> AzureOpenAIService:
    """Get or create Azure OpenAI service instance"""
    global _azure_openai_service
    if _azure_openai_service is None:
        _azure_openai_service = AzureOpenAIService()
    return _azure_openai_service
