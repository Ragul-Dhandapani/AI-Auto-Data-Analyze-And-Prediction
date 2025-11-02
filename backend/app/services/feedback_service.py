"""
Feedback Loop Service for Active Learning
Tracks predictions, user feedback, and enables model retraining
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timezone
import logging
import uuid


class FeedbackTracker:
    """
    Tracks model predictions and user feedback for active learning
    """
    
    def __init__(self, db):
        self.db = db
        self.collection = db.prediction_feedback
    
    async def store_prediction(
        self,
        dataset_id: str,
        model_name: str,
        input_features: Dict[str, Any],
        prediction: Any,
        confidence: float = None,
        user_id: str = None
    ) -> str:
        """
        Store a model prediction for tracking
        
        Returns:
            prediction_id for future feedback
        """
        prediction_id = str(uuid.uuid4())
        
        prediction_doc = {
            "prediction_id": prediction_id,
            "dataset_id": dataset_id,
            "model_name": model_name,
            "input_features": input_features,
            "prediction": prediction,
            "confidence": confidence,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "feedback": None,
            "actual_outcome": None,
            "is_correct": None
        }
        
        await self.collection.insert_one(prediction_doc)
        
        logging.info(f"Stored prediction {prediction_id} for model {model_name}")
        
        return prediction_id
    
    async def submit_feedback(
        self,
        prediction_id: str,
        is_correct: bool,
        actual_outcome: Any = None,
        user_comment: str = None
    ) -> bool:
        """
        Submit user feedback for a prediction
        
        Args:
            prediction_id: ID of the prediction
            is_correct: Whether prediction was correct
            actual_outcome: Actual observed value (optional)
            user_comment: User's comment about the prediction
        
        Returns:
            Success boolean
        """
        try:
            update_doc = {
                "$set": {
                    "feedback": {
                        "is_correct": is_correct,
                        "actual_outcome": actual_outcome,
                        "user_comment": user_comment,
                        "feedback_timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    "is_correct": is_correct,
                    "actual_outcome": actual_outcome
                }
            }
            
            result = await self.collection.update_one(
                {"prediction_id": prediction_id},
                update_doc
            )
            
            if result.modified_count > 0:
                logging.info(f"Feedback submitted for prediction {prediction_id}")
                return True
            else:
                logging.warning(f"No prediction found with ID {prediction_id}")
                return False
        
        except Exception as e:
            logging.error(f"Failed to submit feedback: {str(e)}")
            return False
    
    async def get_feedback_data(
        self,
        dataset_id: str = None,
        model_name: str = None,
        with_feedback_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve prediction feedback data
        
        Args:
            dataset_id: Filter by dataset
            model_name: Filter by model
            with_feedback_only: Only return predictions with feedback
        
        Returns:
            List of prediction documents with feedback
        """
        query = {}
        
        if dataset_id:
            query["dataset_id"] = dataset_id
        
        if model_name:
            query["model_name"] = model_name
        
        if with_feedback_only:
            query["feedback"] = {"$ne": None}
        
        cursor = self.collection.find(query)
        feedback_data = await cursor.to_list(length=None)
        
        return feedback_data
    
    async def get_model_performance_stats(
        self,
        dataset_id: str,
        model_name: str
    ) -> Dict[str, Any]:
        """
        Calculate performance statistics based on user feedback
        
        Returns:
            Statistics including accuracy, feedback count, etc.
        """
        feedback_data = await self.get_feedback_data(
            dataset_id=dataset_id,
            model_name=model_name,
            with_feedback_only=True
        )
        
        if not feedback_data:
            return {
                "feedback_count": 0,
                "accuracy": None,
                "correct_predictions": 0,
                "incorrect_predictions": 0
            }
        
        correct_count = sum(1 for item in feedback_data if item.get("is_correct"))
        total_count = len(feedback_data)
        
        return {
            "feedback_count": total_count,
            "accuracy": correct_count / total_count if total_count > 0 else 0,
            "correct_predictions": correct_count,
            "incorrect_predictions": total_count - correct_count,
            "feedback_data": feedback_data
        }
    
    async def prepare_retraining_data(
        self,
        dataset_id: str,
        model_name: str = None
    ) -> pd.DataFrame:
        """
        Prepare data for model retraining based on feedback
        
        Returns:
            DataFrame with input features and actual outcomes
        """
        feedback_data = await self.get_feedback_data(
            dataset_id=dataset_id,
            model_name=model_name,
            with_feedback_only=True
        )
        
        if not feedback_data:
            return pd.DataFrame()
        
        # Extract features and actuals
        rows = []
        for item in feedback_data:
            if item.get("actual_outcome") is not None:
                row = item["input_features"].copy()
                row["actual_outcome"] = item["actual_outcome"]
                rows.append(row)
        
        if not rows:
            return pd.DataFrame()
        
        df = pd.DataFrame(rows)
        
        logging.info(f"Prepared {len(df)} samples for retraining")
        
        return df
    
    async def get_uncertain_predictions(
        self,
        dataset_id: str,
        model_name: str,
        confidence_threshold: float = 0.6,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get predictions with low confidence for active learning
        
        Args:
            dataset_id: Dataset ID
            model_name: Model name
            confidence_threshold: Return predictions below this confidence
            limit: Maximum number of predictions to return
        
        Returns:
            List of uncertain predictions
        """
        query = {
            "dataset_id": dataset_id,
            "model_name": model_name,
            "confidence": {"$lt": confidence_threshold},
            "feedback": None  # Not yet reviewed
        }
        
        cursor = self.collection.find(query).limit(limit)
        uncertain_predictions = await cursor.to_list(length=limit)
        
        return uncertain_predictions


async def create_feedback_tracker(db):
    """Factory function to create FeedbackTracker instance"""
    return FeedbackTracker(db)
