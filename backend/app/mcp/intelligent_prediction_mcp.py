"""
PROMISE AI - Intelligent Prediction MCP Tool (Enhanced)
Complete End-to-End ML Pipeline with User Prompts

This enhanced MCP tool provides:
1. User-driven model selection (choose specific models to train)
2. Natural language prompts (describe what you want to predict)
3. Automatic training on provided data
4. Predictions with confidence scores
5. Forecasting and trend analysis
6. AI-generated insights (domain-adaptive)
7. Feature importance analysis
8. Model comparison

Perfect for: "I want to predict customer churn based on purchase history, 
            train Random Forest and XGBoost, and get insights on what drives churn"
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
import logging

# ML Libraries
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, accuracy_score, precision_score, recall_score, f1_score

# Advanced models
try:
    from xgboost import XGBRegressor, XGBClassifier
    XGBOOST_AVAILABLE = True
except:
    XGBOOST_AVAILABLE = False

# Database connectors
import cx_Oracle
import pymongo
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


class IntelligentPredictionMCP:
    """
    Intelligent End-to-End ML Pipeline with User Control
    
    Example Usage:
        mcp = IntelligentPredictionMCP()
        
        result = mcp.train_and_predict(
            data_source={
                'type': 'file',
                'path': '/data/customers.csv'
            },
            user_prompt="I want to predict customer churn based on their purchase behavior and support tickets. Focus on identifying high-risk customers.",
            target_column='churned',
            feature_columns=['purchase_frequency', 'support_tickets', 'account_age_days'],
            models_to_train=['random_forest', 'xgboost', 'logistic_regression'],
            include_forecasting=True,
            include_insights=True
        )
    """
    
    # Available models
    REGRESSION_MODELS = {
        'linear_regression': LinearRegression,
        'random_forest': RandomForestRegressor,
        'decision_tree': DecisionTreeRegressor,
        'xgboost': XGBRegressor if XGBOOST_AVAILABLE else None
    }
    
    CLASSIFICATION_MODELS = {
        'logistic_regression': LogisticRegression,
        'random_forest': RandomForestClassifier,
        'decision_tree': DecisionTreeClassifier,
        'xgboost': XGBClassifier if XGBOOST_AVAILABLE else None
    }
    
    def __init__(self, chunk_size: int = 100000, output_dir: str = "/app/backend/models/mcp_models"):
        """
        Initialize Intelligent Prediction MCP
        
        Args:
            chunk_size: Number of rows to process at once
            output_dir: Directory to save trained models
        """
        self.chunk_size = chunk_size
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.supported_db_types = ['oracle', 'postgresql', 'mysql', 'mongodb']
        self.supported_file_types = ['.csv', '.xlsx', '.xls', '.parquet', '.json']
    
    def train_and_predict(
        self,
        data_source: Dict[str, Any],
        user_prompt: str,
        target_column: str,
        feature_columns: List[str],
        models_to_train: List[str] = None,
        problem_type: str = None,  # 'regression' or 'classification', auto-detect if None
        include_forecasting: bool = True,
        include_insights: bool = True,
        test_size: float = 0.2,
        domain: str = None  # e.g., 'it_infrastructure', 'finance', 'ecommerce'
    ) -> Dict[str, Any]:
        """
        Complete end-to-end ML pipeline with user control
        
        Args:
            data_source: Where to load data from
                - For file: {'type': 'file', 'path': '/data/file.csv'}
                - For database: {'type': 'oracle', 'config': {...}, 'table': 'customers'}
            user_prompt: Natural language description of prediction goal
            target_column: Column to predict
            feature_columns: Columns to use as features
            models_to_train: List of model names to train (default: all suitable models)
            problem_type: 'regression' or 'classification' (auto-detected if None)
            include_forecasting: Generate forecasts and trend analysis
            include_insights: Generate AI insights using user prompt
            test_size: Fraction of data for testing
            domain: Domain context for insights (auto-detected if None)
        
        Returns:
            {
                'training_summary': {...},
                'predictions': [...],
                'model_comparison': [{model_name, performance, ...}],
                'feature_importance': {...},
                'forecasting': {...},  # if include_forecasting=True
                'insights': {...},     # if include_insights=True
                'best_model': {...},
                'execution_time_seconds': float
            }
        """
        
        start_time = time.time()
        logger.info(f"🚀 Starting Intelligent Prediction Pipeline")
        logger.info(f"📝 User Prompt: {user_prompt}")
        
        # Step 1: Load data
        logger.info("📥 Step 1/7: Loading data...")
        df = self._load_data_from_source(data_source)
        logger.info(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns")
        
        # Step 2: Auto-detect problem type if not specified
        if problem_type is None:
            problem_type = self._detect_problem_type(df[target_column])
        logger.info(f"🔍 Problem Type: {problem_type}")
        
        # Step 3: Auto-detect domain if not specified
        if domain is None:
            domain = self._detect_domain(user_prompt, feature_columns)
        logger.info(f"🏷️  Domain: {domain}")
        
        # Step 4: Select models to train
        if models_to_train is None:
            models_to_train = self._get_default_models(problem_type)
        else:
            # Validate user-selected models
            models_to_train = self._validate_model_selection(models_to_train, problem_type)
        
        logger.info(f"🤖 Models to train: {', '.join(models_to_train)}")
        
        # Step 5: Prepare data
        logger.info("🔧 Step 2/7: Preprocessing data...")
        X_train, X_test, y_train, y_test, scaler, label_encoder = self._prepare_data(
            df, target_column, feature_columns, test_size, problem_type
        )
        
        # Step 6: Train models
        logger.info("🎯 Step 3/7: Training models...")
        trained_models = self._train_multiple_models(
            models_to_train, X_train, y_train, problem_type
        )
        
        # Step 7: Evaluate models
        logger.info("📊 Step 4/7: Evaluating models...")
        model_comparison = self._evaluate_models(
            trained_models, X_test, y_test, problem_type
        )
        
        # Step 8: Get best model
        best_model_info = max(model_comparison, key=lambda x: x['score'])
        best_model = trained_models[best_model_info['model_name']]
        logger.info(f"🏆 Best Model: {best_model_info['model_name']} (Score: {best_model_info['score']:.4f})")
        
        # Step 9: Feature importance
        logger.info("🔍 Step 5/7: Analyzing feature importance...")
        feature_importance = self._calculate_feature_importance(
            best_model, feature_columns
        )
        
        # Step 10: Make predictions on full dataset
        logger.info("🔮 Step 6/7: Making predictions on full dataset...")
        X_full = df[feature_columns]
        X_full_scaled = scaler.transform(X_full)
        predictions = best_model.predict(X_full_scaled)
        
        # Get confidence scores if available
        confidence_scores = None
        if hasattr(best_model, 'predict_proba'):
            proba = best_model.predict_proba(X_full_scaled)
            confidence_scores = np.max(proba, axis=1).tolist()
        
        # Decode predictions if classification
        if problem_type == 'classification' and label_encoder:
            predictions = label_encoder.inverse_transform(predictions)
        
        # Step 11: Generate forecasting
        forecasting_results = None
        if include_forecasting:
            logger.info("📈 Step 7a/7: Generating forecasts...")
            forecasting_results = self._generate_forecasting(
                df, target_column, feature_columns, predictions, user_prompt, domain
            )
        
        # Step 12: Generate insights
        insights_results = None
        if include_insights:
            logger.info("💡 Step 7b/7: Generating AI insights...")
            insights_results = self._generate_insights(
                user_prompt, model_comparison, feature_importance, 
                forecasting_results, domain, problem_type
            )
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        logger.info(f"✅ Pipeline complete in {execution_time:.1f}s")
        
        # Build comprehensive response
        result = {
            'training_summary': {
                'rows_processed': len(df),
                'features_used': feature_columns,
                'target_column': target_column,
                'problem_type': problem_type,
                'domain': domain,
                'models_trained': len(trained_models),
                'test_size': test_size,
                'user_prompt': user_prompt
            },
            'predictions': predictions.tolist() if hasattr(predictions, 'tolist') else list(predictions),
            'confidence_scores': confidence_scores,
            'model_comparison': model_comparison,
            'best_model': {
                'model_name': best_model_info['model_name'],
                'score': best_model_info['score'],
                'metrics': best_model_info['metrics'],
                'saved_path': str(self.output_dir / f"{best_model_info['model_name']}.pkl")
            },
            'feature_importance': feature_importance,
            'forecasting': forecasting_results,
            'insights': insights_results,
            'execution_time_seconds': execution_time,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save best model
        joblib.dump(best_model, self.output_dir / f"{best_model_info['model_name']}.pkl")
        joblib.dump(scaler, self.output_dir / "scaler.pkl")
        if label_encoder:
            joblib.dump(label_encoder, self.output_dir / "label_encoder.pkl")
        
        return result
    
    def _load_data_from_source(self, data_source: Dict) -> pd.DataFrame:
        """Load data from file or database"""
        source_type = data_source.get('type')
        
        if source_type == 'file':
            file_path = data_source['path']
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.csv':
                return pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                return pd.read_excel(file_path)
            elif file_ext == '.parquet':
                return pd.read_parquet(file_path)
            elif file_ext == '.json':
                return pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
        
        elif source_type in self.supported_db_types:
            # Load from database (chunked for large tables)
            config = data_source['config']
            table_name = data_source.get('table')
            query = data_source.get('query')
            
            if source_type == 'oracle':
                return self._load_from_oracle(config, table_name, query)
            elif source_type in ['postgresql', 'mysql']:
                return self._load_from_sql(source_type, config, table_name, query)
            elif source_type == 'mongodb':
                return self._load_from_mongodb(config, table_name)
        
        else:
            raise ValueError(f"Unsupported data source type: {source_type}")
    
    def _load_from_oracle(self, config, table_name, query):
        """Load data from Oracle"""
        dsn = cx_Oracle.makedsn(
            config['host'],
            config['port'],
            service_name=config['service_name']
        )
        conn = cx_Oracle.connect(
            user=config['username'],
            password=config['password'],
            dsn=dsn
        )
        
        if query:
            df = pd.read_sql(query, conn)
        else:
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        
        conn.close()
        return df
    
    def _load_from_sql(self, db_type, config, table_name, query):
        """Load data from PostgreSQL/MySQL"""
        engine_url = f"{db_type}://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        engine = create_engine(engine_url)
        
        if query:
            df = pd.read_sql(query, engine)
        else:
            df = pd.read_sql_table(table_name, engine)
        
        engine.dispose()
        return df
    
    def _load_from_mongodb(self, config, collection_name):
        """Load data from MongoDB"""
        client = pymongo.MongoClient(config['connection_string'])
        db = client[config['database']]
        collection = db[collection_name]
        
        data = list(collection.find())
        df = pd.DataFrame(data)
        
        client.close()
        return df
    
    def _detect_problem_type(self, target_series: pd.Series) -> str:
        """Auto-detect if regression or classification"""
        if target_series.dtype in ['object', 'category', 'bool']:
            return 'classification'
        
        unique_ratio = len(target_series.unique()) / len(target_series)
        if unique_ratio < 0.05:  # Less than 5% unique values
            return 'classification'
        
        return 'regression'
    
    def _detect_domain(self, user_prompt: str, feature_columns: List[str]) -> str:
        """Auto-detect domain from user prompt and features"""
        prompt_lower = user_prompt.lower()
        features_str = ' '.join(feature_columns).lower()
        combined = prompt_lower + ' ' + features_str
        
        if any(word in combined for word in ['latency', 'cpu', 'memory', 'server', 'slo', 'uptime', 'infrastructure']):
            return 'it_infrastructure'
        elif any(word in combined for word in ['revenue', 'sales', 'profit', 'price', 'stock', 'trading', 'finance']):
            return 'finance'
        elif any(word in combined for word in ['patient', 'diagnosis', 'treatment', 'healthcare', 'medical']):
            return 'healthcare'
        elif any(word in combined for word in ['customer', 'purchase', 'order', 'cart', 'ecommerce', 'retail']):
            return 'ecommerce'
        elif any(word in combined for word in ['food', 'recipe', 'meal', 'cuisine', 'restaurant']):
            return 'food'
        else:
            return 'general'
    
    def _get_default_models(self, problem_type: str) -> List[str]:
        """Get default models for problem type"""
        if problem_type == 'regression':
            models = ['linear_regression', 'random_forest', 'decision_tree']
            if XGBOOST_AVAILABLE:
                models.append('xgboost')
        else:
            models = ['logistic_regression', 'random_forest', 'decision_tree']
            if XGBOOST_AVAILABLE:
                models.append('xgboost')
        
        return models
    
    def _validate_model_selection(self, models: List[str], problem_type: str) -> List[str]:
        """Validate user-selected models"""
        available_models = self.REGRESSION_MODELS if problem_type == 'regression' else self.CLASSIFICATION_MODELS
        
        valid_models = []
        for model in models:
            if model in available_models and available_models[model] is not None:
                valid_models.append(model)
            else:
                logger.warning(f"Model '{model}' not available for {problem_type}, skipping")
        
        if not valid_models:
            logger.warning("No valid models selected, using defaults")
            return self._get_default_models(problem_type)
        
        return valid_models
    
    def _prepare_data(self, df, target_column, feature_columns, test_size, problem_type):
        """Prepare data for training"""
        X = df[feature_columns]
        y = df[target_column]
        
        # Handle missing values
        X = X.fillna(X.median(numeric_only=True))
        
        # Encode categorical target if classification
        label_encoder = None
        if problem_type == 'classification' and y.dtype == 'object':
            label_encoder = LabelEncoder()
            y = label_encoder.fit_transform(y)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=42
        )
        
        return X_train, X_test, y_train, y_test, scaler, label_encoder
    
    def _train_multiple_models(self, model_names, X_train, y_train, problem_type):
        """Train multiple models in parallel"""
        trained_models = {}
        model_dict = self.REGRESSION_MODELS if problem_type == 'regression' else self.CLASSIFICATION_MODELS
        
        for model_name in model_names:
            logger.info(f"  Training {model_name}...")
            model_class = model_dict[model_name]
            
            # Initialize model with appropriate parameters
            if 'random_forest' in model_name:
                model = model_class(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
            elif 'xgboost' in model_name:
                model = model_class(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
            else:
                model = model_class()
            
            # Train
            start = time.time()
            model.fit(X_train, y_train)
            training_time = time.time() - start
            
            trained_models[model_name] = {
                'model': model,
                'training_time': training_time
            }
            
            logger.info(f"  ✅ {model_name} trained in {training_time:.2f}s")
        
        return trained_models
    
    def _evaluate_models(self, trained_models, X_test, y_test, problem_type):
        """Evaluate all trained models"""
        results = []
        
        for model_name, model_info in trained_models.items():
            model = model_info['model']
            predictions = model.predict(X_test)
            
            if problem_type == 'regression':
                r2 = r2_score(y_test, predictions)
                rmse = np.sqrt(mean_squared_error(y_test, predictions))
                mae = mean_absolute_error(y_test, predictions)
                
                results.append({
                    'model_name': model_name,
                    'score': r2,
                    'metrics': {
                        'r2_score': float(r2),
                        'rmse': float(rmse),
                        'mae': float(mae)
                    },
                    'training_time': model_info['training_time']
                })
            else:
                accuracy = accuracy_score(y_test, predictions)
                precision = precision_score(y_test, predictions, average='weighted', zero_division=0)
                recall = recall_score(y_test, predictions, average='weighted', zero_division=0)
                f1 = f1_score(y_test, predictions, average='weighted', zero_division=0)
                
                results.append({
                    'model_name': model_name,
                    'score': accuracy,
                    'metrics': {
                        'accuracy': float(accuracy),
                        'precision': float(precision),
                        'recall': float(recall),
                        'f1_score': float(f1)
                    },
                    'training_time': model_info['training_time']
                })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def _calculate_feature_importance(self, model, feature_columns):
        """Calculate feature importance"""
        importance_dict = {}
        
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            # Normalize
            if importances.sum() > 0:
                importances = importances / importances.sum()
            
            for feat, imp in zip(feature_columns, importances):
                importance_dict[feat] = float(imp)
        
        elif hasattr(model, 'coef_'):
            coefs = np.abs(model.coef_)
            if len(coefs.shape) > 1:
                coefs = coefs.mean(axis=0)
            
            # Normalize
            if coefs.sum() > 0:
                coefs = coefs / coefs.sum()
            
            for feat, coef in zip(feature_columns, coefs):
                importance_dict[feat] = float(coef)
        
        # Sort by importance
        importance_dict = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        
        return importance_dict
    
    def _generate_forecasting(self, df, target_column, feature_columns, predictions, user_prompt, domain):
        """Generate forecasting and trend analysis"""
        # Calculate basic statistics
        actual_values = df[target_column].values
        predicted_mean = np.mean(predictions)
        actual_mean = np.mean(actual_values)
        trend_direction = "increasing" if predicted_mean > actual_mean else "decreasing"
        trend_magnitude = abs(predicted_mean - actual_mean) / actual_mean * 100
        
        # Detect high-risk predictions (top 10%)
        threshold = np.percentile(predictions, 90) if trend_direction == "increasing" else np.percentile(predictions, 10)
        high_risk_count = np.sum(predictions >= threshold) if trend_direction == "increasing" else np.sum(predictions <= threshold)
        
        forecasting = {
            'summary': f"Predictions show {trend_direction} trend of {trend_magnitude:.1f}% compared to historical average",
            'statistics': {
                'predicted_mean': float(predicted_mean),
                'predicted_median': float(np.median(predictions)),
                'predicted_std': float(np.std(predictions)),
                'predicted_min': float(np.min(predictions)),
                'predicted_max': float(np.max(predictions)),
                'actual_mean': float(actual_mean),
                'trend_direction': trend_direction,
                'trend_magnitude_percent': float(trend_magnitude)
            },
            'alerts': [
                {
                    'level': 'warning' if high_risk_count > len(predictions) * 0.1 else 'info',
                    'message': f"{high_risk_count} ({high_risk_count/len(predictions)*100:.1f}%) predictions flagged as high-risk",
                    'threshold': float(threshold)
                }
            ],
            'recommendations': self._generate_recommendations(trend_direction, trend_magnitude, domain)
        }
        
        return forecasting
    
    def _generate_recommendations(self, trend_direction, trend_magnitude, domain):
        """Generate domain-specific recommendations"""
        recommendations = []
        
        if domain == 'it_infrastructure':
            if trend_direction == 'increasing' and trend_magnitude > 10:
                recommendations.append("Consider scaling infrastructure resources to handle predicted load increase")
                recommendations.append("Implement monitoring alerts for early warning signs")
            elif trend_direction == 'decreasing':
                recommendations.append("System performance improving - consider documenting best practices")
        
        elif domain == 'ecommerce':
            if trend_direction == 'increasing':
                recommendations.append("High churn risk detected - implement retention campaigns")
                recommendations.append("Analyze feedback from high-risk customers")
            else:
                recommendations.append("Churn trending down - current strategies are working")
        
        elif domain == 'finance':
            if trend_magnitude > 15:
                recommendations.append("Significant volatility detected - review risk management policies")
                recommendations.append("Consider diversification strategies")
        
        else:
            recommendations.append(f"Monitor trend closely - {trend_direction} by {trend_magnitude:.1f}%")
        
        return recommendations
    
    def _generate_insights(self, user_prompt, model_comparison, feature_importance, forecasting, domain, problem_type):
        """Generate AI insights (simplified - would use Azure OpenAI in production)"""
        best_model = model_comparison[0]
        top_features = list(feature_importance.items())[:3]
        
        insights = {
            'summary': f"Based on your goal to '{user_prompt}', the {best_model['model_name']} model performs best with a {'R²' if problem_type == 'regression' else 'accuracy'} score of {best_model['score']:.4f}.",
            'key_findings': [
                f"Top 3 most influential features: {', '.join([f'{feat} ({imp*100:.1f}%)' for feat, imp in top_features])}",
                f"Model comparison: {len(model_comparison)} models tested, {best_model['model_name']} outperforms others",
                f"Prediction quality: {'High' if best_model['score'] > 0.8 else 'Moderate' if best_model['score'] > 0.6 else 'Needs improvement'}"
            ],
            'domain_context': domain,
            'user_prompt': user_prompt
        }
        
        if forecasting:
            insights['key_findings'].append(f"Forecast trend: {forecasting['statistics']['trend_direction']} by {forecasting['statistics']['trend_magnitude_percent']:.1f}%")
        
        return insights


# Example usage
if __name__ == "__main__":
    mcp = IntelligentPredictionMCP()
    
    # Example: Predict customer churn
    result = mcp.train_and_predict(
        data_source={
            'type': 'file',
            'path': '/data/customers.csv'
        },
        user_prompt="I want to predict which customers are likely to churn based on their purchase behavior, support interactions, and account history. Focus on identifying actionable patterns.",
        target_column='churned',
        feature_columns=['purchase_frequency', 'support_tickets', 'account_age_days', 'last_purchase_days'],
        models_to_train=['random_forest', 'xgboost', 'logistic_regression'],
        include_forecasting=True,
        include_insights=True,
        domain='ecommerce'
    )
    
    print(f"✅ Best Model: {result['best_model']['model_name']}")
    print(f"📊 Score: {result['best_model']['score']:.4f}")
    print(f"💡 Insight: {result['insights']['summary']}")
    print(f"📈 Forecast: {result['forecasting']['summary']}")
