"""
Instant API Deployment - Deploy trained models as REST APIs in 1 click

THIS IS THE KILLER FEATURE:
- Copilot: Write code, set up server, deploy manually
- PROMISE AI: Click button → Model is live as API instantly
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import joblib
import numpy as np
from pathlib import Path
import uuid
import logging

router = APIRouter(prefix="/instant-api", tags=["Instant API Deployment"])
logger = logging.getLogger(__name__)


# In-memory registry of deployed APIs
deployed_apis = {}


class DeployModelRequest(BaseModel):
    model_id: str  # dataset_id
    model_name: str
    api_name: str  # User-friendly name for the API
    description: Optional[str] = None
    require_auth: bool = False
    rate_limit: Optional[int] = 1000  # requests per hour


class PredictionRequest(BaseModel):
    features: List[float]
    return_confidence: bool = False


class BatchPredictionRequest(BaseModel):
    features: List[List[float]]
    return_confidence: bool = False


@router.post("/deploy")
async def deploy_model_as_api(request: DeployModelRequest):
    """
    Deploy a trained model as a REST API endpoint instantly
    
    Returns:
        {
            'api_id': 'unique-id',
            'api_endpoint': '/api/instant-api/predict/{api_id}',
            'batch_endpoint': '/api/instant-api/predict-batch/{api_id}',
            'docs': '/api/instant-api/docs/{api_id}',
            'status': 'deployed'
        }
    """
    
    try:
        # Load model
        model_path = Path(f"/app/backend/models/{request.model_id}/{request.model_name}.pkl")
        
        if not model_path.exists():
            raise HTTPException(status_code=404, detail=f"Model not found: {request.model_name}")
        
        model = joblib.load(model_path)
        
        # Generate unique API ID
        api_id = str(uuid.uuid4())[:8]
        
        # Register API
        deployed_apis[api_id] = {
            'model': model,
            'model_id': request.model_id,
            'model_name': request.model_name,
            'api_name': request.api_name,
            'description': request.description,
            'require_auth': request.require_auth,
            'rate_limit': request.rate_limit,
            'created_at': str(pd.Timestamp.now()),
            'request_count': 0,
            'status': 'active'
        }
        
        logger.info(f"✅ Deployed API: {api_id} ({request.api_name})")
        
        return {
            'status': 'success',
            'api_id': api_id,
            'api_name': request.api_name,
            'endpoints': {
                'predict': f"/api/instant-api/predict/{api_id}",
                'predict_batch': f"/api/instant-api/predict-batch/{api_id}",
                'status': f"/api/instant-api/status/{api_id}",
                'docs': f"/api/instant-api/docs/{api_id}"
            },
            'curl_example': f'''curl -X POST https://mlexport-hub.preview.emergentagent.com/api/instant-api/predict/{api_id} \\
  -H "Content-Type: application/json" \\
  -d '{{"features": [1.0, 2.0, 3.0]}}'
''',
            'python_example': f'''import requests

response = requests.post(
    'https://mlexport-hub.preview.emergentagent.com/api/instant-api/predict/{api_id}',
    json={{'features': [1.0, 2.0, 3.0]}}
)
print(response.json())
''',
            'message': f"Model '{request.api_name}' deployed successfully! Ready for predictions."
        }
    
    except Exception as e:
        logger.error(f"❌ Deployment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")


@router.post("/predict/{api_id}")
async def predict_with_deployed_model(api_id: str, request: PredictionRequest):
    """
    Make a prediction using a deployed model
    
    Example:
    ```
    POST /api/instant-api/predict/abc123
    {
        "features": [1.0, 2.0, 3.0],
        "return_confidence": true
    }
    
    Response:
    {
        "prediction": 42.5,
        "confidence": 0.89,
        "api_id": "abc123",
        "timestamp": "2025-11-18T12:00:00"
    }
    ```
    """
    
    if api_id not in deployed_apis:
        raise HTTPException(status_code=404, detail=f"API not found: {api_id}")
    
    api_info = deployed_apis[api_id]
    model = api_info['model']
    
    try:
        # Make prediction
        features_array = np.array(request.features).reshape(1, -1)
        prediction = model.predict(features_array)[0]
        
        # Get confidence if available
        confidence = None
        if request.return_confidence and hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features_array)[0]
            confidence = float(np.max(proba))
        
        # Update request count
        api_info['request_count'] += 1
        
        result = {
            'prediction': float(prediction),
            'api_id': api_id,
            'api_name': api_info['api_name'],
            'timestamp': str(pd.Timestamp.now())
        }
        
        if confidence:
            result['confidence'] = confidence
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/predict-batch/{api_id}")
async def predict_batch_with_deployed_model(api_id: str, request: BatchPredictionRequest):
    """
    Make batch predictions using a deployed model
    
    Example:
    ```
    POST /api/instant-api/predict-batch/abc123
    {
        "features": [
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0]
        ],
        "return_confidence": true
    }
    
    Response:
    {
        "predictions": [42.5, 45.2, 48.1],
        "confidences": [0.89, 0.92, 0.85],
        "count": 3
    }
    ```
    """
    
    if api_id not in deployed_apis:
        raise HTTPException(status_code=404, detail=f"API not found: {api_id}")
    
    api_info = deployed_apis[api_id]
    model = api_info['model']
    
    try:
        # Make predictions
        features_array = np.array(request.features)
        predictions = model.predict(features_array)
        
        # Get confidences if available
        confidences = None
        if request.return_confidence and hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features_array)
            confidences = np.max(proba, axis=1).tolist()
        
        # Update request count
        api_info['request_count'] += len(request.features)
        
        result = {
            'predictions': predictions.tolist(),
            'count': len(predictions),
            'api_id': api_id,
            'api_name': api_info['api_name'],
            'timestamp': str(pd.Timestamp.now())
        }
        
        if confidences:
            result['confidences'] = confidences
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Batch prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@router.get("/status/{api_id}")
async def get_api_status(api_id: str):
    """
    Get status and statistics for a deployed API
    """
    
    if api_id not in deployed_apis:
        raise HTTPException(status_code=404, detail=f"API not found: {api_id}")
    
    api_info = deployed_apis[api_id]
    
    return {
        'api_id': api_id,
        'api_name': api_info['api_name'],
        'description': api_info['description'],
        'model_name': api_info['model_name'],
        'status': api_info['status'],
        'created_at': api_info['created_at'],
        'total_requests': api_info['request_count'],
        'rate_limit': api_info['rate_limit'],
        'health': 'healthy' if api_info['status'] == 'active' else 'inactive'
    }


@router.get("/list")
async def list_deployed_apis():
    """
    List all deployed APIs
    """
    
    return {
        'total_apis': len(deployed_apis),
        'apis': [
            {
                'api_id': api_id,
                'api_name': info['api_name'],
                'model_name': info['model_name'],
                'status': info['status'],
                'request_count': info['request_count'],
                'endpoints': {
                    'predict': f"/api/instant-api/predict/{api_id}",
                    'status': f"/api/instant-api/status/{api_id}"
                }
            }
            for api_id, info in deployed_apis.items()
        ]
    }


@router.delete("/undeploy/{api_id}")
async def undeploy_api(api_id: str):
    """
    Undeploy (remove) an API
    """
    
    if api_id not in deployed_apis:
        raise HTTPException(status_code=404, detail=f"API not found: {api_id}")
    
    api_name = deployed_apis[api_id]['api_name']
    del deployed_apis[api_id]
    
    logger.info(f"✅ Undeployed API: {api_id} ({api_name})")
    
    return {
        'status': 'success',
        'message': f"API '{api_name}' has been undeployed"
    }


@router.get("/docs/{api_id}")
async def get_api_documentation(api_id: str):
    """
    Get auto-generated documentation for a deployed API
    """
    
    if api_id not in deployed_apis:
        raise HTTPException(status_code=404, detail=f"API not found: {api_id}")
    
    api_info = deployed_apis[api_id]
    
    return {
        'api_id': api_id,
        'api_name': api_info['api_name'],
        'description': api_info['description'],
        'endpoints': {
            'single_prediction': {
                'method': 'POST',
                'url': f"/api/instant-api/predict/{api_id}",
                'request_body': {
                    'features': [1.0, 2.0, 3.0],
                    'return_confidence': False
                },
                'response': {
                    'prediction': 42.5,
                    'api_id': api_id,
                    'timestamp': '2025-11-18T12:00:00'
                }
            },
            'batch_prediction': {
                'method': 'POST',
                'url': f"/api/instant-api/predict-batch/{api_id}",
                'request_body': {
                    'features': [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
                    'return_confidence': False
                },
                'response': {
                    'predictions': [42.5, 45.2],
                    'count': 2
                }
            }
        },
        'examples': {
            'curl': f'''curl -X POST https://mlexport-hub.preview.emergentagent.com/api/instant-api/predict/{api_id} \\
  -H "Content-Type: application/json" \\
  -d '{{"features": [1.0, 2.0, 3.0]}}'
''',
            'python': f'''import requests

url = 'https://mlexport-hub.preview.emergentagent.com/api/instant-api/predict/{api_id}'
data = {{'features': [1.0, 2.0, 3.0]}}

response = requests.post(url, json=data)
result = response.json()
print(f"Prediction: {{result['prediction']}}")
''',
            'javascript': f'''const response = await fetch(
  'https://mlexport-hub.preview.emergentagent.com/api/instant-api/predict/{api_id}',
  {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{features: [1.0, 2.0, 3.0]}})
  }}
);
const result = await response.json();
console.log('Prediction:', result.prediction);
'''
        }
    }


# Import pandas for timestamps
import pandas as pd
