import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.schemas.schemas import JobCreate, JobResponse, ProductRow
from app.db.database import get_db
from app.db.models import JobModel, JobRowModel
from app.services.ingestion import parse_input_csv
from app.services.output_builder import load_expected_headers, map_to_output, export_to_csv, export_to_xlsx
from app.services.pipeline import process_product_row

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

def process_job_background(job_id: str):
    # This runs in a separate thread. We need a new DB session.
    from app.db.database import SessionLocal
    db = SessionLocal()
    
    try:
        job = db.query(JobModel).filter(JobModel.id == job_id).first()
        if not job:
            return
            
        job.status = "PROCESSING"
        db.commit()
        
        # Get all rows for this job
        db_rows = db.query(JobRowModel).filter(JobRowModel.job_id == job_id).order_by(JobRowModel.row_id).all()
        
        import time
        import os
        
        # Pacing settings
        min_interval = float(os.environ.get("GEMINI_MIN_REQUEST_INTERVAL_SECONDS", "4.0"))
        
        for db_row in db_rows:
            # Parse the DB JSON back into a ProductRow schema
            row_data = db_row.result_data
            if not row_data:
                # Construct basic row
                row = ProductRow(
                    row_id=db_row.row_id,
                    mfg_part_num=db_row.mfg_part_num,
                    part_desc=db_row.part_desc,
                    part_manuf=db_row.part_manuf
                )
            else:
                row = ProductRow(**row_data)
                
            # Run the AI pipeline
            processed_row = process_product_row(row)
            
            # Save back to DB
            db_row.result_data = processed_row.dict()
            
            # Increment processed counter
            job.processed_rows += 1
            if not processed_row.is_valid:
                job.failed_rows += 1
                
            # Track metrics
            ai_required = False
            ai_quota_exceeded = False
            needs_review = False
            ai_success = False
            
            if processed_row.extraction:
                if processed_row.extraction.reasoning and "Deterministic" not in processed_row.extraction.reasoning:
                    ai_required = True
                if processed_row.extraction.status == "AI_QUOTA_EXCEEDED":
                    ai_quota_exceeded = True
                    ai_required = True
                elif processed_row.extraction.status == "SUCCESS":
                    ai_success = True
            
            discovery_success = False
            if processed_row.identity:
                if processed_row.identity.status in ["OFFICIAL_PRODUCT_PAGE_FOUND", "OFFICIAL_DOCUMENT_FOUND"]:
                    discovery_success = True
                if processed_row.identity.status == "NEEDS_REVIEW":
                    needs_review = True
                if processed_row.identity.status == "AI_QUOTA_EXCEEDED":
                    ai_quota_exceeded = True
                    ai_required = True

            if discovery_success and not ai_required:
                job.deterministic_rows += 1
            elif ai_required:
                job.ai_required_rows += 1
                
            if ai_success:
                job.ai_success_rows += 1
                
            if ai_quota_exceeded:
                job.ai_quota_limited_rows += 1
                
            if needs_review:
                job.needs_review_rows += 1

            # Commit every row so the UI sees progress
            db.commit()
            
            # Pace requests to avoid hitting 429 Gemini API limits
            # Only pace if AI was actually required for this row to speed up deterministic processing
            if ai_required:
                time.sleep(min_interval)
            
        job.status = "COMPLETED"
        db.commit()
        
    except Exception as e:
        if 'job' in locals() and job:
            job.status = "FAILED"
            db.commit()
        print(f"Background Job Error: {e}")
    finally:
        db.close()


@router.post("", response_model=JobResponse)
def create_job(db: Session = Depends(get_db)):
    job_id = str(uuid.uuid4())
    new_job = JobModel(
        id=job_id,
        status="CREATED",
        total_rows=0,
        processed_rows=0,
        failed_rows=0,
        errors=[]
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    return JobResponse(
        id=new_job.id,
        status=new_job.status,
        total_rows=new_job.total_rows,
        processed_rows=new_job.processed_rows,
        failed_rows=new_job.failed_rows,
        created_at=new_job.created_at.isoformat(),
        deterministic_rows=new_job.deterministic_rows,
        ai_required_rows=new_job.ai_required_rows,
        ai_success_rows=new_job.ai_success_rows,
        ai_quota_limited_rows=new_job.ai_quota_limited_rows,
        needs_review_rows=new_job.needs_review_rows,
        gemini_request_count=new_job.gemini_request_count
    )

@router.post("/{job_id}/upload", response_model=JobResponse)
async def upload_file(job_id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
    content = await file.read()
    content_str = content.decode("utf-8")
    
    rows, errors = parse_input_csv(content_str)
    
    # Save raw rows to DB
    for r in rows:
        db_row = JobRowModel(
            job_id=job_id,
            row_id=r.row_id,
            mfg_part_num=r.mfg_part_num,
            part_desc=r.part_desc,
            part_manuf=r.part_manuf,
            result_data=r.dict()
        )
        db.add(db_row)
        
    job.total_rows = len(rows)
    job.errors = errors
    db.commit()
    
    # Start processing in the background
    background_tasks.add_task(process_job_background, job_id)
    
    return JobResponse(
        id=job.id,
        status=job.status,
        total_rows=job.total_rows,
        processed_rows=job.processed_rows,
        failed_rows=job.failed_rows,
        created_at=job.created_at.isoformat(),
        deterministic_rows=job.deterministic_rows,
        ai_required_rows=job.ai_required_rows,
        ai_success_rows=job.ai_success_rows,
        ai_quota_limited_rows=job.ai_quota_limited_rows,
        needs_review_rows=job.needs_review_rows,
        gemini_request_count=job.gemini_request_count
    )

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return JobResponse(
        id=job.id,
        status=job.status,
        total_rows=job.total_rows,
        processed_rows=job.processed_rows,
        failed_rows=job.failed_rows,
        created_at=job.created_at.isoformat(),
        deterministic_rows=job.deterministic_rows,
        ai_required_rows=job.ai_required_rows,
        ai_success_rows=job.ai_success_rows,
        ai_quota_limited_rows=job.ai_quota_limited_rows,
        needs_review_rows=job.needs_review_rows,
        gemini_request_count=job.gemini_request_count
    )

@router.get("/{job_id}/results")
def get_job_results(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    db_rows = db.query(JobRowModel).filter(JobRowModel.job_id == job_id).order_by(JobRowModel.row_id).all()
    
    return {
        "rows": [r.result_data for r in db_rows],
        "errors": job.errors
    }

@router.get("/{job_id}/download/csv")
def download_csv(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    db_rows = db.query(JobRowModel).filter(JobRowModel.job_id == job_id).order_by(JobRowModel.row_id).all()
    rows = [ProductRow(**r.result_data) for r in db_rows]
    
    headers = load_expected_headers()
    mapped_rows = map_to_output(rows, headers)
    csv_content = export_to_csv(mapped_rows, headers)
    
    return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=job_{job_id}_output.csv"})

@router.get("/{job_id}/download/xlsx")
def download_xlsx(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    db_rows = db.query(JobRowModel).filter(JobRowModel.job_id == job_id).order_by(JobRowModel.row_id).all()
    rows = [ProductRow(**r.result_data) for r in db_rows]
    
    headers = load_expected_headers()
    mapped_rows = map_to_output(rows, headers)
    xlsx_content = export_to_xlsx(mapped_rows, headers)
    
    return Response(content=xlsx_content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename=job_{job_id}_output.xlsx"})
