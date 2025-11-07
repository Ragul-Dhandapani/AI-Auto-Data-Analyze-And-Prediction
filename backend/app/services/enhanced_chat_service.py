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
        """Handle chart creation requests with Azure OpenAI intelligence"""
        try:
            from app.services.azure_openai_service import get_azure_openai_service
            import plotly.graph_objects as go
            import plotly.express as px
            
            azure_service = get_azure_openai_service()
            
            # Parse chart request using Azure OpenAI
            chart_config = await self._parse_chart_request_with_ai(message, dataset, azure_service)
            
            if not chart_config:
                return {
                    'response': "❌ I couldn't understand the chart request. Please try something like:\n• 'Create a scatter plot of price vs quantity'\n• 'Show histogram for revenue'\n• 'Plot latency over time'",
                    'action': 'message',
                    'data': {},
                    'requires_confirmation': False,
                    'suggestions': [
                        'Show me available columns',
                        'Create a chart for the first numeric column',
                        'Generate visualizations automatically'
                    ]
                }
            
            # Validate columns exist
            missing_cols = []
            if chart_config.get('x_col') and chart_config['x_col'] not in dataset.columns:
                missing_cols.append(chart_config['x_col'])
            if chart_config.get('y_col') and chart_config['y_col'] not in dataset.columns:
                missing_cols.append(chart_config['y_col'])
            
            if missing_cols:
                available = ', '.join(list(dataset.columns)[:10])
                return {
                    'response': f"❌ Column(s) not found: {', '.join(missing_cols)}\n\n**Available columns:**\n{available}",
                    'action': 'message',
                    'data': {'available_columns': list(dataset.columns)},
                    'requires_confirmation': False,
                    'suggestions': [
                        'Show all column names',
                        f'Create chart with {dataset.columns[0]}',
                        'Check data types'
                    ]
                }
            
            # Generate the chart
            fig = None
            chart_type = chart_config.get('chart_type', 'scatter')
            
            try:
                if chart_type == 'scatter' and chart_config.get('x_col') and chart_config.get('y_col'):
                    fig = px.scatter(dataset, x=chart_config['x_col'], y=chart_config['y_col'],
                                    title=f"{chart_config['y_col']} vs {chart_config['x_col']}")
                
                elif chart_type == 'line' and chart_config.get('x_col') and chart_config.get('y_col'):
                    fig = px.line(dataset, x=chart_config['x_col'], y=chart_config['y_col'],
                                 title=f"{chart_config['y_col']} over {chart_config['x_col']}")
                
                elif chart_type == 'bar' and chart_config.get('x_col') and chart_config.get('y_col'):
                    fig = px.bar(dataset, x=chart_config['x_col'], y=chart_config['y_col'],
                                title=f"{chart_config['y_col']} by {chart_config['x_col']}")
                
                elif chart_type == 'histogram' and chart_config.get('x_col'):
                    fig = px.histogram(dataset, x=chart_config['x_col'],
                                      title=f"Distribution of {chart_config['x_col']}")
                
                elif chart_type == 'box' and chart_config.get('y_col'):
                    fig = px.box(dataset, y=chart_config['y_col'],
                                title=f"Box Plot of {chart_config['y_col']}")
                
                elif chart_type == 'pie' and chart_config.get('x_col'):
                    # Count occurrences for pie chart
                    value_counts = dataset[chart_config['x_col']].value_counts().head(10)
                    fig = px.pie(values=value_counts.values, names=value_counts.index,
                                title=f"Distribution of {chart_config['x_col']}")
                
                else:
                    return {
                        'response': f"❌ Unable to create {chart_type} chart with the specified columns.",
                        'action': 'message',
                        'data': {},
                        'requires_confirmation': False,
                        'suggestions': ['Try a different chart type', 'Show available columns']
                    }
                
                if fig:
                    # Convert to plotly JSON format
                    chart_data = {
                        'data': fig.data,
                        'layout': fig.layout
                    }
                    
                    # Ask for confirmation to append to dashboard
                    return {
                        'response': f"✅ Created {chart_type} chart successfully!\n\n**Do you want to append this chart to the dashboard?**",
                        'action': 'chart',
                        'data': chart_data,
                        'requires_confirmation': True,
                        'suggestions': [
                            'Yes, append to dashboard',
                            'No, just show it here',
                            'Create another chart'
                        ]
                    }
            
            except Exception as e:
                logger.error(f"Chart generation error: {str(e)}")
                return {
                    'response': f"❌ Error creating chart: {str(e)}",
                    'action': 'message',
                    'data': {},
                    'requires_confirmation': False,
                    'suggestions': ['Try simpler chart request', 'Check column names']
                }
                
        except Exception as e:
            logger.error(f"Chart creation handler error: {str(e)}", exc_info=True)
            return {
                'response': f"❌ Chart creation failed: {str(e)}",
                'action': 'message',
                'data': {},
                'requires_confirmation': False,
                'suggestions': []
            }
    
    async def _parse_chart_request_with_ai(self, message: str, dataset: pd.DataFrame, azure_service) -> Optional[Dict]:
        """Use Azure OpenAI to parse natural language chart requests"""
        try:
            columns_list = ', '.join(list(dataset.columns)[:30])
            numeric_cols = ', '.join(dataset.select_dtypes(include=[np.number]).columns.tolist()[:20])
            
            prompt = f"""You are a data visualization expert. Parse this chart request into structured format.

User request: "{message}"

Available columns: {columns_list}
Numeric columns: {numeric_cols}

Identify:
1. Chart type (scatter, line, bar, histogram, box, pie)
2. X-axis column (if applicable)
3. Y-axis column (if applicable)

Respond with ONLY a JSON object:
{{
    "chart_type": "scatter|line|bar|histogram|box|pie",
    "x_col": "column_name or null",
    "y_col": "column_name or null"
}}

Match column names exactly from the available list. Handle typos and variations intelligently."""

            if azure_service.is_available():
                response = await azure_service.generate_completion(
                    prompt=prompt,
                    max_tokens=200,
                    temperature=0.3
                )
                
                # Parse JSON from response
                import json
                import re
                
                # Extract JSON from response (handle markdown code blocks)
                json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
                if json_match:
                    chart_config = json.loads(json_match.group())
                    return chart_config
            
            # Fallback to pattern matching
            return self._parse_chart_fallback(message, dataset)
            
        except Exception as e:
            logger.error(f"AI chart parsing error: {str(e)}")
            return self._parse_chart_fallback(message, dataset)
    
    def _parse_chart_fallback(self, message: str, dataset: pd.DataFrame) -> Optional[Dict]:
        """Fallback pattern matching for chart requests"""
        message_lower = message.lower()
        columns = list(dataset.columns)
        numeric_cols = dataset.select_dtypes(include=[np.number]).columns.tolist()
        
        # Detect chart type
        chart_type = 'scatter'
        if 'histogram' in message_lower or 'distribution' in message_lower:
            chart_type = 'histogram'
        elif 'line' in message_lower or 'over time' in message_lower or 'trend' in message_lower:
            chart_type = 'line'
        elif 'bar' in message_lower or 'by' in message_lower:
            chart_type = 'bar'
        elif 'box' in message_lower or 'outlier' in message_lower:
            chart_type = 'box'
        elif 'pie' in message_lower:
            chart_type = 'pie'
        
        # Find columns mentioned in message
        x_col = None
        y_col = None
        
        for col in columns:
            col_lower = col.lower().replace('_', ' ')
            if col_lower in message_lower or col.lower() in message_lower:
                if x_col is None:
                    x_col = col
                elif y_col is None:
                    y_col = col
                    break
        
        # For single column charts
        if chart_type in ['histogram', 'box', 'pie'] and x_col:
            return {'chart_type': chart_type, 'x_col': x_col, 'y_col': None}
        
        # For two-column charts
        if chart_type in ['scatter', 'line', 'bar'] and x_col and y_col:
            return {'chart_type': chart_type, 'x_col': x_col, 'y_col': y_col}
        
        # Default: use first two numeric columns for scatter
        if len(numeric_cols) >= 2:
            return {'chart_type': 'scatter', 'x_col': numeric_cols[0], 'y_col': numeric_cols[1]}
        
        return None
    
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
        """Show current prediction target"""
        ml_models = analysis_results.get('ml_models', [])
        if not ml_models:
            return {
                'response': "❌ No models have been trained yet. Run Predictive Analysis first.",
                'action': 'message',
                'data': {},
                'requires_confirmation': False,
                'suggestions': ['Train models', 'Select target variable']
            }
        
        # Get target from first model
        target = ml_models[0].get('target_column', 'Unknown')
        problem_type = analysis_results.get('problem_type', 'unknown')
        
        response = f"🎯 **Current Prediction Target**\n\n"
        response += f"• **Target Variable:** {target}\n"
        response += f"• **Problem Type:** {problem_type.capitalize()}\n"
        response += f"• **Models Trained:** {len(ml_models)}"
        
        return {
            'response': response,
            'action': 'message',
            'data': {'target': target, 'problem_type': problem_type},
            'requires_confirmation': False,
            'suggestions': [
                'Show model metrics',
                'Which model is best?',
                'Show feature importance'
            ]
        }
    
    async def _handle_metrics(self, analysis_results: Dict) -> Dict:
        """Display model evaluation metrics"""
        ml_models = analysis_results.get('ml_models', [])
        if not ml_models:
            return {
                'response': "❌ No models trained yet. Train models first to see metrics.",
                'action': 'message',
                'data': {},
                'requires_confirmation': False,
                'suggestions': ['Start training']
            }
        
        problem_type = analysis_results.get('problem_type', 'unknown')
        response = f"📊 **Model Performance Metrics**\n\n"
        
        for i, model in enumerate(ml_models[:5], 1):
            model_name = model.get('model_name', 'Unknown')
            response += f"**{i}. {model_name}**"
            if model.get('is_best'):
                response += " 🏆"
            response += "\n"
            
            if problem_type == 'regression':
                response += f"   • R² Score: {model.get('r2_score', 0):.4f}\n"
                response += f"   • RMSE: {model.get('rmse', 0):.2f}\n"
                response += f"   • MAE: {model.get('mae', 0):.2f}\n"
            else:
                response += f"   • Accuracy: {model.get('accuracy', 0):.4f}\n"
                response += f"   • F1 Score: {model.get('f1_score', 0):.4f}\n"
                response += f"   • Precision: {model.get('precision', 0):.4f}\n"
            response += "\n"
        
        if len(ml_models) > 5:
            response += f"_...and {len(ml_models) - 5} more models_"
        
        return {
            'response': response,
            'action': 'message',
            'data': {'models': ml_models},
            'requires_confirmation': False,
            'suggestions': [
                'Show best model',
                'Compare top 3 models',
                'Show feature importance'
            ]
        }
    
    async def _handle_best_model(self, analysis_results: Dict) -> Dict:
        """Identify and describe the best performing model"""
        ml_models = analysis_results.get('ml_models', [])
        best_model = next((m for m in ml_models if m.get('is_best')), None)
        
        if not best_model:
            best_model = ml_models[0] if ml_models else None
        
        if not best_model:
            return {
                'response': "❌ No models available to compare.",
                'action': 'message',
                'data': {},
                'requires_confirmation': False,
                'suggestions': []
            }
        
        model_name = best_model.get('model_name', 'Unknown')
        problem_type = analysis_results.get('problem_type', 'unknown')
        
        response = f"🏆 **Best Model: {model_name}**\n\n"
        
        if problem_type == 'regression':
            r2 = best_model.get('r2_score', 0)
            rmse = best_model.get('rmse', 0)
            response += f"• **R² Score:** {r2:.4f} (explains {r2*100:.1f}% of variance)\n"
            response += f"• **RMSE:** {rmse:.2f}\n"
            response += f"• **MAE:** {best_model.get('mae', 0):.2f}\n"
        else:
            acc = best_model.get('accuracy', 0)
            response += f"• **Accuracy:** {acc:.4f} ({acc*100:.1f}% correct predictions)\n"
            response += f"• **F1 Score:** {best_model.get('f1_score', 0):.4f}\n"
            response += f"• **Precision:** {best_model.get('precision', 0):.4f}\n"
        
        response += f"\n💡 **Why {model_name}?**\n"
        response += f"This model achieved the highest performance among {len(ml_models)} models tested."
        
        return {
            'response': response,
            'action': 'message',
            'data': {'best_model': best_model},
            'requires_confirmation': False,
            'suggestions': [
                'Compare with other models',
                'Show feature importance',
                'Explain this model'
            ]
        }
    
    async def _handle_feature_importance(self, analysis_results: Dict) -> Dict:
        """Show feature importance ranking"""
        feature_importance = analysis_results.get('feature_importance', {})
        
        if not feature_importance:
            return {
                'response': "❌ Feature importance data not available for this analysis.",
                'action': 'message',
                'data': {},
                'requires_confirmation': False,
                'suggestions': ['Show model metrics', 'Show best model']
            }
        
        # Sort by importance
        sorted_features = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)
        
        response = f"🎯 **Feature Importance Rankings**\n\n"
        response += "Top features driving predictions:\n\n"
        
        for i, (feature, importance) in enumerate(sorted_features[:10], 1):
            bar_length = int(importance * 20)
            bar = "█" * bar_length
            response += f"{i}. **{feature}**: {importance:.3f} {bar}\n"
        
        if len(sorted_features) > 10:
            response += f"\n_...and {len(sorted_features) - 10} more features_"
        
        return {
            'response': response,
            'action': 'message',
            'data': {'feature_importance': dict(sorted_features)},
            'requires_confirmation': False,
            'suggestions': [
                f'Show correlation with {sorted_features[0][0]}',
                'Create feature importance chart',
                'Explain top features'
            ]
        }
    
    async def _handle_model_comparison(self, analysis_results: Dict) -> Dict:
        """Compare multiple models"""
        ml_models = analysis_results.get('ml_models', [])
        if len(ml_models) < 2:
            return {
                'response': "❌ Need at least 2 models to compare. Train more models first.",
                'action': 'message',
                'data': {},
                'requires_confirmation': False,
                'suggestions': []
            }
        
        problem_type = analysis_results.get('problem_type', 'unknown')
        response = f"📊 **Model Comparison**\n\n"
        
        # Sort by performance
        if problem_type == 'regression':
            sorted_models = sorted(ml_models, key=lambda x: x.get('r2_score', 0), reverse=True)
            metric = 'R² Score'
        else:
            sorted_models = sorted(ml_models, key=lambda x: x.get('accuracy', 0), reverse=True)
            metric = 'Accuracy'
        
        response += f"Ranking by {metric}:\n\n"
        
        for i, model in enumerate(sorted_models[:10], 1):
            name = model.get('model_name', 'Unknown')
            score = model.get('r2_score' if problem_type == 'regression' else 'accuracy', 0)
            
            response += f"{i}. **{name}**: {score:.4f}"
            if i == 1:
                response += " 🏆"
            response += "\n"
        
        return {
            'response': response,
            'action': 'message',
            'data': {'sorted_models': sorted_models},
            'requires_confirmation': False,
            'suggestions': [
                'Show best model details',
                'Create comparison chart',
                'Show metrics for all models'
            ]
        }
    
    async def _handle_anomaly_detection(self, dataset: pd.DataFrame, message: str) -> Dict:
        """Detect anomalies/outliers in data"""
        numeric_cols = dataset.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return {
                'response': "❌ No numeric columns found for anomaly detection.",
                'action': 'message',
                'data': {},
                'requires_confirmation': False,
                'suggestions': []
            }
        
        # Use IQR method for outlier detection
        outliers_summary = {}
        
        for col in numeric_cols[:10]:  # Limit to first 10 columns
            Q1 = dataset[col].quantile(0.25)
            Q3 = dataset[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = dataset[(dataset[col] < lower_bound) | (dataset[col] > upper_bound)]
            outlier_count = len(outliers)
            outlier_pct = (outlier_count / len(dataset)) * 100
            
            if outlier_count > 0:
                outliers_summary[col] = {
                    'count': outlier_count,
                    'percentage': outlier_pct
                }
        
        response = f"🔍 **Anomaly Detection Results**\n\n"
        
        if not outliers_summary:
            response += "✅ No significant outliers detected using IQR method."
        else:
            response += f"Found outliers in {len(outliers_summary)} columns:\n\n"
            
            for col, info in list(outliers_summary.items())[:5]:
                status = "🔴" if info['percentage'] > 10 else "🟡" if info['percentage'] > 5 else "🟢"
                response += f"{status} **{col}:** {info['count']:,} outliers ({info['percentage']:.1f}%)\n"
        
        return {
            'response': response,
            'action': 'message',
            'data': {'outliers': outliers_summary},
            'requires_confirmation': False,
            'suggestions': [
                'Visualize outliers',
                'Remove outliers',
                'Show statistics excluding outliers'
            ]
        }
    
    async def _handle_trend_analysis(self, dataset: pd.DataFrame, message: str) -> Dict:
        """Analyze trends over time"""
        # Look for date/time columns
        date_cols = []
        for col in dataset.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                date_cols.append(col)
        
        if not date_cols:
            return {
                'response': "❌ No date/time columns found in the dataset. Add a datetime column for trend analysis.",
                'action': 'message',
                'data': {},
                'requires_confirmation': False,
                'suggestions': ['Show column names', 'Check data types']
            }
        
        response = f"📈 **Trend Analysis**\n\n"
        response += f"Found {len(date_cols)} temporal column(s): {', '.join(date_cols)}\n\n"
        response += "💡 To analyze trends:\n"
        response += "• Use Time Series Analysis tab\n"
        response += "• Specify target variable for forecasting\n"
        response += "• Choose Prophet or LSTM method"
        
        return {
            'response': response,
            'action': 'message',
            'data': {'date_columns': date_cols},
            'requires_confirmation': False,
            'suggestions': [
                'Go to Time Series tab',
                'Show me date column values',
                'Create time series chart'
            ]
        }
    
    async def _handle_interpretation(self, dataset: Optional[pd.DataFrame], analysis_results: Optional[Dict], message: str) -> Dict:
        """Interpret results or charts using Azure OpenAI"""
        try:
            from app.services.azure_openai_service import get_azure_openai_service
            
            azure_service = get_azure_openai_service()
            
            if not azure_service.is_available():
                return {
                    'response': "Interpretation requires Azure OpenAI. Please check configuration.",
                    'action': 'message',
                    'data': {},
                    'requires_confirmation': False,
                    'suggestions': []
                }
            
            # Build context
            context = f"User asked for interpretation: {message}\n\n"
            
            if analysis_results:
                ml_models = analysis_results.get('ml_models', [])
                if ml_models:
                    best = next((m for m in ml_models if m.get('is_best')), ml_models[0])
                    context += f"Best model: {best.get('model_name')}\n"
                    context += f"Performance: {best.get('r2_score', best.get('accuracy', 0)):.3f}\n"
            
            context += "\nProvide a clear, business-friendly interpretation in 2-3 sentences."
            
            interpretation = await azure_service.generate_completion(
                prompt=context,
                max_tokens=300,
                temperature=0.7
            )
            
            return {
                'response': f"💡 **Interpretation:**\n\n{interpretation}",
                'action': 'message',
                'data': {},
                'requires_confirmation': False,
                'suggestions': ['Tell me more', 'What should I do next?']
            }
            
        except Exception as e:
            logger.error(f"Interpretation failed: {str(e)}")
            return {
                'response': "I can help interpret results. Please be more specific about what you'd like me to explain.",
                'action': 'message',
                'data': {},
                'requires_confirmation': False,
                'suggestions': []
            }
    
    async def _handle_suggestions(self, dataset: Optional[pd.DataFrame], analysis_results: Optional[Dict]) -> Dict:
        """Provide smart analytical suggestions"""
        suggestions = []
        
        if dataset is not None:
            # Check data quality
            null_pct = (dataset.isnull().sum().sum() / (len(dataset) * len(dataset.columns))) * 100
            if null_pct > 5:
                suggestions.append("🔴 Address missing values (data is {:.1f}% incomplete)".format(null_pct))
            
            # Check for numeric columns
            numeric_cols = dataset.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                suggestions.append("📊 Explore correlations between numeric variables")
            
            # Check for outliers
            suggestions.append("🔍 Run anomaly detection to identify outliers")
            
            # Suggest visualizations
            suggestions.append("📈 Create visualizations to understand distributions")
        
        if analysis_results and analysis_results.get('ml_models'):
            suggestions.append("🏆 Review best performing model")
            suggestions.append("🎯 Analyze feature importance")
            suggestions.append("📊 Compare model performance")
        
        if not analysis_results or not analysis_results.get('ml_models'):
            suggestions.append("🚀 Train ML models for predictions")
        
        response = f"💡 **Recommended Next Steps:**\n\n"
        response += "\n".join([f"{i+1}. {s}" for i, s in enumerate(suggestions[:5])])
        
        return {
            'response': response,
            'action': 'message',
            'data': {},
            'requires_confirmation': False,
            'suggestions': [s.split(']')[-1].split(')')[0].strip() if ']' in s or ')' in s else s.replace('🔴 ', '').replace('📊 ', '').replace('🔍 ', '')[:50] for s in suggestions[:3]]
        }
