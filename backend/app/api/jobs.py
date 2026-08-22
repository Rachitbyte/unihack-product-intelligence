import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response

from app.schemas.schemas import JobCreate, JobResponse
from app.db.memory import db
from app.services.ingestion import parse_input_csv
from app.services.output_builder import load_expected_headers, map_to_output, export_to_csv, export_to_xlsx

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

@router.post("", response_model=JobResponse)
def create_job():
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "status": "CREATED",
        "total_rows": 0,
        "processed_rows": 0,
        "failed_rows": 0,
        "created_at": datetime.utcnow(),
        "rows": [],
        "errors": []
    }
    db.jobs[job_id] = job
    return JobResponse(**job)

@router.post("/{job_id}/upload", response_model=JobResponse)
async def upload_file(job_id: str, file: UploadFile = File(...)):
    if job_id not in db.jobs:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
    content = await file.read()
    content_str = content.decode("utf-8")
    
    rows, errors = parse_input_csv(content_str)
    
    job = db.jobs[job_id]
    job["rows"] = rows
    job["errors"] = errors
    job["total_rows"] = len(rows)
    job["processed_rows"] = len(rows)
    job["failed_rows"] = len(errors)
    job["status"] = "COMPLETED"
    
    return JobResponse(**job)

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str):
    if job_id not in db.jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(**db.jobs[job_id])

@router.get("/{job_id}/results")
def get_job_results(job_id: str):
    if job_id not in db.jobs:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = db.jobs[job_id]
    return {
        "rows": [r.dict() for r in job["rows"]],
        "errors": job["errors"]
    }

@router.get("/{job_id}/download/csv")
def download_csv(job_id: str):
    if job_id not in db.jobs:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = db.jobs[job_id]
    headers = load_expected_headers()
    mapped_rows = map_to_output(job["rows"], headers)
    csv_content = export_to_csv(mapped_rows, headers)
    
    return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=job_{job_id}_output.csv"})

@router.get("/{job_id}/download/xlsx")
def download_xlsx(job_id: str):
    if job_id not in db.jobs:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = db.jobs[job_id]
    headers = load_expected_headers()
    mapped_rows = map_to_output(job["rows"], headers)
    xlsx_content = export_to_xlsx(mapped_rows, headers)
    
    return Response(content=xlsx_content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename=job_{job_id}_output.xlsx"})
