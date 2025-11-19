"""
AutoML Hyperparameter Optimization
Automatically find best hyperparameters for each model

This DIFFERENTIATES from Copilot:
- Copilot gives you default parameters
- PROMISE AI finds OPTIMAL parameters for YOUR data
"""

import numpy as np
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import logging

logger = logging.getLogger(__name__)


class AutoMLOptimizer:
    """
    Automatic hyperparameter optimization for ML models
    
    Finds best parameters using:
    1. Grid Search (exhaustive) - for small parameter spaces
    2. Random Search (sampling) - for large parameter spaces
    3. Bayesian Optimization (smart) - coming soon
    """
    
    # Hyperparameter search spaces
    PARAM_GRIDS = {
        'random_forest_regression': {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 15, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2', None]
        },
        'random_forest_classification': {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 15, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2']
        },
        'xgboost': {
            'n_estimators': [50, 100, 200],
            'max_depth': [3, 5, 7, 9],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'subsample': [0.6, 0.8, 1.0],
            'colsample_bytree': [0.6, 0.8, 1.0]
        },
        'gradient_boosting': {
            'n_estimators': [50, 100, 200],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.05, 0.1],
            'subsample': [0.8, 0.9, 1.0]
        }
    }
    
    def __init__(self, optimization_level='fast'):
        """
        Initialize AutoML optimizer
        
        Args:
            optimization_level: 'fast' (5 min), 'balanced' (15 min), 'thorough' (1 hour)
        """
        self.optimization_level = optimization_level
        
        # Set search iterations based on level
        if optimization_level == 'fast':
            self.n_iter = 10
            self.cv = 3
        elif optimization_level == 'balanced':
            self.n_iter = 30
            self.cv = 5
        else:  # thorough
            self.n_iter = 100
            self.cv = 10
    
    def optimize_model(
        self, 
        model_class, 
        model_name: str, 
        X_train, 
        y_train,
        problem_type: str
    ):
        """
        Find optimal hyperparameters for a model
        
        Returns:
            {
                'best_params': {...},
                'best_score': float,
                'best_model': trained model,
                'search_results': {...}
            }
        """
        
        # Get parameter grid
        param_key = f"{model_name}_{problem_type}"
        if param_key not in self.PARAM_GRIDS and model_name in self.PARAM_GRIDS:
            param_key = model_name
        
        param_grid = self.PARAM_GRIDS.get(param_key)
        
        if not param_grid:
            logger.warning(f"No parameter grid for {model_name}, using defaults")
            model = model_class()
            model.fit(X_train, y_train)
            return {
                'best_params': {},
                'best_score': None,
                'best_model': model,
                'search_results': {}
            }
        
        # Initialize base model
        base_model = model_class(random_state=42)
        
        # Choose search strategy
        if self.optimization_level == 'fast':
            # Random search (faster)
            search = RandomizedSearchCV(
                base_model,
                param_distributions=param_grid,
                n_iter=self.n_iter,
                cv=self.cv,
                scoring='r2' if problem_type == 'regression' else 'accuracy',
                n_jobs=-1,
                random_state=42,
                verbose=0
            )
        else:
            # Grid search (thorough)
            search = GridSearchCV(
                base_model,
                param_grid=param_grid,
                cv=self.cv,
                scoring='r2' if problem_type == 'regression' else 'accuracy',
                n_jobs=-1,
                verbose=0
            )
        
        logger.info(f"🔧 Optimizing {model_name} hyperparameters...")
        search.fit(X_train, y_train)
        
        logger.info(f"✅ Best score: {search.best_score_:.4f}")
        logger.info(f"✅ Best params: {search.best_params_}")
        
        return {
            'best_params': search.best_params_,
            'best_score': float(search.best_score_),
            'best_model': search.best_estimator_,
            'search_results': {
                'cv_results': {
                    'mean_test_score': search.cv_results_['mean_test_score'].tolist()[:10],  # Top 10
                    'params': [str(p) for p in search.cv_results_['params'][:10]]
                },
                'n_splits': self.cv,
                'total_fits': len(search.cv_results_['params'])
            }
        }
    
    def compare_optimized_vs_default(
        self,
        model_class,
        model_name: str,
        X_train,
        X_test,
        y_train,
        y_test,
        problem_type: str
    ):
        """
        Compare optimized model vs default parameters
        
        Shows value of AutoML optimization
        """
        from sklearn.metrics import r2_score, accuracy_score
        
        # Train with defaults
        logger.info(f"Training {model_name} with default parameters...")
        default_model = model_class(random_state=42)
        default_model.fit(X_train, y_train)
        default_pred = default_model.predict(X_test)
        
        if problem_type == 'regression':
            default_score = r2_score(y_test, default_pred)
        else:
            default_score = accuracy_score(y_test, default_pred)
        
        logger.info(f"Default score: {default_score:.4f}")
        
        # Train with optimization
        optimized = self.optimize_model(model_class, model_name, X_train, y_train, problem_type)
        optimized_pred = optimized['best_model'].predict(X_test)
        
        if problem_type == 'regression':
            optimized_score = r2_score(y_test, optimized_pred)
        else:
            optimized_score = accuracy_score(y_test, optimized_pred)
        
        improvement = ((optimized_score - default_score) / default_score) * 100
        
        return {
            'default_score': float(default_score),
            'optimized_score': float(optimized_score),
            'improvement_percent': float(improvement),
            'best_params': optimized['best_params'],
            'message': f"AutoML optimization improved performance by {improvement:.2f}%"
        }


# Example usage
if __name__ == "__main__":
    from sklearn.datasets import make_regression
    from sklearn.model_selection import train_test_split
    
    # Generate sample data
    X, y = make_regression(n_samples=1000, n_features=10, noise=0.1, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Compare default vs optimized
    optimizer = AutoMLOptimizer(optimization_level='fast')
    
    result = optimizer.compare_optimized_vs_default(
        RandomForestRegressor,
        'random_forest',
        X_train, X_test, y_train, y_test,
        'regression'
    )
    
    print(f"Default score: {result['default_score']:.4f}")
    print(f"Optimized score: {result['optimized_score']:.4f}")
    print(f"Improvement: {result['improvement_percent']:.2f}%")
    print(f"Best params: {result['best_params']}")
