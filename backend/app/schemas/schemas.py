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
    candidate_manufacturer: str = ""
    candidate_brand: str = ""
    candidate_product_name: str = ""
    candidate_classpath: str = ""
    mpn: str = ""
    official_source_url: str = ""
    matched_evidence_text: str = ""
    confidence: float = 0.0
    status: str = "FAILED"  # VERIFIED, NEEDS_REVIEW, CONFLICT, FAILED

class ExtractedFact(BaseModel):
    attribute: str
    raw_value: str
    evidence_text: str
    source_id: str
    source_url: str
    source_type: str  # HTML, PDF, MANUAL
    page_number: Optional[int] = None
    confidence: float

class ExtractionResult(BaseModel):
    facts: List[ExtractedFact] = Field(default_factory=list)
    status: str = "FAILED"
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
    retrieved_content: Optional[str] = None
    extraction: Optional[ExtractionResult] = None
