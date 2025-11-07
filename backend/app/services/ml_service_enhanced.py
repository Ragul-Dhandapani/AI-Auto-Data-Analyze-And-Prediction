"""
Enhanced ML Service - Enterprise Edition
Supports 30+ machine learning models across 6 categories
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    confusion_matrix, classification_report,
    silhouette_score, davies_bouldin_score, calinski_harabasz_score
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
import logging
from typing import Dict, Any, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

# ===== CLASSIFICATION MODELS =====
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier

# ===== REGRESSION MODELS =====
from sklearn.linear_model import (
    LinearRegression, Ridge, Lasso, ElasticNet,
    BayesianRidge, SGDRegressor
)
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.preprocessing import PolynomialFeatures

# ===== CLUSTERING MODELS =====
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering, SpectralClustering
from sklearn.mixture import GaussianMixture

# ===== DIMENSIONALITY REDUCTION =====
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# ===== ANOMALY DETECTION =====
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor

# Optional imports
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    logger.warning("XGBoost not available")

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False
    logger.warning("LightGBM not available")

try:
    import umap
    HAS_UMAP = True
except ImportError:
    HAS_UMAP = False
    logger.warning("UMAP not available")


# ============================================================================
# MODEL CATALOG - Enterprise Suite
# ============================================================================

CLASSIFICATION_MODELS = {
    'logistic_regression': {
        'name': 'Logistic Regression',
        'model': LogisticRegression,
        'params': {'max_iter': 1000, 'random_state': 42},
        'description': 'Linear model for binary and multiclass classification'
    },
    'decision_tree': {
        'name': 'Decision Tree',
        'model': DecisionTreeClassifier,
        'params': {'max_depth': 10, 'random_state': 42},
        'description': 'Tree-based model with interpretable rules'
    },
    'random_forest': {
        'name': 'Random Forest',
        'model': RandomForestClassifier,
        'params': {'n_estimators': 100, 'max_depth': 10, 'random_state': 42},
        'description': 'Ensemble of decision trees for robust predictions'
    },
    'svm': {
        'name': 'Support Vector Machine',
        'model': SVC,
        'params': {'kernel': 'rbf', 'probability': True, 'random_state': 42},
        'description': 'Finds optimal hyperplane for classification'
    },
    'knn': {
        'name': 'k-Nearest Neighbors',
        'model': KNeighborsClassifier,
        'params': {'n_neighbors': 5},
        'description': 'Classifies based on nearest data points'
    },
    'naive_bayes': {
        'name': 'Naive Bayes',
        'model': GaussianNB,
        'params': {},
        'description': 'Probabilistic classifier based on Bayes theorem'
    },
    'gradient_boosting': {
        'name': 'Gradient Boosting',
        'model': GradientBoostingClassifier,
        'params': {'n_estimators': 100, 'learning_rate': 0.1, 'random_state': 42},
        'description': 'Sequential ensemble method with boosting'
    },
    'qda': {
        'name': 'Quadratic Discriminant Analysis',
        'model': QuadraticDiscriminantAnalysis,
        'params': {},
        'description': 'Quadratic decision boundary classifier'
    },
    'sgd': {
        'name': 'SGD Classifier',
        'model': SGDClassifier,
        'params': {'max_iter': 1000, 'random_state': 42},
        'description': 'Stochastic gradient descent classifier'
    },
    'mlp': {
        'name': 'Neural Network (MLP)',
        'model': MLPClassifier,
        'params': {'hidden_layer_sizes': (100, 50), 'max_iter': 500, 'random_state': 42},
        'description': 'Multi-layer perceptron neural network'
    }
}

if HAS_XGBOOST:
    CLASSIFICATION_MODELS['xgboost'] = {
        'name': 'XGBoost',
        'model': xgb.XGBClassifier,
        'params': {'n_estimators': 100, 'max_depth': 5, 'random_state': 42, 'eval_metric': 'logloss'},
        'description': 'Extreme gradient boosting - high performance'
    }

if HAS_LIGHTGBM:
    CLASSIFICATION_MODELS['lightgbm'] = {
        'name': 'LightGBM',
        'model': lgb.LGBMClassifier,
        'params': {'n_estimators': 100, 'max_depth': 5, 'random_state': 42, 'verbosity': -1},
        'description': 'Light gradient boosting - fast and efficient'
    }

REGRESSION_MODELS = {
    'linear_regression': {
        'name': 'Linear Regression',
        'model': LinearRegression,
        'params': {},
        'description': 'Simple linear relationship modeling'
    },
    'ridge': {
        'name': 'Ridge Regression',
        'model': Ridge,
        'params': {'alpha': 1.0, 'random_state': 42},
        'description': 'Linear regression with L2 regularization'
    },
    'lasso': {
        'name': 'Lasso Regression',
        'model': Lasso,
        'params': {'alpha': 1.0, 'random_state': 42},
        'description': 'Linear regression with L1 regularization (feature selection)'
    },
    'elasticnet': {
        'name': 'ElasticNet',
        'model': ElasticNet,
        'params': {'alpha': 1.0, 'l1_ratio': 0.5, 'random_state': 42},
        'description': 'Combines L1 and L2 regularization'
    },
    'bayesian_ridge': {
        'name': 'Bayesian Ridge',
        'model': BayesianRidge,
        'params': {},
        'description': 'Bayesian approach to ridge regression'
    },
    'decision_tree_reg': {
        'name': 'Decision Tree Regressor',
        'model': DecisionTreeRegressor,
        'params': {'max_depth': 10, 'random_state': 42},
        'description': 'Tree-based regression model'
    },
    'random_forest_reg': {
        'name': 'Random Forest Regressor',
        'model': RandomForestRegressor,
        'params': {'n_estimators': 100, 'max_depth': 10, 'random_state': 42},
        'description': 'Ensemble of regression trees'
    },
    'svr': {
        'name': 'Support Vector Regressor',
        'model': SVR,
        'params': {'kernel': 'rbf'},
        'description': 'SVM for regression tasks'
    },
    'knn_reg': {
        'name': 'k-NN Regressor',
        'model': KNeighborsRegressor,
        'params': {'n_neighbors': 5},
        'description': 'Regression based on nearest neighbors'
    },
    'gaussian_process': {
        'name': 'Gaussian Process',
        'model': GaussianProcessRegressor,
        'params': {'random_state': 42},
        'description': 'Non-parametric probabilistic regression'
    },
    'gradient_boosting_reg': {
        'name': 'Gradient Boosting Regressor',
        'model': GradientBoostingRegressor,
        'params': {'n_estimators': 100, 'learning_rate': 0.1, 'random_state': 42},
        'description': 'Sequential boosting for regression'
    },
    'sgd_reg': {
        'name': 'SGD Regressor',
        'model': SGDRegressor,
        'params': {'max_iter': 1000, 'random_state': 42},
        'description': 'Stochastic gradient descent regressor'
    }
}

if HAS_XGBOOST:
    REGRESSION_MODELS['xgboost_reg'] = {
        'name': 'XGBoost Regressor',
        'model': xgb.XGBRegressor,
        'params': {'n_estimators': 100, 'max_depth': 5, 'random_state': 42},
        'description': 'XGBoost for regression'
    }

if HAS_LIGHTGBM:
    REGRESSION_MODELS['lightgbm_reg'] = {
        'name': 'LightGBM Regressor',
        'model': lgb.LGBMRegressor,
        'params': {'n_estimators': 100, 'max_depth': 5, 'random_state': 42, 'verbosity': -1},
        'description': 'LightGBM for regression'
    }

CLUSTERING_MODELS = {
    'kmeans': {
        'name': 'K-Means',
        'model': KMeans,
        'params': {'n_clusters': 3, 'random_state': 42},
        'description': 'Partitions data into k clusters'
    },
    'hierarchical': {
        'name': 'Hierarchical Clustering',
        'model': AgglomerativeClustering,
        'params': {'n_clusters': 3},
        'description': 'Builds hierarchy of clusters'
    },
    'dbscan': {
        'name': 'DBSCAN',
        'model': DBSCAN,
        'params': {'eps': 0.5, 'min_samples': 5},
        'description': 'Density-based clustering with noise detection'
    },
    'gmm': {
        'name': 'Gaussian Mixture',
        'model': GaussianMixture,
        'params': {'n_components': 3, 'random_state': 42},
        'description': 'Probabilistic clustering with Gaussian distributions'
    },
    'spectral': {
        'name': 'Spectral Clustering',
        'model': SpectralClustering,
        'params': {'n_clusters': 3, 'random_state': 42},
        'description': 'Graph-based clustering using eigenvalues'
    }
}

DIMENSIONALITY_MODELS = {
    'pca': {
        'name': 'PCA',
        'model': PCA,
        'params': {'n_components': 2, 'random_state': 42},
        'description': 'Linear dimensionality reduction'
    },
    'tsne': {
        'name': 't-SNE',
        'model': TSNE,
        'params': {'n_components': 2, 'random_state': 42},
        'description': 'Non-linear dimensionality reduction for visualization'
    }
}

if HAS_UMAP:
    DIMENSIONALITY_MODELS['umap'] = {
        'name': 'UMAP',
        'model': umap.UMAP,
        'params': {'n_components': 2, 'random_state': 42},
        'description': 'Uniform Manifold Approximation and Projection'
    }

ANOMALY_MODELS = {
    'isolation_forest': {
        'name': 'Isolation Forest',
        'model': IsolationForest,
        'params': {'contamination': 0.1, 'random_state': 42},
        'description': 'Isolates anomalies using random trees'
    },
    'one_class_svm': {
        'name': 'One-Class SVM',
        'model': OneClassSVM,
        'params': {'nu': 0.1},
        'description': 'Unsupervised anomaly detection with SVM'
    },
    'lof': {
        'name': 'Local Outlier Factor',
        'model': LocalOutlierFactor,
        'params': {'contamination': 0.1, 'novelty': True},
        'description': 'Detects outliers based on local density'
    }
}


# ============================================================================
# CORE TRAINING FUNCTIONS
# ============================================================================

def train_classification_models_enhanced(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    selected_models: Optional[List[str]] = None
) -> Tuple[List[Dict], Any, float]:
    """
    Train multiple classification models
    
    Args:
        X_train, y_train: Training data
        X_test, y_test: Test data
        selected_models: List of model keys to train (None = all models)
    
    Returns:
        results, best_model, best_score
    """
    results = []
    best_model = None
    best_score = -float('inf')
    
    models_to_train = CLASSIFICATION_MODELS
    if selected_models:
        models_to_train = {k: v for k, v in CLASSIFICATION_MODELS.items() if k in selected_models}
    
    for model_key, model_info in models_to_train.items():
        try:
            logger.info(f"Training {model_info['name']}...")
            
            model = model_info['model'](**model_info['params'])
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            
            result = {
                'model_key': model_key,
                'model_name': model_info['name'],
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'description': model_info['description']
            }
            
            results.append(result)
            
            if accuracy > best_score:
                best_score = accuracy
                best_model = model
                
            logger.info(f"{model_info['name']}: Accuracy={accuracy:.4f}")
            
        except Exception as e:
            logger.error(f"Failed to train {model_info['name']}: {str(e)}")
    
    return results, best_model, best_score


def train_regression_models_enhanced(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    selected_models: Optional[List[str]] = None
) -> Tuple[List[Dict], Any, float]:
    """Train multiple regression models"""
    results = []
    best_model = None
    best_score = -float('inf')
    
    models_to_train = REGRESSION_MODELS
    if selected_models:
        models_to_train = {k: v for k, v in REGRESSION_MODELS.items() if k in selected_models}
    
    for model_key, model_info in models_to_train.items():
        try:
            logger.info(f"Training {model_info['name']}...")
            
            model = model_info['model'](**model_info['params'])
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            
            r2 = r2_score(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            
            result = {
                'model_key': model_key,
                'model_name': model_info['name'],
                'r2_score': float(r2),
                'rmse': float(rmse),
                'mae': float(mae),
                'mse': float(mse),
                'description': model_info['description']
            }
            
            results.append(result)
            
            if r2 > best_score:
                best_score = r2
                best_model = model
                
            logger.info(f"{model_info['name']}: R²={r2:.4f}, RMSE={rmse:.4f}")
            
        except Exception as e:
            logger.error(f"Failed to train {model_info['name']}: {str(e)}")
    
    return results, best_model, best_score


def get_available_models(problem_type: str) -> List[Dict]:
    """Get list of available models for a problem type"""
    if problem_type == 'classification':
        return [
            {'key': k, 'name': v['name'], 'description': v['description']}
            for k, v in CLASSIFICATION_MODELS.items()
        ]
    elif problem_type == 'regression':
        return [
            {'key': k, 'name': v['name'], 'description': v['description']}
            for k, v in REGRESSION_MODELS.items()
        ]
    elif problem_type == 'clustering':
        return [
            {'key': k, 'name': v['name'], 'description': v['description']}
            for k, v in CLUSTERING_MODELS.items()
        ]
    else:
        return []


def get_model_recommendations(X: pd.DataFrame, y: pd.Series, problem_type: str) -> List[str]:
    """
    AI-powered model recommendations based on data characteristics
    
    Returns: List of recommended model keys
    """
    n_samples, n_features = X.shape
    n_unique = y.nunique()
    
    recommendations = []
    
    if problem_type == 'classification':
        # Always recommend these baseline models
        recommendations.extend(['logistic_regression', 'random_forest'])
        
        # Small dataset
        if n_samples < 1000:
            recommendations.extend(['knn', 'naive_bayes'])
        # Large dataset
        elif n_samples > 10000:
            if HAS_XGBOOST:
                recommendations.append('xgboost')
            if HAS_LIGHTGBM:
                recommendations.append('lightgbm')
            recommendations.append('sgd')
        
        # High dimensional
        if n_features > 50:
            recommendations.append('svm')
        
        # Many classes
        if n_unique > 10:
            recommendations.append('mlp')
    
    elif problem_type == 'regression':
        # Baseline
        recommendations.extend(['linear_regression', 'random_forest_reg'])
        
        # Need regularization
        if n_features > n_samples:
            recommendations.extend(['ridge', 'lasso', 'elasticnet'])
        
        # Non-linear relationships
        if n_samples < 5000:
            recommendations.extend(['svr', 'gaussian_process'])
        
        # Large dataset
        if n_samples > 10000:
            if HAS_XGBOOST:
                recommendations.append('xgboost_reg')
            recommendations.append('gradient_boosting_reg')
    
    return list(set(recommendations))  # Remove duplicates
