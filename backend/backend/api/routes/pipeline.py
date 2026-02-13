"""
Pipeline routes for direct execution of AURA preprocessing pipeline.
Handles file upload, processing, and result download.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
import os
import uuid
import logging
import shutil
from datetime import datetime
from pathlib import Path

from backend.backend.core.pipeline import AuraPipeline
from backend.backend.core.agent.tools import register_dataset, get_dataset
from backend.backend.core.agent.graph import run_agentic_pipeline
import pandas as pd
from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)
router = APIRouter()

# Storage for uploaded files and results
UPLOAD_DIR = "outputs/uploads"
RESULTS_DIR = "outputs/results"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


@router.post("/run")
async def run_pipeline(
    file: UploadFile = File(...),
    mode: str = "auto",
    target_col: Optional[str] = None,
    test_size: float = 0.2
):
    """
    Run the AURA preprocessing pipeline on an uploaded CSV file.
    
    Parameters:
    - file: CSV file to process
    - mode: Execution mode ('auto' or 'step')
    - target_col: Target column name (auto-detected if not provided)
    - test_size: Train/test split ratio (default: 0.2)
    
    Returns:
    - Pipeline execution results including model performance and download links
    """
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Generate unique job ID
    job_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create job-specific directories
    job_upload_dir = os.path.join(UPLOAD_DIR, job_id)
    job_results_dir = os.path.join(RESULTS_DIR, job_id)
    os.makedirs(job_upload_dir, exist_ok=True)
    os.makedirs(job_results_dir, exist_ok=True)
    
    # Save uploaded file
    file_path = os.path.join(job_upload_dir, f"{timestamp}_{file.filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Job {job_id}: File uploaded to {file_path}")
        
    except Exception as e:
        logger.error(f"Job {job_id}: File upload failed - {str(e)}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    # Run the pipeline
    try:
        logger.info(f"Job {job_id}: Starting pipeline execution")
        
        # Initialize pipeline - matching YOUR exact structure
        pipeline = AuraPipeline(
            filepath=file_path,
            mode=mode,
            target_col=target_col
        )
        
        if mode == "agentic":
            logger.info(f"Job {job_id}: Running in AGENTIC mode")
            # 1. Load Data
            df = pd.read_csv(file_path)
            
            # 2. Register with Agent Memory
            register_dataset(job_id, df)
            
            # 3. Run Agent
            agent_output = run_agentic_pipeline(job_id)
            
            # 4. Retrieve Results
            final_df = get_dataset(job_id)
            
            # 5. Save Results (Mimic AuraPipeline output)
            processed_path = file_path.replace(".csv", "_processed.csv")
            final_df.to_csv(processed_path, index=False)
            
            # Extract steps from messages
            steps_log = []
            if agent_output and "messages" in agent_output:
                for m in agent_output["messages"]:
                     # Only show key decisions or tool outputs
                    if hasattr(m, "tool_calls") and m.tool_calls:
                        for tc in m.tool_calls:
                            steps_log.append(f"Tool Call: {tc['name']}")
                    elif hasattr(m, "content") and m.content:
                        # Log shortened content
                        steps_log.append(str(m.content)[:100])

            results = {
                "success": True,
                "processed_data_path": processed_path,
                "preprocessing_steps": steps_log,
                "pipeline_info": {"original_shape": df.shape},
                "report": {"dataset_info": {"processed_shape": final_df.shape}},
                "model_results": {"results": {"accuracy": "N/A (Agentic Mode)"}}
            }
            
        else:
            # Run standard pipeline
            results = pipeline.run_full_pipeline(
                test_size=test_size,
                save_data=True,
                save_explanations=True
            )
        
        # Organize output files
        output_files = {
            "processed_data": None,
            "report": None,
            "explanations": None
        }
        
        # Move processed CSV to job results directory
        if results.get("processed_data_path") and os.path.exists(results["processed_data_path"]):
            processed_filename = os.path.basename(results["processed_data_path"])
            new_processed_path = os.path.join(job_results_dir, processed_filename)
            shutil.move(results["processed_data_path"], new_processed_path)
            output_files["processed_data"] = new_processed_path
            logger.info(f"Job {job_id}: Moved processed data to {new_processed_path}")
        
        # Move report.json
        report_path = "outputs/report.json"
        if os.path.exists(report_path):
            new_report_path = os.path.join(job_results_dir, "report.json")
            shutil.move(report_path, new_report_path)
            output_files["report"] = new_report_path
            logger.info(f"Job {job_id}: Moved report to {new_report_path}")
        
        # Move aura_explanations.json
        explanations_path = "outputs/aura_explanations.json"
        if os.path.exists(explanations_path):
            new_explanations_path = os.path.join(job_results_dir, "aura_explanations.json")
            shutil.move(explanations_path, new_explanations_path)
            output_files["explanations"] = new_explanations_path
            logger.info(f"Job {job_id}: Moved explanations to {new_explanations_path}")
        
        logger.info(f"Job {job_id}: Pipeline completed successfully")
        
        # Prepare comprehensive response
        response = {
            "job_id": job_id,
            "status": "completed",
            "success": results.get("success", True),
            "timestamp": datetime.now().isoformat(),
            "input_file": file.filename,
            "mode": mode,
            "target_column": pipeline.target_col,
            "download_links": {
                "processed_data": f"/api/pipeline/download/{job_id}/processed_data",
                "report": f"/api/pipeline/download/{job_id}/report",
                "explanations": f"/api/pipeline/download/{job_id}/explanations"
            },
            "results_summary": {
                "original_shape": results.get("pipeline_info", {}).get("original_shape"),
                "processed_shape": results.get("report", {}).get("dataset_info", {}).get("processed_shape"),
                "preprocessing_steps": len(results.get("preprocessing_steps", [])),
                "model_performance": results.get("model_results", {}).get("results", {})
            }
        }
        
        # Include error if pipeline failed
        if not results.get("success"):
            response["error"] = results.get("error", "Unknown error")
        
        return response
    
    except Exception as e:
        logger.error(f"Job {job_id}: Pipeline execution failed - {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline execution failed: {str(e)}"
        )


@router.get("/download/{job_id}/{file_type}")
async def download_result(job_id: str, file_type: str):
    """
    Download a result file from a completed pipeline job.
    
    Parameters:
    - job_id: Job identifier
    - file_type: Type of file ('processed_data', 'report', 'explanations')
    
    Returns:
    - File download response
    """
    
    job_results_dir = os.path.join(RESULTS_DIR, job_id)
    
    if not os.path.exists(job_results_dir):
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Map file types to actual files
    file_mapping = {
        "processed_data": None,  # Will be detected
        "report": "report.json",
        "explanations": "aura_explanations.json"
    }
    
    if file_type not in file_mapping:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Must be one of: {list(file_mapping.keys())}"
        )
    
    # Find the actual file
    if file_type == "processed_data":
        # Find the processed CSV file
        csv_files = [f for f in os.listdir(job_results_dir) if f.endswith('_processed.csv')]
        if not csv_files:
            raise HTTPException(status_code=404, detail="Processed data file not found")
        file_path = os.path.join(job_results_dir, csv_files[0])
    else:
        file_path = os.path.join(job_results_dir, file_mapping[file_type])
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, 
            detail=f"{file_type} file not found for job {job_id}"
        )
    
    # Determine media type
    media_type = "application/json" if file_path.endswith('.json') else "text/csv"
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=os.path.basename(file_path)
    )


@router.get("/jobs")
async def list_jobs():
    """
    List all pipeline jobs (completed and in-progress).
    
    Returns:
    - List of job information
    """
    
    jobs = []
    
    if os.path.exists(RESULTS_DIR):
        for job_id in os.listdir(RESULTS_DIR):
            job_dir = os.path.join(RESULTS_DIR, job_id)
            if os.path.isdir(job_dir):
                # Get job info
                report_path = os.path.join(job_dir, "report.json")
                
                job_info = {
                    "job_id": job_id,
                    "status": "completed" if os.path.exists(report_path) else "failed",
                    "result_files": os.listdir(job_dir),
                    "info_url": f"/api/pipeline/info/{job_id}"
                }
                
                jobs.append(job_info)
    
    return {
        "total_jobs": len(jobs),
        "jobs": jobs
    }


@router.get("/info/{job_id}")
async def get_job_info(job_id: str):
    """
    Get detailed information about a specific job.
    
    Parameters:
    - job_id: Job identifier
    
    Returns:
    - Detailed job information including full report
    """
    
    job_results_dir = os.path.join(RESULTS_DIR, job_id)
    
    if not os.path.exists(job_results_dir):
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Load report if available
    report_path = os.path.join(job_results_dir, "report.json")
    report_data = None
    
    if os.path.exists(report_path):
        import json
        with open(report_path, 'r') as f:
            report_data = json.load(f)
    
    # Load explanations if available
    explanations_path = os.path.join(job_results_dir, "aura_explanations.json")
    explanations_data = None
    
    if os.path.exists(explanations_path):
        import json
        with open(explanations_path, 'r') as f:
            explanations_data = json.load(f)
    
    return {
        "job_id": job_id,
        "status": "completed" if report_data else "incomplete",
        "result_files": os.listdir(job_results_dir),
        "report": report_data,
        "explanations_count": len(explanations_data) if explanations_data else 0,
        "download_links": {
            "processed_data": f"/api/pipeline/download/{job_id}/processed_data",
            "report": f"/api/pipeline/download/{job_id}/report",
            "explanations": f"/api/pipeline/download/{job_id}/explanations"
        }
    }


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a pipeline job and its associated files.
    
    Parameters:
    - job_id: Job identifier
    
    Returns:
    - Deletion confirmation
    """
    
    job_upload_dir = os.path.join(UPLOAD_DIR, job_id)
    job_results_dir = os.path.join(RESULTS_DIR, job_id)
    
    deleted = False
    deleted_items = []
    
    if os.path.exists(job_upload_dir):
        shutil.rmtree(job_upload_dir)
        deleted = True
        deleted_items.append("uploads")
    
    if os.path.exists(job_results_dir):
        shutil.rmtree(job_results_dir)
        deleted = True
        deleted_items.append("results")
    
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return {
        "job_id": job_id,
        "status": "deleted",
        "deleted_items": deleted_items,
        "message": f"Job {job_id} and all associated files deleted successfully"
    }