"""
Model Export Routes
Export trained models with requirements, README, and scripts
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import io
import zipfile
import logging
from datetime import datetime

from app.database.db_helper import get_db
from app.services.model_export_service import (
    sanitize_filename,
    generate_requirements_txt,
    generate_readme_md
)
from app.services.model_script_generator import generate_model_script

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/model", tags=["model-export"])


@router.post("/export")
async def export_models(request: Dict[str, Any]):
    """
    Export selected trained models as ZIP with requirements, README, and scripts
    
    Request: {"dataset_id": "uuid", "model_ids": ["id1", "id2"]}
    """
    try:
        dataset_id = request.get("dataset_id")
        model_ids = request.get("model_ids", [])
        
        if not dataset_id:
            raise HTTPException(400, "dataset_id is required")
        if not model_ids:
            raise HTTPException(400, "At least one model_id required")
        
        logger.info(f"📦 Exporting {len(model_ids)} models for dataset {dataset_id}")
        
        db_adapter = get_db()
        dataset = await db_adapter.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(404, f"Dataset {dataset_id} not found")
        
        dataset_name = dataset.get("name", "unknown_dataset")
        
        models_metadata = []
        for model_id in model_ids:
            metadata = await db_adapter.get_training_metadata(model_id)
            if metadata:
                models_metadata.append(metadata)
            else:
                logger.warning(f"Model {model_id} not found, skipping")
        
        if not models_metadata:
            raise HTTPException(404, "No valid models found")
        
        logger.info(f"✅ Found {len(models_metadata)} models to export")
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            requirements = generate_requirements_txt(models_metadata)
            zip_file.writestr("requirements.txt", requirements)
            logger.info("✅ Added requirements.txt")
            
            readme = generate_readme_md(dataset, models_metadata)
            zip_file.writestr("README.md", readme)
            logger.info("✅ Added README.md")
            
            for idx, metadata in enumerate(models_metadata, 1):
                script_name = f"model_{idx}_{sanitize_filename(metadata.get('model_type', 'model'))}.py"
                script = generate_model_script(metadata, dataset)
                zip_file.writestr(script_name, script)
                logger.info(f"✅ Added {script_name}")
        
        zip_buffer.seek(0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"models_{sanitize_filename(dataset_name)}_{timestamp}.zip"
        
        logger.info(f"✅ Export complete: {zip_filename}")
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export failed: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Export failed: {str(e)}")
