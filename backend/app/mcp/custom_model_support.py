"""
Custom Model Support - Allow users to bring their own algorithms
This is what differentiates PROMISE AI from just using Copilot!
"""

import pandas as pd
import numpy as np
from typing import Any, Dict, Callable
import importlib
import inspect
import joblib


class CustomModelRegistry:
    """
    Registry for custom user-defined models
    
    Users can:
    1. Upload their own model class
    2. Use models from any library
    3. Define custom preprocessing
    4. Implement domain-specific logic
    """
    
    def __init__(self):
        self.custom_models = {}
        self.custom_preprocessors = {}
    
    def register_model(
        self, 
        name: str, 
        model_class: Any = None,
        model_code: str = None,
        fit_params: Dict = None,
        predict_method: str = 'predict'
    ):
        """
        Register a custom model
        
        Examples:
        
        1. Register existing model class:
        registry.register_model(
            name='my_custom_rf',
            model_class=MyCustomRandomForest,
            fit_params={'n_estimators': 200}
        )
        
        2. Register from code string:
        registry.register_model(
            name='my_neural_net',
            model_code='''
class MyNeuralNet:
    def __init__(self):
        import tensorflow as tf
        self.model = tf.keras.Sequential([...])
    
    def fit(self, X, y):
        self.model.fit(X, y, epochs=50)
    
    def predict(self, X):
        return self.model.predict(X)
            '''
        )
        
        3. Register lambda model:
        registry.register_model(
            name='simple_average',
            model_code='lambda X: X.mean(axis=1)'
        )
        """
        
        if model_class:
            self.custom_models[name] = {
                'class': model_class,
                'fit_params': fit_params or {},
                'predict_method': predict_method,
                'type': 'class'
            }
        
        elif model_code:
            # Execute code in safe namespace
            namespace = {}
            exec(model_code, namespace)
            
            # Find the model class or function
            for key, value in namespace.items():
                if inspect.isclass(value) or callable(value):
                    self.custom_models[name] = {
                        'class': value,
                        'fit_params': fit_params or {},
                        'predict_method': predict_method,
                        'type': 'code',
                        'source': model_code
                    }
                    break
    
    def register_preprocessor(self, name: str, preprocessor: Callable):
        """
        Register custom preprocessing function
        
        Example:
        def my_preprocessing(df):
            # Domain-specific logic
            df['log_revenue'] = np.log1p(df['revenue'])
            df['is_weekend'] = df['date'].dt.dayofweek >= 5
            return df
        
        registry.register_preprocessor('ecommerce_prep', my_preprocessing)
        """
        self.custom_preprocessors[name] = preprocessor
    
    def get_model(self, name: str):
        """Get registered custom model"""
        return self.custom_models.get(name)
    
    def get_preprocessor(self, name: str):
        """Get registered preprocessor"""
        return self.custom_preprocessors.get(name)
    
    def list_custom_models(self):
        """List all registered custom models"""
        return list(self.custom_models.keys())


class CustomModelWrapper:
    """
    Wrapper for custom models to ensure compatibility with PROMISE AI pipeline
    """
    
    def __init__(self, model_info: Dict):
        self.model_info = model_info
        self.model_class = model_info['class']
        self.fit_params = model_info['fit_params']
        self.predict_method = model_info['predict_method']
        self.model_instance = None
    
    def fit(self, X, y):
        """Fit the custom model"""
        # Initialize model
        self.model_instance = self.model_class(**self.fit_params)
        
        # Fit
        if hasattr(self.model_instance, 'fit'):
            self.model_instance.fit(X, y)
        else:
            raise ValueError(f"Model {self.model_class} must have a 'fit' method")
        
        return self
    
    def predict(self, X):
        """Make predictions"""
        if not self.model_instance:
            raise ValueError("Model not fitted yet")
        
        predict_fn = getattr(self.model_instance, self.predict_method)
        return predict_fn(X)
    
    def get_feature_importance(self, feature_names):
        """Extract feature importance if available"""
        if hasattr(self.model_instance, 'feature_importances_'):
            return dict(zip(feature_names, self.model_instance.feature_importances_))
        elif hasattr(self.model_instance, 'coef_'):
            return dict(zip(feature_names, np.abs(self.model_instance.coef_)))
        else:
            return None


# Global registry
custom_registry = CustomModelRegistry()


# Example: Pre-register some advanced models
def register_advanced_models():
    """Register additional advanced models not in base sklearn"""
    
    # 1. Prophet for time series
    try:
        from prophet import Prophet
        
        class ProphetWrapper:
            def __init__(self):
                self.model = Prophet()
            
            def fit(self, X, y):
                # Prophet expects DataFrame with 'ds' and 'y' columns
                df = pd.DataFrame({'ds': X[:, 0], 'y': y})
                self.model.fit(df)
            
            def predict(self, X):
                df = pd.DataFrame({'ds': X[:, 0]})
                forecast = self.model.predict(df)
                return forecast['yhat'].values
        
        custom_registry.register_model('prophet', ProphetWrapper)
    except:
        pass
    
    # 2. ARIMA for time series
    try:
        from statsmodels.tsa.arima.model import ARIMA
        
        class ARIMAWrapper:
            def __init__(self, order=(1,1,1)):
                self.order = order
                self.model = None
            
            def fit(self, X, y):
                self.model = ARIMA(y, order=self.order)
                self.fitted_model = self.model.fit()
            
            def predict(self, X):
                return self.fitted_model.forecast(steps=len(X))
        
        custom_registry.register_model('arima', ARIMAWrapper)
    except:
        pass
    
    # 3. Gaussian Process
    try:
        from sklearn.gaussian_process import GaussianProcessRegressor
        custom_registry.register_model('gaussian_process', GaussianProcessRegressor)
    except:
        pass
    
    # 4. Isolation Forest for anomaly detection
    try:
        from sklearn.ensemble import IsolationForest
        custom_registry.register_model('isolation_forest', IsolationForest)
    except:
        pass


# Register on module import
register_advanced_models()


# Example usage functions
def example_custom_model():
    """Example: User-defined custom model"""
    
    # Define custom model
    custom_code = '''
class MyEnsembleModel:
    """Custom ensemble of multiple models"""
    
    def __init__(self):
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        from sklearn.linear_model import Ridge
        
        self.models = [
            RandomForestRegressor(n_estimators=100),
            GradientBoostingRegressor(n_estimators=100),
            Ridge()
        ]
        self.weights = [0.5, 0.3, 0.2]
    
    def fit(self, X, y):
        for model in self.models:
            model.fit(X, y)
        return self
    
    def predict(self, X):
        predictions = np.array([model.predict(X) for model in self.models])
        weighted_pred = np.average(predictions, axis=0, weights=self.weights)
        return weighted_pred
    '''
    
    # Register
    custom_registry.register_model('my_ensemble', model_code=custom_code)
    
    # Use in training
    from app.mcp.intelligent_prediction_mcp import IntelligentPredictionMCP
    mcp = IntelligentPredictionMCP()
    
    result = mcp.train_and_predict(
        data_source={'type': 'file', 'path': '/data/sales.csv'},
        user_prompt="Predict sales with my custom ensemble model",
        target_column='sales',
        feature_columns=['price', 'marketing_spend'],
        models_to_train=['my_ensemble', 'random_forest', 'xgboost'],  # Mix custom + built-in
        include_forecasting=True,
        include_insights=True
    )
    
    return result


def example_custom_preprocessing():
    """Example: Domain-specific preprocessing"""
    
    def ecommerce_preprocessing(df):
        """Custom preprocessing for ecommerce data"""
        # Feature engineering
        df['days_since_purchase'] = (pd.Timestamp.now() - df['last_purchase_date']).dt.days
        df['is_weekend'] = df['date'].dt.dayofweek >= 5
        df['purchase_velocity'] = df['total_purchases'] / df['account_age_days']
        
        # Handle domain-specific outliers
        df = df[df['purchase_amount'] < df['purchase_amount'].quantile(0.99)]
        
        # Domain-specific encoding
        df['customer_tier'] = pd.cut(df['lifetime_value'], 
                                      bins=[0, 100, 500, 1000, np.inf],
                                      labels=['bronze', 'silver', 'gold', 'platinum'])
        
        return df
    
    # Register
    custom_registry.register_preprocessor('ecommerce', ecommerce_preprocessing)
    
    # Use in pipeline
    # (Would need to modify IntelligentPredictionMCP to support custom preprocessors)


if __name__ == "__main__":
    print(f"✅ Custom model support initialized")
    print(f"📋 Available custom models: {custom_registry.list_custom_models()}")
