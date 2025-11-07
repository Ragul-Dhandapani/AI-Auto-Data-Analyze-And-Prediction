"""
Training Metadata Routes
Handles training history and metadata
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.database.db_helper import get_db
from datetime import datetime, timezone
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/training", tags=["training"])


@router.get("/metadata/download-pdf/{dataset_id}")
async def download_training_metadata_pdf(dataset_id: str):
    """Generate and download PDF report for training metadata"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        import io
        from fastapi.responses import StreamingResponse
        
        # Get dataset using adapter
        db_adapter = get_db()
        dataset = await db_adapter.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        
        # Get saved states for this dataset using adapter
        saved_states = await db_adapter.list_workspaces(dataset_id)
        
        # Prepare metadata
        dataset_name = dataset.get("name", "Unknown Dataset")
        training_count = dataset.get("training_count", 0)
        row_count = dataset.get("row_count", 0)
        column_count = dataset.get("column_count", 0)
        
        # Calculate scores from states
        initial_scores = {}
        current_scores = {}
        
        for state in saved_states:
            state_name = state.get("state_name", "")
            
            # Extract scores from state data
            if "initial_scores" in state_name.lower():
                try:
                    # Load state data if needed
                    if state.get("storage_type") == "blob":
                        state_data = await db_adapter.retrieve_file(state.get("gridfs_file_id"))
                        import json
                        state_content = json.loads(state_data.decode('utf-8'))
                    else:
                        state_content = state.get("state_data", {})
                    
                    scores = state_content.get("scores", {})
                    initial_scores.update(scores)
                except:
                    pass
            
            elif "current_scores" in state_name.lower() or "final_scores" in state_name.lower():
                try:
                    # Load state data if needed
                    if state.get("storage_type") == "blob":
                        state_data = await db_adapter.retrieve_file(state.get("gridfs_file_id"))
                        import json
                        state_content = json.loads(state_data.decode('utf-8'))
                    else:
                        state_content = state.get("state_data", {})
                    
                    scores = state_content.get("scores", {})
                    current_scores.update(scores)
                except:
                    pass
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Title
        title = Paragraph("Training Metadata Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Dataset Information
        elements.append(Paragraph("Dataset Information", heading_style))
        
        dataset_data = [
            ['Dataset Name', dataset_name],
            ['Dataset ID', dataset_id],
            ['Total Rows', f"{row_count:,}"],
            ['Total Columns', f"{column_count:,}"],
            ['Training Sessions', str(training_count)],
            ['Created At', dataset.get('created_at', 'Unknown')],
            ['Last Updated', dataset.get('updated_at', 'Unknown')]
        ]
        
        dataset_table = Table(dataset_data, colWidths=[2*inch, 3*inch])
        dataset_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(dataset_table)
        elements.append(Spacer(1, 20))
        
        # Model Performance Summary
        if initial_scores or current_scores:
            elements.append(Paragraph("Model Performance Summary", heading_style))
            
            # Combine scores for comparison
            all_models = set(initial_scores.keys()) | set(current_scores.keys())
            
            if all_models:
                performance_data = [['Model', 'Initial Score', 'Current Score', 'Improvement']]
                
                for model in sorted(all_models):
                    initial = initial_scores.get(model, 'N/A')
                    current = current_scores.get(model, 'N/A')
                    
                    if isinstance(initial, (int, float)) and isinstance(current, (int, float)):
                        improvement = f"{((current - initial) / initial * 100):+.2f}%"
                        initial = f"{initial:.4f}"
                        current = f"{current:.4f}"
                    else:
                        improvement = 'N/A'
                        initial = str(initial) if initial != 'N/A' else 'N/A'
                        current = str(current) if current != 'N/A' else 'N/A'
                    
                    performance_data.append([model, initial, current, improvement])
                
                performance_table = Table(performance_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.1*inch])
                performance_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(performance_table)
                elements.append(Spacer(1, 20))
        
        # Training History
        if saved_states:
            elements.append(Paragraph("Training History", heading_style))
            
            history_data = [['State Name', 'Created At', 'Size (KB)', 'Storage Type']]
            
            for state in saved_states[:10]:  # Limit to recent 10 states
                state_name = state.get("state_name", "Unknown")
                created_at = state.get("created_at", "Unknown")
                size_bytes = state.get("size_bytes", 0)
                size_kb = f"{size_bytes / 1024:.2f}" if size_bytes else "0"
                storage_type = state.get("storage_type", "direct")
                
                history_data.append([state_name, created_at, size_kb, storage_type])
            
            history_table = Table(history_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch])
            history_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(history_table)
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer and return as response
        buffer.seek(0)
        
        return StreamingResponse(
            io.BytesIO(buffer.read()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=training_metadata_{dataset_id}.pdf"}
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise HTTPException(500, f"Error generating PDF: {str(e)}")


@router.get("/metadata")
async def get_all_training_metadata(limit: int = 100):
    """Get comprehensive training metadata for ALL models trained (35+ models supported)"""
    try:
        db_adapter = get_db()
        
        # Get training metadata directly from training_metadata table
        training_records = await db_adapter.get_training_metadata(dataset_id=None, limit=limit)
        
        logger.info(f"✅ Retrieved {len(training_records)} training metadata records")
        
        # Group by dataset for organized display
        grouped_metadata = {}
        
        for record in training_records:
            dataset_id = record.get("dataset_id")
            dataset_name = record.get("dataset_name", "Unknown Dataset")
            
            if dataset_id not in grouped_metadata:
                grouped_metadata[dataset_id] = {
                    "dataset_id": dataset_id,
                    "dataset_name": dataset_name,
                    "training_count": 0,
                    "models_trained": [],
                    "unique_models": set(),
                    "last_training": None,
                    "problem_types": set()
                }
            
            # Add to count
            grouped_metadata[dataset_id]["training_count"] += 1
            grouped_metadata[dataset_id]["unique_models"].add(record.get("model_type"))
            grouped_metadata[dataset_id]["problem_types"].add(record.get("problem_type"))
            
            # Update last training
            if not grouped_metadata[dataset_id]["last_training"] or record.get("created_at") > grouped_metadata[dataset_id]["last_training"]:
                grouped_metadata[dataset_id]["last_training"] = record.get("created_at")
            
            # Add model details
            model_info = {
                "id": record.get("id"),
                "model_type": record.get("model_type"),
                "problem_type": record.get("problem_type"),
                "target_variable": record.get("target_variable"),
                "feature_variables": record.get("feature_variables"),
                "metrics": record.get("metrics", {}),
                "training_duration": record.get("training_duration", 0.0),
                "created_at": record.get("created_at")
            }
            grouped_metadata[dataset_id]["models_trained"].append(model_info)
        
        # Convert to list and clean up
        metadata_list = []
        for dataset_id, data in grouped_metadata.items():
            data["unique_models"] = len(data["unique_models"])
            data["problem_types"] = list(data["problem_types"])
            # Sort models by created_at descending
            data["models_trained"].sort(key=lambda x: x.get("created_at", ""), reverse=True)
            metadata_list.append(data)
        
        # Sort by last_training descending
        metadata_list.sort(key=lambda x: x.get("last_training", ""), reverse=True)
        
        return {
            "metadata": metadata_list,
            "total_training_sessions": len(training_records),
            "total_datasets": len(grouped_metadata)
        }
    
    except Exception as e:
        logger.error(f"Failed to fetch training metadata: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Failed to fetch training metadata: {str(e)}")


@router.get("/metadata/{dataset_id}")
async def get_training_metadata(dataset_id: str):
    """Get training metadata for a dataset"""
    try:
        db_adapter = get_db()
        
        # Get dataset
        dataset = await db_adapter.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        
        # Get saved states
        saved_states = await db_adapter.list_workspaces(dataset_id)
        
        # Prepare response
        metadata = {
            "dataset_id": dataset_id,
            "dataset_name": dataset.get("name", "Unknown"),
            "training_count": dataset.get("training_count", 0),
            "last_trained_at": dataset.get("last_trained_at"),
            "created_at": dataset.get("created_at"),
            "updated_at": dataset.get("updated_at"),
            "row_count": dataset.get("row_count", 0),
            "column_count": dataset.get("column_count", 0),
            "saved_states_count": len(saved_states),
            "saved_states": [
                {
                    "id": state.get("id"),
                    "state_name": state.get("state_name"),
                    "created_at": state.get("created_at"),
                    "size_bytes": state.get("size_bytes", 0),
                    "storage_type": state.get("storage_type", "direct")
                }
                for state in saved_states
            ]
        }
        
        return metadata
        
    except Exception as e:
        logger.error(f"Error getting training metadata: {str(e)}")
        raise HTTPException(500, f"Error getting training metadata: {str(e)}")


@router.delete("/metadata/{dataset_id}")
async def clear_training_metadata(dataset_id: str):
    """Clear all training metadata for a dataset"""
    try:
        db_adapter = get_db()
        
        # Get dataset to verify it exists
        dataset = await db_adapter.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        
        # Get all workspaces for this dataset
        workspaces = await db_adapter.list_workspaces(dataset_id)
        
        # Delete each workspace
        deleted_count = 0
        for workspace in workspaces:
            success = await db_adapter.delete_workspace(workspace.get("id"))
            if success:
                deleted_count += 1
        
        # Reset training count in dataset
        await db_adapter.update_dataset(dataset_id, {
            "training_count": 0,
            "last_trained_at": None
        })
        
        return {
            "message": f"Cleared {deleted_count} training states for dataset {dataset_id}",
            "deleted_states": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error clearing training metadata: {str(e)}")
        raise HTTPException(500, f"Error clearing training metadata: {str(e)}")


@router.get("/stats")
async def get_training_stats():
    """Get overall training statistics"""
    try:
        db_adapter = get_db()
        
        # Get all datasets
        datasets = await db_adapter.list_datasets(limit=1000)  # Get more datasets for stats
        
        total_datasets = len(datasets)
        total_training_sessions = sum(d.get("training_count", 0) for d in datasets)
        
        # Count datasets with training
        trained_datasets = len([d for d in datasets if d.get("training_count", 0) > 0])
        
        # Get recent activity (datasets updated in last 7 days)
        from datetime import datetime, timedelta
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        recent_activity = len([
            d for d in datasets 
            if d.get("updated_at", "") > week_ago
        ])
        
        stats = {
            "total_datasets": total_datasets,
            "trained_datasets": trained_datasets,
            "untrained_datasets": total_datasets - trained_datasets,
            "total_training_sessions": total_training_sessions,
            "avg_training_per_dataset": total_training_sessions / total_datasets if total_datasets > 0 else 0,
            "recent_activity_7_days": recent_activity
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting training stats: {str(e)}")
        raise HTTPException(500, f"Error getting training stats: {str(e)}")
