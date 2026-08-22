from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class JobCreate(BaseModel):
    pass

class JobResponse(BaseModel):
    id: str
    status: str
    total_rows: int
    processed_rows: int
    failed_rows: int
    created_at: datetime

class IdentityResult(BaseModel):
    resolved_manufacturer: str = ""
    resolved_brand: str = ""
    resolved_product_name: str = ""
    resolved_classpath: str = ""
    confidence: float = 0.0
    status: str = "FAILED"  # VERIFIED, NEEDS_REVIEW, CONFLICT, FAILED
    evidence_urls: List[str] = Field(default_factory=list)
    reasoning: str = ""

class ProductRow(BaseModel):
    mfg_part_num: Optional[str] = None
    part_desc: Optional[str] = None
    e1_brand: Optional[str] = None
    unilog_brand: Optional[str] = None
    dib_brand: Optional[str] = None
    part_manuf: Optional[str] = None
    
    # Internal tracking
    row_id: int
    is_valid: bool = True
    errors: List[str] = Field(default_factory=list)
    identity: Optional[IdentityResult] = None
