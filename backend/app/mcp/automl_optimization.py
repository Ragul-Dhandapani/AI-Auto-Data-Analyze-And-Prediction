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
    
    # Hyperparameter search spaces for ALL 37 MODELS
    PARAM_GRIDS = {
        # REGRESSION MODELS
        
        # Linear Models
        'linear_regression': {},  # No hyperparameters to tune
        
        'ridge_regression': {
            'alpha': [0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
            'solver': ['auto', 'svd', 'cholesky', 'lsqr']
        },
        
        'lasso_regression': {
            'alpha': [0.001, 0.01, 0.1, 1.0, 10.0],
            'max_iter': [1000, 2000, 5000]
        },
        
        'elastic_net_regression': {
            'alpha': [0.001, 0.01, 0.1, 1.0],
            'l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9],
            'max_iter': [1000, 2000]
        },
        
        'sgd_regressor': {
            'loss': ['squared_error', 'huber', 'epsilon_insensitive'],
            'penalty': ['l1', 'l2', 'elasticnet'],
            'alpha': [0.0001, 0.001, 0.01],
            'learning_rate': ['constant', 'optimal', 'adaptive'],
            'eta0': [0.001, 0.01, 0.1]
        },
        
        'passive_aggressive_regressor': {
            'C': [0.1, 0.5, 1.0, 5.0],
            'max_iter': [1000, 2000],
            'loss': ['epsilon_insensitive', 'squared_epsilon_insensitive']
        },
        
        # Tree-Based Models - Regression
        'decision_tree_regression': {
            'max_depth': [3, 5, 10, 15, None],
            'min_samples_split': [2, 5, 10, 20],
            'min_samples_leaf': [1, 2, 4, 8],
            'criterion': ['squared_error', 'friedman_mse', 'absolute_error']
        },
        
        'extra_tree_regression': {
            'max_depth': [3, 5, 10, 15, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        },
        
        'random_forest_regression': {
            'n_estimators': [50, 100, 200, 300],
            'max_depth': [5, 10, 15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2', None],
            'bootstrap': [True, False]
        },
        
        'extra_trees_regression': {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 15, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2', None]
        },
        
        'gradient_boosting_regression': {
            'n_estimators': [50, 100, 200],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'subsample': [0.6, 0.8, 1.0],
            'min_samples_split': [2, 5, 10]
        },
        
        'adaboost_regression': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.5, 1.0, 2.0],
            'loss': ['linear', 'square', 'exponential']
        },
        
        # Advanced Gradient Boosting - Regression
        'xgboost_regression': {
            'n_estimators': [50, 100, 200, 300],
            'max_depth': [3, 5, 7, 9],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'subsample': [0.6, 0.8, 1.0],
            'colsample_bytree': [0.6, 0.8, 1.0],
            'gamma': [0, 0.1, 0.3],
            'min_child_weight': [1, 3, 5]
        },
        
        'lightgbm_regression': {
            'n_estimators': [50, 100, 200],
            'max_depth': [3, 5, 7, 10],
            'learning_rate': [0.01, 0.05, 0.1],
            'num_leaves': [15, 31, 63],
            'min_child_samples': [10, 20, 30],
            'subsample': [0.6, 0.8, 1.0]
        },
        
        'catboost_regression': {
            'iterations': [50, 100, 200],
            'depth': [4, 6, 8, 10],
            'learning_rate': [0.01, 0.05, 0.1],
            'l2_leaf_reg': [1, 3, 5, 7]
        },
        
        # Support Vector Machines - Regression
        'svr': {
            'C': [0.1, 1.0, 10.0, 100.0],
            'epsilon': [0.01, 0.1, 0.2],
            'kernel': ['linear', 'rbf', 'poly'],
            'gamma': ['scale', 'auto']
        },
        
        'linear_svr': {
            'C': [0.1, 1.0, 10.0],
            'epsilon': [0.0, 0.1, 0.2],
            'loss': ['epsilon_insensitive', 'squared_epsilon_insensitive'],
            'max_iter': [1000, 2000]
        },
        
        # K-Nearest Neighbors - Regression
        'knn_regression': {
            'n_neighbors': [3, 5, 7, 9, 11, 15],
            'weights': ['uniform', 'distance'],
            'algorithm': ['auto', 'ball_tree', 'kd_tree'],
            'leaf_size': [20, 30, 40],
            'p': [1, 2]
        },
        
        # Neural Networks - Regression
        'mlp_regression': {
            'hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 50)],
            'activation': ['relu', 'tanh'],
            'alpha': [0.0001, 0.001, 0.01],
            'learning_rate': ['constant', 'adaptive'],
            'max_iter': [200, 500, 1000]
        },
        
        # CLASSIFICATION MODELS
        
        # Linear Models - Classification
        'logistic_regression': {
            'C': [0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
            'penalty': ['l1', 'l2', 'elasticnet', None],
            'solver': ['lbfgs', 'liblinear', 'saga'],
            'max_iter': [100, 500, 1000]
        },
        
        'sgd_classifier': {
            'loss': ['hinge', 'log_loss', 'modified_huber'],
            'penalty': ['l1', 'l2', 'elasticnet'],
            'alpha': [0.0001, 0.001, 0.01],
            'learning_rate': ['constant', 'optimal', 'adaptive'],
            'eta0': [0.001, 0.01, 0.1]
        },
        
        'passive_aggressive_classifier': {
            'C': [0.1, 0.5, 1.0, 5.0],
            'max_iter': [1000, 2000],
            'loss': ['hinge', 'squared_hinge']
        },
        
        # Tree-Based Models - Classification
        'decision_tree_classification': {
            'max_depth': [3, 5, 10, 15, None],
            'min_samples_split': [2, 5, 10, 20],
            'min_samples_leaf': [1, 2, 4, 8],
            'criterion': ['gini', 'entropy']
        },
        
        'extra_tree_classification': {
            'max_depth': [3, 5, 10, 15, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'criterion': ['gini', 'entropy']
        },
        
        'random_forest_classification': {
            'n_estimators': [50, 100, 200, 300],
            'max_depth': [5, 10, 15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2'],
            'criterion': ['gini', 'entropy'],
            'bootstrap': [True, False]
        },
        
        'extra_trees_classification': {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 15, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2'],
            'criterion': ['gini', 'entropy']
        },
        
        'gradient_boosting_classification': {
            'n_estimators': [50, 100, 200],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'subsample': [0.6, 0.8, 1.0],
            'min_samples_split': [2, 5, 10]
        },
        
        'adaboost_classification': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.5, 1.0, 2.0],
            'algorithm': ['SAMME', 'SAMME.R']
        },
        
        # Advanced Gradient Boosting - Classification
        'xgboost_classification': {
            'n_estimators': [50, 100, 200, 300],
            'max_depth': [3, 5, 7, 9],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'subsample': [0.6, 0.8, 1.0],
            'colsample_bytree': [0.6, 0.8, 1.0],
            'gamma': [0, 0.1, 0.3],
            'min_child_weight': [1, 3, 5],
            'scale_pos_weight': [1, 2, 5]
        },
        
        'lightgbm_classification': {
            'n_estimators': [50, 100, 200],
            'max_depth': [3, 5, 7, 10],
            'learning_rate': [0.01, 0.05, 0.1],
            'num_leaves': [15, 31, 63],
            'min_child_samples': [10, 20, 30],
            'subsample': [0.6, 0.8, 1.0]
        },
        
        'catboost_classification': {
            'iterations': [50, 100, 200],
            'depth': [4, 6, 8, 10],
            'learning_rate': [0.01, 0.05, 0.1],
            'l2_leaf_reg': [1, 3, 5, 7]
        },
        
        # Support Vector Machines - Classification
        'svc': {
            'C': [0.1, 1.0, 10.0, 100.0],
            'kernel': ['linear', 'rbf', 'poly'],
            'gamma': ['scale', 'auto'],
            'class_weight': [None, 'balanced']
        },
        
        'linear_svc': {
            'C': [0.1, 1.0, 10.0],
            'penalty': ['l1', 'l2'],
            'loss': ['hinge', 'squared_hinge'],
            'max_iter': [1000, 2000],
            'class_weight': [None, 'balanced']
        },
        
        # K-Nearest Neighbors - Classification
        'knn_classification': {
            'n_neighbors': [3, 5, 7, 9, 11, 15],
            'weights': ['uniform', 'distance'],
            'algorithm': ['auto', 'ball_tree', 'kd_tree'],
            'leaf_size': [20, 30, 40],
            'p': [1, 2]
        },
        
        # Naive Bayes - Classification
        'gaussian_nb': {
            'var_smoothing': [1e-9, 1e-8, 1e-7, 1e-6]
        },
        
        'bernoulli_nb': {
            'alpha': [0.1, 0.5, 1.0, 2.0],
            'binarize': [0.0, 0.5, 1.0]
        },
        
        'multinomial_nb': {
            'alpha': [0.1, 0.5, 1.0, 2.0],
            'fit_prior': [True, False]
        },
        
        # Neural Networks - Classification
        'mlp_classification': {
            'hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 50), (100, 100)],
            'activation': ['relu', 'tanh'],
            'alpha': [0.0001, 0.001, 0.01],
            'learning_rate': ['constant', 'adaptive'],
            'max_iter': [200, 500, 1000]
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
