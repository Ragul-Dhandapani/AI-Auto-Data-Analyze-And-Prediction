"""
Training Metadata Routes
Handles training history and metadata
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.database.mongodb import db, fs
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
        
        # Get dataset
        dataset = await db.datasets.find_one({"id": dataset_id}, {"_id": 0})
        if not dataset:
            raise HTTPException(404, "Dataset not found")
        
        # Get saved states for this dataset
        saved_states = await db.saved_states.find(
            {"dataset_id": dataset_id},
            {"_id": 0}
        ).sort("created_at", -1).to_list(length=100)
        
        # Prepare metadata
        dataset_name = dataset.get("name", "Unknown Dataset")
        training_count = dataset.get("training_count", 0)
        row_count = dataset.get("row_count", 0)
        column_count = dataset.get("column_count", 0)
        
        # Calculate scores from states
        initial_scores = {}
        current_scores = {}
        
        if saved_states:
            sorted_states = sorted(saved_states, key=lambda x: x.get("created_at", ""))
            
            if len(sorted_states) > 0:
                first_state = sorted_states[0]
                first_analysis = first_state.get("analysis_data", {})
                first_models = first_analysis.get("models", []) or first_analysis.get("ml_models", [])
                
                for model in first_models:
                    model_name = model.get("model_name")
                    r2_score = model.get("r2_score", 0)
                    initial_scores[model_name] = r2_score
                
                latest_state = sorted_states[-1]
                latest_analysis = latest_state.get("analysis_data", {})
                latest_models = latest_analysis.get("models", []) or latest_analysis.get("ml_models", [])
                
                for model in latest_models:
                    model_name = model.get("model_name")
                    r2_score = model.get("r2_score", 0)
                    current_scores[model_name] = r2_score
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for PDF elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        elements.append(Paragraph("PROMISE AI - Training Metadata Report", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Dataset Information
        elements.append(Paragraph("Dataset Information", heading_style))
        dataset_info = [
            ["Dataset Name:", dataset_name],
            ["Total Records:", f"{row_count:,}"],
            ["Total Columns:", str(column_count)],
            ["Training Count:", str(training_count)],
            ["Report Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        ]
        
        dataset_table = Table(dataset_info, colWidths=[2*inch, 4*inch])
        dataset_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(dataset_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Model Performance
        if initial_scores or current_scores:
            elements.append(Paragraph("Model Performance", heading_style))
            
            model_data = [["Model Name", "Initial Score", "Current Score", "Improvement"]]
            
            all_models = set(list(initial_scores.keys()) + list(current_scores.keys()))
            for model_name in all_models:
                initial = initial_scores.get(model_name, 0)
                current = current_scores.get(model_name, 0)
                improvement = ((current - initial) / initial * 100) if initial > 0 else 0
                
                model_data.append([
                    model_name,
                    f"{initial:.3f}" if initial else "N/A",
                    f"{current:.3f}" if current else "N/A",
                    f"{improvement:+.1f}%" if improvement else "0%"
                ])
            
            model_table = Table(model_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            model_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
            ]))
            elements.append(model_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Workspaces
        if saved_states:
            elements.append(Paragraph(f"Saved Workspaces ({len(saved_states)})", heading_style))
            
            workspace_data = [["Workspace Name", "Created At", "Status"]]
            for state in saved_states[:10]:  # Limit to 10 most recent
                workspace_name = state.get("state_name", "Unnamed")
                created_at = state.get("created_at", "Unknown")
                if created_at != "Unknown":
                    try:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M")
                    except (ValueError, TypeError):
                        pass
                
                workspace_data.append([
                    workspace_name,
                    created_at,
                    "Active"
                ])
            
            workspace_table = Table(workspace_data, colWidths=[2.5*inch, 2*inch, 2*inch])
            workspace_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
            ]))
            elements.append(workspace_table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Return PDF as streaming response
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=training_metadata_{dataset_id}.pdf"
            }
        )
        
    except ImportError:
        raise HTTPException(500, "PDF generation requires reportlab library. Please install: pip install reportlab")
    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Failed to generate PDF: {str(e)}")


@router.get("/metadata")
async def get_training_metadata():
    """Get comprehensive training metadata for all datasets"""
    try:
        # Get all datasets
        datasets_cursor = db.datasets.find({}, {"_id": 0})
        datasets = await datasets_cursor.to_list(length=None)
        
        # Get all saved states
        states_cursor = db.analysis_states.find({}, {"_id": 0})
        saved_states = await states_cursor.to_list(length=None)
        
        # Organize metadata
        metadata = []
        
        for dataset in datasets:
            dataset_id = dataset.get("id")
            dataset_name = dataset.get("name")
            
            # Get workspaces for this dataset
            dataset_states = [s for s in saved_states if s.get("dataset_id") == dataset_id]
            
            # Calculate training metadata
            training_count = dataset.get("training_count", 0)
            last_trained = dataset.get("last_trained_at")
            
            # Get model scores (from latest workspace if available)
            initial_scores = {}
            current_scores = {}
            initial_score = None  # Single score for frontend compatibility
            current_score = None  # Single score for frontend compatibility
            
            if dataset_states:
                # Sort states by creation date
                sorted_states = sorted(
                    dataset_states,
                    key=lambda x: x.get("created_at", ""),
                    reverse=False  # Oldest first
                )
                
                # Get initial state (oldest)
                if len(sorted_states) > 0:
                    first_state = sorted_states[0]
                    first_analysis = first_state.get("analysis_data", {})
                    first_models = first_analysis.get("models", []) or first_analysis.get("ml_models", [])
                    
                    if first_models:
                        # Get best model from first training
                        best_first = max(first_models, key=lambda x: x.get("r2_score", 0))
                        initial_score = best_first.get("r2_score", 0)
                        
                        for model in first_models:
                            model_name = model.get("model_name")
                            r2_score = model.get("r2_score", 0)
                            initial_scores[model_name] = r2_score
                
                # Get latest state
                latest_state = sorted_states[-1]  # Most recent
                latest_analysis = latest_state.get("analysis_data", {})
                latest_models = latest_analysis.get("models", []) or latest_analysis.get("ml_models", [])
                
                if latest_models:
                    # Get best model from latest training
                    best_latest = max(latest_models, key=lambda x: x.get("r2_score", 0))
                    current_score = best_latest.get("r2_score", 0)
                    
                    for model in latest_models:
                        model_name = model.get("model_name")
                        r2_score = model.get("r2_score", 0)
                        current_scores[model_name] = r2_score
            
            # Calculate improvement percentage
            improvement_percentage = 0
            if initial_score and current_score and initial_score > 0:
                improvement_percentage = ((current_score - initial_score) / initial_score) * 100
            
            metadata.append({
                "dataset_id": dataset_id,
                "dataset_name": dataset_name,
                "training_count": training_count,
                "last_trained": last_trained,
                "initial_scores": initial_scores,
                "current_scores": current_scores,
                "initial_score": initial_score if initial_score is not None else 0,  # Frontend expects this
                "current_score": current_score if current_score is not None else 0,  # Frontend expects this
                "improvement_percentage": improvement_percentage,  # Frontend expects this
                "improvement": {
                    model: ((current_scores.get(model, 0) - initial_scores.get(model, 0)) / initial_scores.get(model, 1)) * 100
                    if initial_scores.get(model, 0) > 0 else 0
                    for model in current_scores.keys()
                },
                "workspaces": [
                    {
                        "workspace_name": state.get("state_name"),
                        "saved_at": state.get("created_at"),
                        "workspace_id": state.get("id")
                    }
                    for state in dataset_states
                ],
                "row_count": dataset.get("row_count"),
                "column_count": dataset.get("column_count")
            })
        
        return {"metadata": metadata}
        
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch training metadata: {str(e)}")
