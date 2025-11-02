"""
Analytics Tracking Service
Tracks user interactions for self-learning visualization system
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional
import logging
from app.database.mongodb import db

logger = logging.getLogger(__name__)


async def track_chart_view(
    user_id: str,
    dataset_id: str,
    chart_type: str,
    chart_config: Dict,
    duration_seconds: float = 0
):
    """
    Track when a user views a chart
    
    Args:
        user_id: User identifier
        dataset_id: Dataset being analyzed
        chart_type: Type of chart (scatter, bar, heatmap, etc.)
        chart_config: Configuration of the chart
        duration_seconds: How long user viewed the chart
    """
    try:
        tracking_data = {
            "event_type": "chart_view",
            "user_id": user_id,
            "dataset_id": dataset_id,
            "chart_type": chart_type,
            "chart_config": chart_config,
            "duration_seconds": duration_seconds,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await db.analytics_tracking.insert_one(tracking_data)
        logger.info(f"Tracked chart view: {chart_type} for dataset {dataset_id}")
    except Exception as e:
        logger.error(f"Error tracking chart view: {str(e)}")


async def track_chart_export(
    user_id: str,
    dataset_id: str,
    chart_type: str,
    export_format: str
):
    """Track when a user exports a chart"""
    try:
        tracking_data = {
            "event_type": "chart_export",
            "user_id": user_id,
            "dataset_id": dataset_id,
            "chart_type": chart_type,
            "export_format": export_format,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await db.analytics_tracking.insert_one(tracking_data)
        logger.info(f"Tracked chart export: {chart_type} as {export_format}")
    except Exception as e:
        logger.error(f"Error tracking chart export: {str(e)}")


async def track_insight_interaction(
    user_id: str,
    dataset_id: str,
    insight_type: str,
    insight_text: str,
    rating: Optional[int] = None
):
    """Track user interaction with AI-generated insights"""
    try:
        tracking_data = {
            "event_type": "insight_interaction",
            "user_id": user_id,
            "dataset_id": dataset_id,
            "insight_type": insight_type,
            "insight_text": insight_text,
            "rating": rating,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await db.analytics_tracking.insert_one(tracking_data)
        logger.info(f"Tracked insight interaction for dataset {dataset_id}")
    except Exception as e:
        logger.error(f"Error tracking insight interaction: {str(e)}")


async def get_popular_charts_for_dataset_type(
    column_count: int,
    row_count: int,
    has_time_column: bool = False,
    limit: int = 5
) -> List[Dict]:
    """
    Get most popular chart types for similar datasets
    Uses self-learning to recommend charts based on historical usage
    
    Args:
        column_count: Number of columns in dataset
        row_count: Number of rows in dataset
        has_time_column: Whether dataset has temporal data
        limit: Number of recommendations to return
    
    Returns:
        List of recommended chart types with usage statistics
    """
    try:
        # Define similarity criteria
        col_range = (column_count * 0.7, column_count * 1.3)
        row_range = (row_count * 0.5, row_count * 2.0)
        
        # Aggregate chart views for similar datasets
        pipeline = [
            {
                "$match": {
                    "event_type": "chart_view"
                }
            },
            {
                "$lookup": {
                    "from": "datasets",
                    "localField": "dataset_id",
                    "foreignField": "id",
                    "as": "dataset"
                }
            },
            {
                "$unwind": "$dataset"
            },
            {
                "$match": {
                    "dataset.column_count": {"$gte": col_range[0], "$lte": col_range[1]},
                    "dataset.row_count": {"$gte": row_range[0], "$lte": row_range[1]}
                }
            },
            {
                "$group": {
                    "_id": "$chart_type",
                    "view_count": {"$sum": 1},
                    "avg_duration": {"$avg": "$duration_seconds"},
                    "export_count": {"$sum": {"$cond": [{"$eq": ["$event_type", "chart_export"]}, 1, 0]}}
                }
            },
            {
                "$sort": {"view_count": -1}
            },
            {
                "$limit": limit
            }
        ]
        
        cursor = db.analytics_tracking.aggregate(pipeline)
        recommendations = await cursor.to_list(length=limit)
        
        return [
            {
                "chart_type": rec["_id"],
                "popularity_score": rec["view_count"],
                "avg_view_duration": rec.get("avg_duration", 0),
                "export_frequency": rec.get("export_count", 0)
            }
            for rec in recommendations
        ]
    
    except Exception as e:
        logger.error(f"Error getting chart recommendations: {str(e)}")
        return []


async def get_dataset_analytics_summary(dataset_id: str) -> Dict:
    """Get analytics summary for a specific dataset"""
    try:
        pipeline = [
            {"$match": {"dataset_id": dataset_id}},
            {
                "$group": {
                    "_id": "$event_type",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        cursor = db.analytics_tracking.aggregate(pipeline)
        results = await cursor.to_list(length=100)
        
        summary = {
            "total_views": 0,
            "total_exports": 0,
            "total_insights_viewed": 0
        }
        
        for result in results:
            if result["_id"] == "chart_view":
                summary["total_views"] = result["count"]
            elif result["_id"] == "chart_export":
                summary["total_exports"] = result["count"]
            elif result["_id"] == "insight_interaction":
                summary["total_insights_viewed"] = result["count"]
        
        return summary
    
    except Exception as e:
        logger.error(f"Error getting dataset analytics: {str(e)}")
        return {}


async def learn_from_user_feedback(
    user_id: str,
    dataset_id: str,
    chart_type: str,
    feedback_type: str,
    feedback_value: any
):
    """
    Learn from explicit user feedback
    
    Args:
        user_id: User providing feedback
        dataset_id: Dataset being analyzed
        chart_type: Chart receiving feedback
        feedback_type: Type of feedback (rating, useful, not_useful, suggestion)
        feedback_value: The feedback value (1-5 rating, boolean, or text)
    """
    try:
        feedback_data = {
            "event_type": "user_feedback",
            "user_id": user_id,
            "dataset_id": dataset_id,
            "chart_type": chart_type,
            "feedback_type": feedback_type,
            "feedback_value": feedback_value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await db.analytics_tracking.insert_one(feedback_data)
        
        # Update chart recommendation weights based on feedback
        if feedback_type == "rating" and isinstance(feedback_value, (int, float)):
            await update_chart_weights(chart_type, feedback_value)
        
        logger.info(f"Learned from user feedback: {feedback_type} for {chart_type}")
    
    except Exception as e:
        logger.error(f"Error learning from user feedback: {str(e)}")


async def update_chart_weights(chart_type: str, rating: float):
    """Update internal weights for chart recommendations based on ratings"""
    try:
        # Store or update weights in a separate collection
        await db.chart_weights.update_one(
            {"chart_type": chart_type},
            {
                "$inc": {"total_ratings": 1, "rating_sum": rating},
                "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}
            },
            upsert=True
        )
        
        logger.info(f"Updated weights for chart type: {chart_type}")
    
    except Exception as e:
        logger.error(f"Error updating chart weights: {str(e)}")
