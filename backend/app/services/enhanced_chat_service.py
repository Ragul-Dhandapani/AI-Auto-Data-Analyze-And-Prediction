"""
Enhanced Chat Service with Azure OpenAI
Full-featured AI data analysis assistant with:
- Dataset awareness
- Chart creation/manipulation
- Prediction insights
- Interactive workflows
- Analytical guidance
"""
import logging
import json
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class EnhancedChatService:
    """AI-powered chat assistant for data analysis"""
    
    def __init__(self):
        self.context = {}
        
    async def process_message(
        self,
        message: str,
        dataset_id: str,
        dataset: Optional[pd.DataFrame] = None,
        analysis_results: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Process user message with full context awareness
        
        Args:
            message: User's chat message
            dataset_id: Current dataset ID
            dataset: DataFrame (if available)
            analysis_results: ML model results (if available)
            conversation_history: Previous messages
            
        Returns:
            {
                'response': str,
                'action': str,  # 'message', 'chart', 'confirm', 'error'
                'data': dict,  # Additional data (chart config, stats, etc.)
                'requires_confirmation': bool,
                'suggestions': List[str]  # Follow-up suggestions
            }
        """
        try:
            message_lower = message.lower().strip()
            
            # Update context
            self.context = {
                'dataset_id': dataset_id,
                'has_dataset': dataset is not None,
                'has_results': analysis_results is not None,
                'dataset_shape': dataset.shape if dataset is not None else None,
                'columns': list(dataset.columns) if dataset is not None else [],
                'analysis_results': analysis_results
            }
            
            # Route to appropriate handler
            if not dataset:
                return await self._handle_no_dataset()
            
            # 1. Dataset Information Requests
            if any(keyword in message_lower for keyword in ['columns', 'column names', 'what columns', 'available columns']):
                return await self._handle_column_list(dataset)
            
            if any(keyword in message_lower for keyword in ['dataset size', 'how many rows', 'shape', 'dimensions']):
                return await self._handle_dataset_info(dataset)
            
            if 'statistics' in message_lower or 'stats' in message_lower or 'summary' in message_lower:
                return await self._handle_statistics(dataset, message)
            
            if 'data type' in message_lower or 'dtype' in message_lower:
                return await self._handle_dtypes(dataset)
            
            if 'null' in message_lower or 'missing' in message_lower:
                return await self._handle_missing_values(dataset)
            
            if 'correlation' in message_lower:
                return await self._handle_correlation(dataset, message)
            
            # 2. Chart Creation Commands
            if any(keyword in message_lower for keyword in ['create chart', 'plot', 'visualize', 'show chart', 'draw']):
                return await self._handle_chart_creation(dataset, message, analysis_results)
            
            # 3. Model/Prediction Insights
            if analysis_results:
                if any(keyword in message_lower for keyword in ['prediction target', 'target variable', 'what am i predicting']):
                    return await self._handle_target_info(analysis_results)
                
                if any(keyword in message_lower for keyword in ['metrics', 'accuracy', 'performance', 'r2', 'rmse']):
                    return await self._handle_metrics(analysis_results)
                
                if any(keyword in message_lower for keyword in ['best model', 'top model', 'which model']):
                    return await self._handle_best_model(analysis_results)
                
                if 'feature importance' in message_lower or 'important features' in message_lower:
                    return await self._handle_feature_importance(analysis_results)
                
                if 'compare model' in message_lower:
                    return await self._handle_model_comparison(analysis_results)
            
            # 4. Analytical Assistance
            if 'anomaly' in message_lower or 'outlier' in message_lower:
                return await self._handle_anomaly_detection(dataset, message)
            
            if 'trend' in message_lower:
                return await self._handle_trend_analysis(dataset, message)
            
            if any(keyword in message_lower for keyword in ['what does this mean', 'interpret', 'explain']):
                return await self._handle_interpretation(dataset, analysis_results, message)
            
            if 'what next' in message_lower or 'suggestion' in message_lower or 'recommend' in message_lower:
                return await self._handle_suggestions(dataset, analysis_results)
            
            # 5. General Query - Use Azure OpenAI
            return await self._handle_general_query(message, dataset, analysis_results, conversation_history)
            
        except Exception as e:
            logger.error(f"Chat processing error: {str(e)}", exc_info=True)
            return {
                'response': f"I encountered an error processing your request: {str(e)}",
                'action': 'error',
                'data': {},
                'requires_confirmation': False,
                'suggestions': ['Try rephrasing your question', 'Ask about dataset columns', 'Request statistics']
            }
    
    async def _handle_no_dataset(self) -> Dict:
        """Handle chat when no dataset is loaded"""
        return {
            'response': "⚠️ No dataset is currently loaded. Please upload or select a dataset first to start analysis.",
            'action': 'message',
            'data': {},
            'requires_confirmation': False,
            'suggestions': [
                'Upload a CSV file',
                'Connect to a database',
                'Select an existing dataset'
            ]
        }
    
    async def _handle_column_list(self, dataset: pd.DataFrame) -> Dict:
        """List all available columns"""
        columns = list(dataset.columns)
        numeric_cols = dataset.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = dataset.select_dtypes(include=['object', 'category']).columns.tolist()
        
        response = f"📊 **Dataset Columns ({len(columns)} total)**\n\n"
        response += f"**Numeric columns ({len(numeric_cols)}):**\n{', '.join(numeric_cols[:15])}"
        if len(numeric_cols) > 15:
            response += f" ... and {len(numeric_cols) - 15} more"
        
        response += f"\n\n**Categorical columns ({len(categorical_cols)}):**\n{', '.join(categorical_cols[:10])}"
        if len(categorical_cols) > 10:
            response += f" ... and {len(categorical_cols) - 10} more"
        
        return {
            'response': response,
            'action': 'message',
            'data': {'columns': columns, 'numeric': numeric_cols, 'categorical': categorical_cols},
            'requires_confirmation': False,
            'suggestions': [
                f'Show statistics for {columns[0]}',
                'Check for missing values',
                f'Create a chart for {numeric_cols[0] if numeric_cols else columns[0]}'
            ]
        }
    
    async def _handle_dataset_info(self, dataset: pd.DataFrame) -> Dict:
        """Provide dataset size and shape info"""
        rows, cols = dataset.shape
        memory_mb = dataset.memory_usage(deep=True).sum() / 1024 / 1024
        
        response = f"📈 **Dataset Information**\n\n"
        response += f"• **Rows:** {rows:,}\n"
        response += f"• **Columns:** {cols}\n"
        response += f"• **Memory Usage:** {memory_mb:.2f} MB\n"
        response += f"• **Data Density:** {(1 - dataset.isnull().sum().sum() / (rows * cols)) * 100:.1f}% complete"
        
        return {
            'response': response,
            'action': 'message',
            'data': {'rows': rows, 'columns': cols, 'memory_mb': memory_mb},
            'requires_confirmation': False,
            'suggestions': [
                'Show column names',
                'Check for missing values',
                'Show summary statistics'
            ]
        }
    
    async def _handle_statistics(self, dataset: pd.DataFrame, message: str) -> Dict:
        """Provide statistical summary"""
        # Check if specific column mentioned
        columns = list(dataset.columns)
        target_col = None
        for col in columns:
            if col.lower() in message.lower():
                target_col = col
                break
        
        if target_col and target_col in dataset.select_dtypes(include=[np.number]).columns:
            # Stats for specific column
            col_data = dataset[target_col]
            stats = {
                'mean': col_data.mean(),
                'std': col_data.std(),
                'min': col_data.min(),
                'max': col_data.max(),
                'median': col_data.median(),
                'null_pct': (col_data.isnull().sum() / len(col_data)) * 100
            }
            
            response = f"📊 **Statistics for '{target_col}'**\n\n"
            response += f"• **Mean:** {stats['mean']:.2f}\n"
            response += f"• **Std Dev:** {stats['std']:.2f}\n"
            response += f"• **Min:** {stats['min']:.2f}\n"
            response += f"• **Max:** {stats['max']:.2f}\n"
            response += f"• **Median:** {stats['median']:.2f}\n"
            response += f"• **Missing:** {stats['null_pct']:.1f}%"
            
            return {
                'response': response,
                'action': 'message',
                'data': {'column': target_col, 'stats': stats},
                'requires_confirmation': False,
                'suggestions': [
                    f'Create histogram for {target_col}',
                    f'Check correlation with {target_col}',
                    'Show outliers'
                ]
            }
        else:
            # General statistics
            numeric_cols = dataset.select_dtypes(include=[np.number]).columns
            response = f"📊 **Dataset Statistics Summary**\n\n"
            response += f"**Numeric Columns:** {len(numeric_cols)}\n\n"
            
            for col in numeric_cols[:5]:
                mean_val = dataset[col].mean()
                response += f"• **{col}:** Mean = {mean_val:.2f}, Std = {dataset[col].std():.2f}\n"
            
            if len(numeric_cols) > 5:
                response += f"\n_...and {len(numeric_cols) - 5} more columns_"
            
            return {
                'response': response,
                'action': 'message',
                'data': {},
                'requires_confirmation': False,
                'suggestions': [
                    'Show correlation matrix',
                    'Check for outliers',
                    'Create visualizations'
                ]
            }
    
    async def _handle_dtypes(self, dataset: pd.DataFrame) -> Dict:
        """Show data types for all columns"""
        dtypes_dict = dataset.dtypes.astype(str).to_dict()
        
        # Group by type
        type_groups = {}
        for col, dtype in dtypes_dict.items():
            if dtype not in type_groups:
                type_groups[dtype] = []
            type_groups[dtype].append(col)
        
        response = f"🔤 **Column Data Types**\n\n"
        for dtype, cols in type_groups.items():
            response += f"**{dtype}** ({len(cols)} columns):\n"
            response += f"{', '.join(cols[:10])}\n"
            if len(cols) > 10:
                response += f"_...and {len(cols) - 10} more_\n"
            response += "\n"
        
        return {
            'response': response,
            'action': 'message',
            'data': {'dtypes': dtypes_dict},
            'requires_confirmation': False,
            'suggestions': [
                'Show numeric columns only',
                'Check for categorical columns',
                'Show statistics'
            ]
        }
    
    async def _handle_missing_values(self, dataset: pd.DataFrame) -> Dict:
        """Analyze missing values"""
        missing = dataset.isnull().sum()
        missing_pct = (missing / len(dataset)) * 100
        cols_with_missing = missing[missing > 0].sort_values(ascending=False)
        
        if len(cols_with_missing) == 0:
            response = "✅ Great news! No missing values found in the dataset."
        else:
            response = f"⚠️ **Missing Values Analysis**\n\n"
            response += f"**{len(cols_with_missing)} columns have missing values:**\n\n"
            
            for col in cols_with_missing.head(10).index:
                pct = missing_pct[col]
                count = missing[col]
                status = "🔴" if pct > 50 else "🟡" if pct > 10 else "🟢"
                response += f"{status} **{col}:** {count:,} missing ({pct:.1f}%)\n"
            
            if len(cols_with_missing) > 10:
                response += f"\n_...and {len(cols_with_missing) - 10} more columns with missing data_"
        
        return {
            'response': response,
            'action': 'message',
            'data': {'missing_columns': cols_with_missing.to_dict()},
            'requires_confirmation': False,
            'suggestions': [
                'Show columns with < 5% missing',
                'Recommend data cleaning strategy',
                'Visualize missing data patterns'
            ]
        }
    
    async def _handle_correlation(self, dataset: pd.DataFrame, message: str) -> Dict:
        """Calculate and display correlations"""
        numeric_cols = dataset.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {
                'response': "❌ Need at least 2 numeric columns to calculate correlations.",
                'action': 'message',
                'data': {},
                'requires_confirmation': False,
                'suggestions': ['Show column data types', 'Show dataset info']
            }
        
        # Check if specific column mentioned
        target_col = None
        for col in numeric_cols:
            if col.lower() in message.lower():
                target_col = col
                break
        
        if target_col:
            # Correlation with specific column
            correlations = dataset[numeric_cols].corrwith(dataset[target_col]).sort_values(ascending=False)
            correlations = correlations[correlations.index != target_col]  # Remove self-correlation
            
            response = f"🔗 **Correlations with '{target_col}'**\n\n"
            response += "**Top 5 positive correlations:**\n"
            for col, corr in correlations.head(5).items():
                response += f"• {col}: {corr:.3f}\n"
            
            response += "\n**Top 5 negative correlations:**\n"
            for col, corr in correlations.tail(5).items():
                response += f"• {col}: {corr:.3f}\n"
        else:
            # General correlation overview
            corr_matrix = dataset[numeric_cols].corr()
            
            # Find strongest correlations (excluding diagonal)
            corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    col1 = corr_matrix.columns[i]
                    col2 = corr_matrix.columns[j]
                    corr_val = corr_matrix.iloc[i, j]
                    corr_pairs.append((col1, col2, corr_val))
            
            corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
            
            response = f"🔗 **Correlation Analysis**\n\n"
            response += "**Strongest correlations:**\n"
            for col1, col2, corr in corr_pairs[:5]:
                response += f"• {col1} ↔ {col2}: {corr:.3f}\n"
        
        return {
            'response': response,
            'action': 'message',
            'data': {},
            'requires_confirmation': False,
            'suggestions': [
                'Create correlation heatmap',
                'Show scatter plot for top correlation',
                'Explain correlation values'
            ]
        }
    
    async def _handle_chart_creation(self, dataset: pd.DataFrame, message: str, analysis_results: Optional[Dict]) -> Dict:
        """Handle chart creation requests"""
        # This will be implemented in the next part
        # For now, return a placeholder
        return {
            'response': "📊 Chart creation feature is being enhanced. Use the 'Generate Visualizations' button for now.",
            'action': 'message',
            'data': {},
            'requires_confirmation': False,
            'suggestions': [
                'Click Generate Visualizations button',
                'Ask about dataset statistics',
                'Request correlation analysis'
            ]
        }
    
    async def _handle_general_query(self, message: str, dataset: Optional[pd.DataFrame], analysis_results: Optional[Dict], conversation_history: Optional[List[Dict]]) -> Dict:
        """Handle general questions using Azure OpenAI"""
        try:
            from app.services.azure_openai_service import get_azure_openai_service
            
            azure_service = get_azure_openai_service()
            
            if not azure_service.is_available():
                return {
                    'response': "I can help with specific data analysis tasks. Try asking about:\n• Dataset columns\n• Statistics\n• Missing values\n• Correlations\n• Model performance",
                    'action': 'message',
                    'data': {},
                    'requires_confirmation': False,
                    'suggestions': ['Show columns', 'Check statistics', 'Show missing values']
                }
            
            # Build context
            context = f"User question: {message}\n\n"
            context += f"Dataset context:\n"
            if dataset is not None:
                context += f"- Rows: {len(dataset)}, Columns: {len(dataset.columns)}\n"
                context += f"- Columns: {', '.join(list(dataset.columns)[:20])}\n"
            
            if analysis_results:
                context += f"- ML models trained: {len(analysis_results.get('ml_models', []))}\n"
                context += f"- Problem type: {analysis_results.get('problem_type', 'unknown')}\n"
            
            # Get AI response
            response = await azure_service.generate_completion(
                prompt=context,
                max_tokens=500,
                temperature=0.7
            )
            
            return {
                'response': response,
                'action': 'message',
                'data': {},
                'requires_confirmation': False,
                'suggestions': [
                    'Tell me more',
                    'Show me a chart',
                    'What else can I explore?'
                ]
            }
            
        except Exception as e:
            logger.error(f"Azure OpenAI query failed: {str(e)}")
            return {
                'response': "I can help with data analysis. Try asking specific questions like:\n• 'Show me column names'\n• 'What's the dataset size?'\n• 'Check for missing values'",
                'action': 'message',
                'data': {},
                'requires_confirmation': False,
                'suggestions': ['Show columns', 'Dataset info', 'Statistics']
            }
    
    # Placeholder methods for remaining handlers
    async def _handle_target_info(self, analysis_results: Dict) -> Dict:
        return {'response': 'Target info handler', 'action': 'message', 'data': {}, 'requires_confirmation': False, 'suggestions': []}
    
    async def _handle_metrics(self, analysis_results: Dict) -> Dict:
        return {'response': 'Metrics handler', 'action': 'message', 'data': {}, 'requires_confirmation': False, 'suggestions': []}
    
    async def _handle_best_model(self, analysis_results: Dict) -> Dict:
        return {'response': 'Best model handler', 'action': 'message', 'data': {}, 'requires_confirmation': False, 'suggestions': []}
    
    async def _handle_feature_importance(self, analysis_results: Dict) -> Dict:
        return {'response': 'Feature importance handler', 'action': 'message', 'data': {}, 'requires_confirmation': False, 'suggestions': []}
    
    async def _handle_model_comparison(self, analysis_results: Dict) -> Dict:
        return {'response': 'Model comparison handler', 'action': 'message', 'data': {}, 'requires_confirmation': False, 'suggestions': []}
    
    async def _handle_anomaly_detection(self, dataset: pd.DataFrame, message: str) -> Dict:
        return {'response': 'Anomaly detection handler', 'action': 'message', 'data': {}, 'requires_confirmation': False, 'suggestions': []}
    
    async def _handle_trend_analysis(self, dataset: pd.DataFrame, message: str) -> Dict:
        return {'response': 'Trend analysis handler', 'action': 'message', 'data': {}, 'requires_confirmation': False, 'suggestions': []}
    
    async def _handle_interpretation(self, dataset: Optional[pd.DataFrame], analysis_results: Optional[Dict], message: str) -> Dict:
        return {'response': 'Interpretation handler', 'action': 'message', 'data': {}, 'requires_confirmation': False, 'suggestions': []}
    
    async def _handle_suggestions(self, dataset: Optional[pd.DataFrame], analysis_results: Optional[Dict]) -> Dict:
        suggestions = []
        
        if dataset is not None:
            suggestions.append("Check for missing values and data quality issues")
            suggestions.append("Explore correlations between variables")
            suggestions.append("Create visualizations to understand distributions")
        
        if analysis_results:
            suggestions.append("Compare model performance metrics")
            suggestions.append("Analyze feature importance")
            suggestions.append("Review prediction accuracy")
        
        return {
            'response': f"💡 **Suggested Next Steps:**\n\n" + "\n".join([f"• {s}" for s in suggestions[:5]]),
            'action': 'message',
            'data': {},
            'requires_confirmation': False,
            'suggestions': suggestions[:3]
        }
