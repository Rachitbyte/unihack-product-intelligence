from sqlalchemy import Column, String, Integer, DateTime, JSON, Boolean, ForeignKey
from .database import Base
import datetime

class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, default="CREATED")
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Tracking fields
    deterministic_rows = Column(Integer, default=0)
    ai_required_rows = Column(Integer, default=0)
    ai_success_rows = Column(Integer, default=0)
    ai_quota_limited_rows = Column(Integer, default=0)
    needs_review_rows = Column(Integer, default=0)
    gemini_request_count = Column(Integer, default=0)
    
    # We will store errors as a JSON list of strings
    errors = Column(JSON, default=[])

class JobRowModel(Base):
    __tablename__ = "job_rows"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    row_id = Column(Integer)
    mfg_part_num = Column(String)
    part_desc = Column(String)
    part_manuf = Column(String)
    
    # Store the complete parsed and processed JSON schema representing ProductRow
    result_data = Column(JSON, default={})
