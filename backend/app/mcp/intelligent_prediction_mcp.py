"""
Intelligent Prediction MCP - Complete ML Pipeline with User Control
Includes: Training, Prediction, Forecasting, and Insights
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from typing import Dict, List, Any
import time
from datetime import datetime
import logging

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, accuracy_score

try:
    from xgboost import XGBRegressor, XGBClassifier
    XGBOOST_AVAILABLE = True
except:
    XGBOOST_AVAILABLE = False

import cx_Oracle
import pymongo
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)

class IntelligentPredictionMCP:
    """Enhanced MCP with user prompt, model selection, forecasting & insights"""
    
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
    
    def __init__(self, output_dir="/app/backend/models/mcp_models"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def train_and_predict(
        self,
        data_source: Dict[str, Any],
        user_prompt: str,
        target_column: str,
        feature_columns: List[str],
        models_to_train: List[str] = None,
        problem_type: str = None,
        include_forecasting: bool = True,
        include_insights: bool = True,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """
        Complete ML pipeline with user control
        
        Returns: predictions, forecasting, insights, model comparison
        """
        start_time = time.time()
        logger.info(f"🚀 Pipeline: {user_prompt}")
        
        # Load data
        df = self._load_data(data_source)
        logger.info(f"✅ Loaded {len(df):,} rows")
        
        # Auto-detect problem type
        if not problem_type:
            problem_type = 'classification' if df[target_column].nunique() / len(df) < 0.05 else 'regression'
        
        # Auto-detect domain
        domain = self._detect_domain(user_prompt, feature_columns)
        
        # Select models
        if not models_to_train:
            models_to_train = ['random_forest', 'xgboost'] if XGBOOST_AVAILABLE else ['random_forest']
        
        # Prepare data
        X_train, X_test, y_train, y_test, scaler, le = self._prepare_data(
            df, target_column, feature_columns, test_size, problem_type
        )
        
        # Train models
        trained = self._train_models(models_to_train, X_train, y_train, problem_type)
        
        # Evaluate
        comparison = self._evaluate(trained, X_test, y_test, problem_type)
        
        # Best model
        best = max(comparison, key=lambda x: x['score'])
        best_model = trained[best['model_name']]['model']
        
        # Feature importance
        feat_imp = self._feature_importance(best_model, feature_columns)
        
        # Predict
        X_full = scaler.transform(df[feature_columns].fillna(df[feature_columns].median()))
        predictions = best_model.predict(X_full)
        
        # Forecasting
        forecasting = None
        if include_forecasting:
            forecasting = self._forecast(df[target_column].values, predictions, domain)
        
        # Insights
        insights = None
        if include_insights:
            insights = self._insights(user_prompt, best, feat_imp, forecasting, domain)
        
        # Save model
        joblib.dump(best_model, self.output_dir / f"{best['model_name']}.pkl")
        
        return {
            'training_summary': {
                'rows': len(df),
                'problem_type': problem_type,
                'domain': domain,
                'user_prompt': user_prompt
            },
            'predictions': predictions.tolist(),
            'model_comparison': comparison,
            'best_model': best,
            'feature_importance': feat_imp,
            'forecasting': forecasting,
            'insights': insights,
            'execution_time': time.time() - start_time
        }
    
    def _load_data(self, source):
        """Load from file or database"""
        if source['type'] == 'file':
            return pd.read_csv(source['path'])
        elif source['type'] == 'oracle':
            conn = cx_Oracle.connect(
                user=source['config']['username'],
                password=source['config']['password'],
                dsn=cx_Oracle.makedsn(source['config']['host'], 
                                      source['config']['port'],
                                      service_name=source['config']['service_name'])
            )
            df = pd.read_sql(f"SELECT * FROM {source['table']}", conn)
            conn.close()
            return df
        # Add other DB types as needed
    
    def _detect_domain(self, prompt, features):
        """Auto-detect domain"""
        text = (prompt + ' ' + ' '.join(features)).lower()
        if any(w in text for w in ['latency', 'cpu', 'memory', 'server']):
            return 'it_infrastructure'
        elif any(w in text for w in ['churn', 'customer', 'purchase']):
            return 'ecommerce'
        return 'general'
    
    def _prepare_data(self, df, target, features, test_size, prob_type):
        """Prepare and split data"""
        X = df[features].fillna(df[features].median())
        y = df[target]
        
        le = None
        if prob_type == 'classification' and y.dtype == 'object':
            le = LabelEncoder()
            y = le.fit_transform(y)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        return (*train_test_split(X_scaled, y, test_size=test_size, random_state=42), scaler, le)
    
    def _train_models(self, names, X_train, y_train, prob_type):
        """Train multiple models"""
        trained = {}
        models = self.REGRESSION_MODELS if prob_type == 'regression' else self.CLASSIFICATION_MODELS
        
        for name in names:
            if models.get(name):
                if 'random_forest' in name:
                    model = models[name](n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
                elif 'xgboost' in name:
                    model = models[name](n_estimators=100, max_depth=6, random_state=42)
                else:
                    model = models[name]()
                
                start = time.time()
                model.fit(X_train, y_train)
                trained[name] = {'model': model, 'time': time.time() - start}
        
        return trained
    
    def _evaluate(self, trained, X_test, y_test, prob_type):
        """Evaluate models"""
        results = []
        for name, info in trained.items():
            pred = info['model'].predict(X_test)
            
            if prob_type == 'regression':
                score = r2_score(y_test, pred)
                metrics = {
                    'r2_score': float(score),
                    'rmse': float(np.sqrt(mean_squared_error(y_test, pred))),
                    'mae': float(mean_absolute_error(y_test, pred))
                }
            else:
                score = accuracy_score(y_test, pred)
                metrics = {'accuracy': float(score)}
            
            results.append({'model_name': name, 'score': score, 'metrics': metrics, 'training_time': info['time']})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def _feature_importance(self, model, features):
        """Get feature importance"""
        imp_dict = {}
        
        if hasattr(model, 'feature_importances_'):
            imps = model.feature_importances_
            if imps.sum() > 0:
                imps = imps / imps.sum()
            imp_dict = {f: float(i) for f, i in zip(features, imps)}
        elif hasattr(model, 'coef_'):
            coefs = np.abs(model.coef_)
            if len(coefs.shape) > 1:
                coefs = coefs.mean(axis=0)
            if coefs.sum() > 0:
                coefs = coefs / coefs.sum()
            imp_dict = {f: float(c) for f, c in zip(features, coefs)}
        
        return dict(sorted(imp_dict.items(), key=lambda x: x[1], reverse=True))
    
    def _forecast(self, actual, predicted, domain):
        """Generate forecasting"""
        pred_mean = np.mean(predicted)
        actual_mean = np.mean(actual)
        trend = "increasing" if pred_mean > actual_mean else "decreasing"
        magnitude = abs(pred_mean - actual_mean) / actual_mean * 100
        
        return {
            'summary': f"Trend {trend} by {magnitude:.1f}%",
            'statistics': {
                'predicted_mean': float(pred_mean),
                'predicted_median': float(np.median(predicted)),
                'trend_direction': trend,
                'trend_magnitude_percent': float(magnitude)
            },
            'alerts': [{
                'level': 'warning' if magnitude > 10 else 'info',
                'message': f"Significant {trend} trend detected"
            }]
        }
    
    def _insights(self, prompt, best_model, feat_imp, forecast, domain):
        """Generate insights"""
        top_3 = list(feat_imp.items())[:3]
        
        return {
            'summary': f"Best model: {best_model['model_name']} (score: {best_model['score']:.4f})",
            'key_findings': [
                f"Top features: {', '.join([f'{f} ({v*100:.1f}%)' for f, v in top_3])}",
                f"Prediction quality: {'High' if best_model['score'] > 0.8 else 'Moderate'}",
                f"Trend: {forecast['summary']}" if forecast else "No forecast generated"
            ],
            'domain': domain,
            'user_prompt': prompt
        }

