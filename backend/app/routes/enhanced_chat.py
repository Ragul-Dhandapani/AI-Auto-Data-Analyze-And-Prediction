"""
Enhanced Chat API Endpoint
Provides comprehensive AI-powered chat with dataset awareness
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from app.services.enhanced_chat_service import EnhancedChatService
from app.database.adapters.factory import get_database_adapter

router = APIRouter(prefix="/enhanced-chat", tags=["enhanced-chat"])
logger = logging.getLogger(__name__)

# Initialize chat service
chat_service = EnhancedChatService()


class ChatRequest(BaseModel):
    message: str
    dataset_id: str
    conversation_history: Optional[List[Dict]] = []


@router.post("/message")
async def send_chat_message(request: ChatRequest):
    """
    Send a message to the enhanced AI chat assistant
    
    Supports:
    - Dataset awareness
    - Chart creation
    - Model insights
    - Analytical assistance
    - Natural language queries
    """
    try:
        db_adapter = get_database_adapter()
        
        # Get dataset
        dataset_doc = await db_adapter.get_dataset(request.dataset_id)
        if not dataset_doc:
            return {
                'response': "⚠️ Dataset not found. Please select a valid dataset.",
                'action': 'error',
                'data': {},
                'requires_confirmation': False,
                'suggestions': ['Select a dataset', 'Upload new data']
            }
        
        # Load dataframe if needed
        dataset_df = None
        if dataset_doc.get('data'):
            import pandas as pd
            import json
            try:
                # Try to load data from storage
                dataset_df = pd.DataFrame(dataset_doc.get('data', []))
            except:
                logger.warning(f"Could not load dataframe for dataset {request.dataset_id}")
        
        # Get analysis results if available (from localStorage or recent training)
        analysis_results = None
        # TODO: Fetch from training metadata or workspace
        
        # Process message
        response = await chat_service.process_message(
            message=request.message,
            dataset_id=request.dataset_id,
            dataset=dataset_df,
            analysis_results=analysis_results,
            conversation_history=request.conversation_history
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Enhanced chat error: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Chat processing failed: {str(e)}")


@router.post("/test")
async def test_chat_scenarios():
    """
    Test endpoint to verify all chat scenarios
    Returns test results for all required functionality
    """
    import pandas as pd
    import numpy as np
    
    # Create test dataset
    test_data = pd.DataFrame({
        'id': range(1, 101),
        'price': np.random.uniform(100, 1000, 100),
        'quantity': np.random.randint(1, 50, 100),
        'revenue': np.random.uniform(1000, 50000, 100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'date': pd.date_range('2024-01-01', periods=100)
    })
    
    # Add some missing values
    test_data.loc[np.random.choice(100, 10, replace=False), 'price'] = np.nan
    
    # Create mock analysis results
    mock_results = {
        'problem_type': 'regression',
        'ml_models': [
            {
                'model_name': 'XGBoost',
                'r2_score': 0.92,
                'rmse': 15000,
                'mae': 12000,
                'is_best': True,
                'target_column': 'revenue'
            },
            {
                'model_name': 'Random Forest',
                'r2_score': 0.89,
                'rmse': 18000,
                'mae': 14000,
                'is_best': False,
                'target_column': 'revenue'
            }
        ],
        'feature_importance': {
            'price': 0.65,
            'quantity': 0.25,
            'id': 0.10
        }
    }
    
    # Test scenarios
    test_cases = [
        # Dataset Awareness Tests
        {'name': 'List Columns', 'message': 'show me column names'},
        {'name': 'Dataset Size', 'message': 'what is the dataset size?'},
        {'name': 'Statistics', 'message': 'show statistics for price'},
        {'name': 'Data Types', 'message': 'what are the data types?'},
        {'name': 'Missing Values', 'message': 'check for null values'},
        {'name': 'Correlation', 'message': 'show correlation with revenue'},
        
        # Model Insights Tests
        {'name': 'Prediction Target', 'message': 'what am i predicting?'},
        {'name': 'Model Metrics', 'message': 'show me model metrics'},
        {'name': 'Best Model', 'message': 'which model is best?'},
        {'name': 'Feature Importance', 'message': 'show feature importance'},
        {'name': 'Model Comparison', 'message': 'compare models'},
        
        # Analytical Assistance
        {'name': 'Anomaly Detection', 'message': 'detect anomalies'},
        {'name': 'Trends', 'message': 'show me trends'},
        {'name': 'Suggestions', 'message': 'what next?'},
    ]
    
    results = []
    
    for test in test_cases:
        try:
            response = await chat_service.process_message(
                message=test['message'],
                dataset_id='test-dataset',
                dataset=test_data,
                analysis_results=mock_results if 'model' in test['name'].lower() or 'prediction' in test['name'].lower() else None,
                conversation_history=[]
            )
            
            results.append({
                'test': test['name'],
                'status': '✅ PASS',
                'message': test['message'],
                'response_length': len(response['response']),
                'action': response['action'],
                'has_suggestions': len(response['suggestions']) > 0
            })
        except Exception as e:
            results.append({
                'test': test['name'],
                'status': '❌ FAIL',
                'message': test['message'],
                'error': str(e)
            })
    
    # Summary
    passed = sum(1 for r in results if r['status'] == '✅ PASS')
    total = len(results)
    
    return {
        'summary': {
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': f"{(passed/total)*100:.1f}%"
        },
        'results': results
    }
