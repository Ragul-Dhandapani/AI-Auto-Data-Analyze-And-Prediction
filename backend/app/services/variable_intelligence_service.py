"""
Variable Intelligence Service
Validates variable selection and suggests better alternatives
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class VariableIntelligenceService:
    """AI-powered variable selection validation and override service"""
    
    @staticmethod
    def validate_variable_selection(
        df: pd.DataFrame,
        target_variables: List[str],
        features: List[str]
    ) -> Dict:
        """
        Validate user's variable selection and suggest overrides if needed
        
        Args:
            df: DataFrame with data
            target_variables: List of target variable names
            features: List of feature variable names
            
        Returns:
            {
                "valid": bool,
                "override_needed": bool,
                "issues": List[Dict],
                "suggested_target": str,
                "suggested_features": List[str],
                "explanation": str,
                "confidence": float
            }
        """
        try:
            issues = []
            override_needed = False
            
            # Validate target variables
            target_issues = []
            valid_targets = []
            
            for target in target_variables:
                if target not in df.columns:
                    target_issues.append({
                        "variable": target,
                        "issue": "not_found",
                        "message": f"Column '{target}' not found in dataset"
                    })
                    continue
                
                # Check if numeric
                if not pd.api.types.is_numeric_dtype(df[target]):
                    target_issues.append({
                        "variable": target,
                        "issue": "not_numeric",
                        "message": f"'{target}' is not numeric (type: {df[target].dtype}). Prediction targets must be numeric."
                    })
                    override_needed = True
                    continue
                
                # Check variance
                if df[target].std() == 0:
                    target_issues.append({
                        "variable": target,
                        "issue": "no_variance",
                        "message": f"'{target}' has no variance (all values are {df[target].iloc[0]}). Cannot predict constant values."
                    })
                    override_needed = True
                    continue
                
                # Check missing values
                null_pct = (df[target].isnull().sum() / len(df)) * 100
                if null_pct > 50:
                    target_issues.append({
                        "variable": target,
                        "issue": "too_many_nulls",
                        "message": f"'{target}' has {null_pct:.1f}% missing values. Too sparse for reliable predictions."
                    })
                    override_needed = True
                    continue
                
                valid_targets.append(target)
            
            issues.extend(target_issues)
            
            # Validate features
            feature_issues = []
            valid_features = []
            
            for feature in features:
                if feature not in df.columns:
                    feature_issues.append({
                        "variable": feature,
                        "issue": "not_found",
                        "message": f"Column '{feature}' not found in dataset"
                    })
                    continue
                
                # Check if it's an ID column
                if VariableIntelligenceService._is_id_column(df, feature):
                    feature_issues.append({
                        "variable": feature,
                        "issue": "id_column",
                        "message": f"'{feature}' appears to be an ID column (all unique values). ID columns have no predictive power."
                    })
                    override_needed = True
                    continue
                
                # Check if constant
                if df[feature].nunique() == 1:
                    feature_issues.append({
                        "variable": feature,
                        "issue": "constant",
                        "message": f"'{feature}' has only 1 unique value. Provides no information."
                    })
                    override_needed = True
                    continue
                
                # Check if mostly null
                null_pct = (df[feature].isnull().sum() / len(df)) * 100
                if null_pct > 80:
                    feature_issues.append({
                        "variable": feature,
                        "issue": "too_many_nulls",
                        "message": f"'{feature}' has {null_pct:.1f}% missing values. Too sparse."
                    })
                    override_needed = True
                    continue
                
                valid_features.append(feature)
            
            issues.extend(feature_issues)
            
            # Suggest better variables if override needed
            suggested_target = None
            suggested_features = []
            confidence = 0.0
            
            if override_needed or not valid_targets:
                # Find best target variable
                suggested_target = VariableIntelligenceService._suggest_best_target(df)
                
                # Find best features
                if suggested_target:
                    suggested_features = VariableIntelligenceService._suggest_best_features(
                        df, suggested_target, top_n=min(10, len(df.columns) - 1)
                    )
                    confidence = 0.85  # Base confidence
                else:
                    confidence = 0.0
            else:
                suggested_target = valid_targets[0] if valid_targets else None
                suggested_features = valid_features
                confidence = 0.95
            
            # Generate explanation
            explanation = VariableIntelligenceService._generate_explanation(
                issues, suggested_target, suggested_features, confidence
            )
            
            return {
                "valid": not override_needed and len(valid_targets) > 0 and len(valid_features) > 0,
                "override_needed": override_needed,
                "issues": issues,
                "suggested_target": suggested_target,
                "suggested_features": suggested_features,
                "explanation": explanation,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Error validating variables: {str(e)}")
            return {
                "valid": False,
                "override_needed": True,
                "issues": [{"message": f"Error analyzing variables: {str(e)}"}],
                "suggested_target": None,
                "suggested_features": [],
                "explanation": "Unable to validate variable selection due to error.",
                "confidence": 0.0
            }
    
    @staticmethod
    def _is_id_column(df: pd.DataFrame, column: str) -> bool:
        """Check if column is likely an ID column"""
        col_data = df[column]
        
        # Check if all values are unique
        if col_data.nunique() == len(df):
            return True
        
        # Check column name patterns
        id_patterns = ['id', 'key', 'code', 'number', 'index', '_id', 'uuid', 'guid']
        column_lower = column.lower()
        if any(pattern in column_lower for pattern in id_patterns):
            # If more than 90% unique, likely an ID
            if col_data.nunique() / len(df) > 0.9:
                return True
        
        return False
    
    @staticmethod
    def _suggest_best_target(df: pd.DataFrame) -> Optional[str]:
        """Suggest best target variable based on data characteristics"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            return None
        
        best_target = None
        best_score = -1
        
        for col in numeric_cols:
            # Skip if ID column
            if VariableIntelligenceService._is_id_column(df, col):
                continue
            
            # Skip if no variance
            if df[col].std() == 0:
                continue
            
            # Calculate score based on:
            # 1. Variance (higher is better)
            # 2. Non-null percentage (higher is better)
            # 3. Not being constant
            
            null_pct = df[col].isnull().sum() / len(df)
            variance_normalized = min(df[col].std() / (df[col].mean() + 1e-10), 10) / 10  # Coefficient of variation, capped
            
            score = (1 - null_pct) * 0.4 + variance_normalized * 0.6
            
            if score > best_score:
                best_score = score
                best_target = col
        
        return best_target
    
    @staticmethod
    def _suggest_best_features(df: pd.DataFrame, target: str, top_n: int = 10) -> List[str]:
        """Suggest best features based on correlation and data quality"""
        if target not in df.columns:
            return []
        
        # Get all columns except target
        candidate_cols = [col for col in df.columns if col != target]
        
        feature_scores = []
        
        for col in candidate_cols:
            # Skip ID columns
            if VariableIntelligenceService._is_id_column(df, col):
                continue
            
            # Skip constants
            if df[col].nunique() <= 1:
                continue
            
            # Calculate feature score
            score = 0.0
            
            # Data quality score (40%)
            null_pct = df[col].isnull().sum() / len(df)
            quality_score = (1 - null_pct) * 0.4
            
            # Variance score (30%)
            if pd.api.types.is_numeric_dtype(df[col]):
                if df[col].std() > 0:
                    variance_score = 0.3
                else:
                    variance_score = 0.0
            else:
                variance_score = 0.15  # Categorical gets partial credit
            
            # Correlation score (30%) - only for numeric columns
            correlation_score = 0.0
            if pd.api.types.is_numeric_dtype(df[col]) and pd.api.types.is_numeric_dtype(df[target]):
                try:
                    corr = abs(df[col].corr(df[target]))
                    if not np.isnan(corr):
                        correlation_score = corr * 0.3
                except:
                    pass
            
            score = quality_score + variance_score + correlation_score
            
            feature_scores.append({
                "feature": col,
                "score": score
            })
        
        # Sort by score and return top N
        feature_scores.sort(key=lambda x: x["score"], reverse=True)
        return [f["feature"] for f in feature_scores[:top_n]]
    
    @staticmethod
    def _generate_explanation(
        issues: List[Dict],
        suggested_target: Optional[str],
        suggested_features: List[str],
        confidence: float
    ) -> str:
        """Generate human-readable explanation"""
        if not issues:
            return f"✅ Your variable selection looks good! (Confidence: {confidence*100:.0f}%)"
        
        explanation_parts = []
        
        # Group issues by type
        target_issues = [i for i in issues if i.get("issue") in ["not_numeric", "no_variance", "too_many_nulls"]]
        feature_issues = [i for i in issues if i.get("issue") in ["id_column", "constant", "too_many_nulls"]]
        
        if target_issues:
            explanation_parts.append("**Target Variable Issues:**")
            for issue in target_issues[:3]:  # Limit to top 3
                explanation_parts.append(f"❌ {issue['message']}")
        
        if feature_issues:
            explanation_parts.append("\n**Feature Issues:**")
            for issue in feature_issues[:5]:  # Limit to top 5
                explanation_parts.append(f"❌ {issue['message']}")
        
        if suggested_target:
            explanation_parts.append(f"\n**✅ AI Recommended Selection:**")
            explanation_parts.append(f"**Target:** {suggested_target}")
            if suggested_features:
                explanation_parts.append(f"**Features:** {', '.join(suggested_features[:5])}{' and more...' if len(suggested_features) > 5 else ''}")
            explanation_parts.append(f"\n**Confidence:** {confidence*100:.0f}% - This selection will produce meaningful predictions.")
        
        return "\n".join(explanation_parts)


# Singleton instance
variable_intelligence = VariableIntelligenceService()



async def get_ai_variable_recommendations(
    df: pd.DataFrame,
    problem_type: str = "auto"
) -> Dict:
    """
    Get AI-powered variable selection recommendations using Azure OpenAI
    
    Args:
        df: DataFrame with data
        problem_type: "regression", "classification", or "auto"
    
    Returns:
        {
            "recommended_target": str,
            "recommended_features": List[str],
            "reasoning": str,
            "confidence": float,
            "problem_type_suggestion": str
        }
    """
    try:
        from app.services.azure_openai_service import get_azure_openai_service
        
        azure_service = get_azure_openai_service()
        
        # Analyze dataset characteristics
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Get basic stats
        stats_summary = {
            "total_columns": len(df.columns),
            "numeric_columns": len(numeric_cols),
            "categorical_columns": len(categorical_cols),
            "row_count": len(df),
            "numeric_cols": numeric_cols[:10],  # First 10
            "categorical_cols": categorical_cols[:5]  # First 5
        }
        
        if not azure_service.is_available():
            # Fallback to rule-based
            logger.warning("Azure OpenAI not available, using rule-based recommendations")
            
            # Simple rule: last numeric column as target
            if numeric_cols:
                recommended_target = numeric_cols[-1]
                recommended_features = [c for c in numeric_cols if c != recommended_target][:10]
            else:
                recommended_target = df.columns[-1]
                recommended_features = df.columns[:-1].tolist()[:10]
            
            return {
                "recommended_target": recommended_target,
                "recommended_features": recommended_features,
                "reasoning": "Rule-based recommendation (Azure OpenAI unavailable)",
                "confidence": 0.6,
                "problem_type_suggestion": "auto"
            }
        
        # Prepare context for AI
        context = f"""
Dataset Analysis:
- Total Columns: {stats_summary['total_columns']}
- Numeric Columns ({len(numeric_cols)}): {', '.join(numeric_cols[:10])}
- Categorical Columns ({len(categorical_cols)}): {', '.join(categorical_cols[:5])}
- Rows: {stats_summary['row_count']}
- Requested Problem Type: {problem_type}

Task: Analyze column names and recommend:
1. Best target variable for prediction
2. Top 10 features (independent variables)
3. Problem type (regression or classification)
4. Brief reasoning (2-3 sentences)

Respond in JSON format:
{{
  "target": "column_name",
  "features": ["feature1", "feature2", ...],
  "problem_type": "regression or classification",
  "reasoning": "explanation"
}}
"""
        
        response = await azure_service.generate_completion(
            prompt=context,
            max_tokens=600,
            temperature=0.3
        )
        
        # Try to parse JSON response
        import json
        try:
            parsed = json.loads(response.strip())
            return {
                "recommended_target": parsed.get("target", numeric_cols[-1] if numeric_cols else df.columns[-1]),
                "recommended_features": parsed.get("features", numeric_cols[:-1])[:10],
                "reasoning": parsed.get("reasoning", response),
                "confidence": 0.85,
                "problem_type_suggestion": parsed.get("problem_type", "auto")
            }
        except:
            # If JSON parsing fails, use fallback
            return {
                "recommended_target": numeric_cols[-1] if numeric_cols else df.columns[-1],
                "recommended_features": numeric_cols[:-1][:10] if numeric_cols else df.columns[:-1].tolist()[:10],
                "reasoning": response,
                "confidence": 0.75,
                "problem_type_suggestion": problem_type
            }
    
    except Exception as e:
        logger.error(f"AI variable recommendations failed: {str(e)}")
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        return {
            "recommended_target": numeric_cols[-1] if numeric_cols else df.columns[-1],
            "recommended_features": numeric_cols[:-1][:10] if numeric_cols else df.columns[:-1].tolist()[:10],
            "reasoning": f"Error occurred: {str(e)}. Using fallback recommendations.",
            "confidence": 0.5,
            "problem_type_suggestion": "auto"
        }

