"""
Intelligent Prediction MCP - Complete ML Pipeline with 35+ Models
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

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier, AdaBoostRegressor, AdaBoostClassifier, ExtraTreesRegressor, ExtraTreesClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso, ElasticNet, SGDRegressor, SGDClassifier, PassiveAggressiveRegressor, PassiveAggressiveClassifier
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier, ExtraTreeRegressor, ExtraTreeClassifier
from sklearn.svm import SVR, SVC, LinearSVR, LinearSVC
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB, BernoulliNB, MultinomialNB
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, accuracy_score

try:
    from xgboost import XGBRegressor, XGBClassifier
    XGBOOST_AVAILABLE = True
except:
    XGBOOST_AVAILABLE = False

try:
    from lightgbm import LGBMRegressor, LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except:
    LIGHTGBM_AVAILABLE = False

try:
    from catboost import CatBoostRegressor, CatBoostClassifier
    CATBOOST_AVAILABLE = True
except:
    CATBOOST_AVAILABLE = False

import cx_Oracle
import pymongo
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)

class IntelligentPredictionMCP:
    """Enhanced MCP with 35+ ML models, user prompt, forecasting & insights"""
    
    REGRESSION_MODELS = {
        # Linear Models
        'linear_regression': LinearRegression,
        'ridge': Ridge,
        'lasso': Lasso,
        'elastic_net': ElasticNet,
        'sgd_regressor': SGDRegressor,
        'passive_aggressive_regressor': PassiveAggressiveRegressor,
        
        # Tree-Based Models
        'decision_tree': DecisionTreeRegressor,
        'extra_tree': ExtraTreeRegressor,
        'random_forest': RandomForestRegressor,
        'extra_trees': ExtraTreesRegressor,
        'gradient_boosting': GradientBoostingRegressor,
        'adaboost': AdaBoostRegressor,
        
        # Advanced Gradient Boosting
        'xgboost': XGBRegressor if XGBOOST_AVAILABLE else None,
        'lightgbm': LGBMRegressor if LIGHTGBM_AVAILABLE else None,
        'catboost': CatBoostRegressor if CATBOOST_AVAILABLE else None,
        
        # Support Vector Machines
        'svr': SVR,
        'linear_svr': LinearSVR,
        
        # Neighbors
        'knn': KNeighborsRegressor,
        
        # Neural Networks
        'mlp': MLPRegressor
    }
    
    CLASSIFICATION_MODELS = {
        # Linear Models
        'logistic_regression': LogisticRegression,
        'sgd_classifier': SGDClassifier,
        'passive_aggressive_classifier': PassiveAggressiveClassifier,
        
        # Tree-Based Models
        'decision_tree': DecisionTreeClassifier,
        'extra_tree': ExtraTreeClassifier,
        'random_forest': RandomForestClassifier,
        'extra_trees': ExtraTreesClassifier,
        'gradient_boosting': GradientBoostingClassifier,
        'adaboost': AdaBoostClassifier,
        
        # Advanced Gradient Boosting
        'xgboost': XGBClassifier if XGBOOST_AVAILABLE else None,
        'lightgbm': LGBMClassifier if LIGHTGBM_AVAILABLE else None,
        'catboost': CatBoostClassifier if CATBOOST_AVAILABLE else None,
        
        # Support Vector Machines
        'svc': SVC,
        'linear_svc': LinearSVC,
        
        # Neighbors
        'knn': KNeighborsClassifier,
        
        # Naive Bayes
        'gaussian_nb': GaussianNB,
        'bernoulli_nb': BernoulliNB,
        'multinomial_nb': MultinomialNB,
        
        # Neural Networks
        'mlp': MLPClassifier
    }
    
    def __init__(self, output_dir="/app/backend/models/mcp_models"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_all_available_models(self, problem_type='regression'):
        """Get list of all available models"""
        models = self.REGRESSION_MODELS if problem_type == 'regression' else self.CLASSIFICATION_MODELS
        return [name for name, cls in models.items() if cls is not None]
    
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
        test_size: float = 0.2,
        use_automl: bool = False,
        automl_optimization_level: str = 'fast'
    ) -> Dict[str, Any]:
        """Complete ML pipeline with user control"""
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
        
        # Select models (default to fast models if not specified)
        if not models_to_train:
            models_to_train = ['random_forest', 'gradient_boosting']
            if XGBOOST_AVAILABLE:
                models_to_train.append('xgboost')
        
        # Validate models
        models_to_train = self._validate_models(models_to_train, problem_type)
        logger.info(f"🤖 Training {len(models_to_train)} models: {', '.join(models_to_train)}")
        
        # Prepare data
        X_train, X_test, y_train, y_test, scaler, le = self._prepare_data(
            df, target_column, feature_columns, test_size, problem_type
        )
        
        # Train models
        trained = self._train_models(models_to_train, X_train, y_train, problem_type, use_automl, automl_optimization_level)
        
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
        
        # Save best model
        joblib.dump(best_model, self.output_dir / f"{best['model_name']}.pkl")
        
        return {
            'training_summary': {
                'rows': len(df),
                'problem_type': problem_type,
                'domain': domain,
                'models_trained': len(trained),
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
    
    def _validate_models(self, models, prob_type):
        """Validate user-selected models"""
        available = self.REGRESSION_MODELS if prob_type == 'regression' else self.CLASSIFICATION_MODELS
        valid = [m for m in models if m in available and available[m] is not None]
        
        if not valid:
            logger.warning("No valid models, using defaults")
            valid = ['random_forest', 'gradient_boosting']
        
        return valid
    
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
    
    def _train_models(self, names, X_train, y_train, prob_type, use_automl=False, automl_level='fast'):
        """Train multiple models with optimized parameters"""
        trained = {}
        models = self.REGRESSION_MODELS if prob_type == 'regression' else self.CLASSIFICATION_MODELS
        
        # Initialize AutoML optimizer if needed
        automl_optimizer = None
        if use_automl:
            from app.mcp.automl_optimization import AutoMLOptimizer
            automl_optimizer = AutoMLOptimizer(optimization_level=automl_level)
            logger.info(f"🔧 AutoML enabled: {automl_level} optimization")
        
        for name in names:
            if models.get(name):
                logger.info(f"  Training {name}...")
                start = time.time()
                
                if use_automl and automl_optimizer:
                    # Use AutoML hyperparameter optimization
                    result = automl_optimizer.optimize_model(
                        model_class=models[name],
                        model_name=name,
                        X_train=X_train,
                        y_train=y_train,
                        problem_type=prob_type
                    )
                    model = result['best_model']
                    best_params = result['best_params']
                    automl_score = result.get('best_score')
                    
                    trained[name] = {
                        'model': model, 
                        'time': time.time() - start,
                        'automl_optimized': True,
                        'best_params': best_params,
                        'cv_score': automl_score
                    }
                    logger.info(f"  ✅ {name} optimized in {trained[name]['time']:.2f}s (CV score: {automl_score:.4f})")
                else:
                    # Use default/hardcoded parameters (fast training)
                    if name == 'random_forest':
                        model = models[name](n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
                    elif name == 'extra_trees':
                        model = models[name](n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
                    elif name == 'gradient_boosting':
                        model = models[name](n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
                    elif name == 'xgboost':
                        model = models[name](n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
                    elif name == 'lightgbm':
                        model = models[name](n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, verbose=-1)
                    elif name == 'catboost':
                        model = models[name](iterations=100, depth=6, learning_rate=0.1, random_state=42, verbose=False)
                    elif name in ['ridge', 'lasso']:
                        model = models[name](alpha=1.0)
                    elif name == 'elastic_net':
                        model = models[name](alpha=1.0, l1_ratio=0.5)
                    elif name == 'knn':
                        model = models[name](n_neighbors=5, n_jobs=-1)
                    elif name == 'mlp':
                        model = models[name](hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
                    elif name == 'adaboost':
                        model = models[name](n_estimators=50, learning_rate=1.0, random_state=42)
                    else:
                        model = models[name]()
                    
                    model.fit(X_train, y_train)
                    trained[name] = {'model': model, 'time': time.time() - start}
                    logger.info(f"  ✅ {name} trained in {trained[name]['time']:.2f}s")
        
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

