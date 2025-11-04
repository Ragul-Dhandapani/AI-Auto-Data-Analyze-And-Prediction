"""
Add this to analysis.py after the other endpoints
"""

HYPERPARAMETER_ENDPOINT = '''
@router.post("/hyperparameter-tuning")
async def hyperparameter_tuning_endpoint(request: Dict[str, Any]):
    """
    Perform hyperparameter tuning for a specific model
    """
    try:
        from app.services import hyperparameter_service
        from sklearn.model_selection import train_test_split
        
        dataset_id = request.get("dataset_id")
        target_column = request.get("target_column")
        model_type = request.get("model_type", "random_forest")
        problem_type = request.get("problem_type", "regression")
        search_type = request.get("search_type", "grid")
        param_grid = request.get("param_grid")
        n_iter = request.get("n_iter", 20)
        
        if not all([dataset_id, target_column]):
            raise HTTPException(400, "Missing required parameters: dataset_id and target_column")
        
        # Load data
        df = await load_dataframe(dataset_id)
        
        # Validate target column
        if target_column not in df.columns:
            raise HTTPException(400, f"Target column '{target_column}' not found in dataset")
        
        # Prepare features and target
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        feature_cols = [col for col in numeric_cols if col != target_column]
        
        if len(feature_cols) == 0:
            raise HTTPException(400, "No numeric feature columns found for training")
        
        X = df[feature_cols].fillna(df[feature_cols].mean())
        y = df[target_column]
        
        # Check if target is suitable for problem type
        unique_values = y.nunique()
        
        if problem_type == "classification":
            if unique_values > 50:
                raise HTTPException(
                    400, 
                    f"❌ Too many unique values for classification: {unique_values}\\n\\n"
                    f"💡 Suggestion: Classification works best with categorical targets (2-50 unique classes).\\n"
                    f"Your column '{target_column}' has {unique_values} unique values, which suggests it might be better suited for regression.\\n\\n"
                    f"✅ Try one of these:\\n"
                    f"1. Switch to 'Regression' mode\\n"
                    f"2. Select a different target column with fewer unique values\\n"
                    f"3. Group your target into categories (e.g., 'Low', 'Medium', 'High')"
                )
            
            # Fill missing values for classification
            y = y.fillna(y.mode()[0] if len(y.mode()) > 0 else y.iloc[0])
        else:
            # Fill missing values for regression
            y = y.fillna(y.mean())
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Perform tuning with error handling
        try:
            if search_type == "grid":
                results = hyperparameter_service.tune_hyperparameters_grid(
                    X_train, y_train, model_type, problem_type, param_grid
                )
            else:
                results = hyperparameter_service.tune_hyperparameters_random(
                    X_train, y_train, model_type, problem_type, n_iter, param_grid
                )
            
            return results
            
        except ValueError as ve:
            error_msg = str(ve)
            
            # Translate common sklearn errors to user-friendly messages
            if "Invalid classes inferred" in error_msg or "Expected:" in error_msg:
                raise HTTPException(
                    400,
                    f"❌ Classification Configuration Error\\n\\n"
                    f"The model expected categorical classes (like: Red, Blue, Green) but received continuous numeric values.\\n\\n"
                    f"💡 Quick Fix:\\n"
                    f"1. Switch to 'Regression' problem type (your data is continuous, not categorical)\\n"
                    f"2. Or convert your target column to categories first\\n\\n"
                    f"📊 Your target '{target_column}' has {unique_values} unique values - this is too many for classification."
                )
            elif "could not convert string to float" in error_msg:
                raise HTTPException(
                    400,
                    f"❌ Data Type Error\\n\\n"
                    f"Some features contain text values that cannot be used for numeric prediction.\\n\\n"
                    f"💡 Solution: Remove non-numeric columns or convert them to numbers first."
                )
            else:
                raise HTTPException(500, f"Model training error: {error_msg}")
        
        except Exception as e:
            logger.error(f"Hyperparameter tuning failed: {str(e)}")
            raise HTTPException(500, f"Tuning failed: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hyperparameter tuning error: {str(e)}", exc_info=True)
        raise HTTPException(500, f"An unexpected error occurred: {str(e)}")
'''

print(HYPERPARAMETER_ENDPOINT)
