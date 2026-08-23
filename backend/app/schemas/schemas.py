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
    
    # Tracking
    deterministic_rows: int = 0
    ai_required_rows: int = 0
    ai_success_rows: int = 0
    ai_quota_limited_rows: int = 0
    needs_review_rows: int = 0
    gemini_request_count: int = 0

class IdentityResult(BaseModel):
    candidate_manufacturer: str = ""
    candidate_brand: str = ""
    candidate_product_name: str = ""
    candidate_classpath: str = ""
    mpn: str = ""
    official_source_url: str = ""
    matched_evidence_text: str = ""
    confidence: float = 0.0
    status: str = "DISCOVERY_FAILED"  # OFFICIAL_PRODUCT_PAGE_FOUND, OFFICIAL_DOCUMENT_FOUND, MANUFACTURER_FOUND_PRODUCT_NOT_FOUND, DISCOVERY_FAILED, NEEDS_REVIEW

class ExtractedFact(BaseModel):
    attribute: str
    raw_value: str
    evidence_text: str
    source_id: str
    source_url: str
    source_type: str  # HTML, PDF, MANUAL
    page_number: Optional[int] = None
    confidence: float
    
    # Phase 6 tracking
    normalized_value: Optional[str] = None
    is_valid: bool = False
    validation_status: str = "PENDING" # PENDING, VALIDATED, NOT_VALIDATED_REFERENCE_DATA_MISSING, NEEDS_REVIEW
    validation_message: str = ""

class ExtractionResult(BaseModel):
    facts: List[ExtractedFact] = Field(default_factory=list)
    status: str = "FAILED"
    reasoning: str = ""

class AssetCandidate(BaseModel):
    url: str
    asset_type: str  # IMAGE, DOCUMENT, VIDEO
    filename: str = ""
    link_text: str = ""
    alt_text: str = ""
    source_page_url: str = ""
    content_type: str = ""

class DigitalAsset(BaseModel):
    asset_id: str
    product_id: str
    url: str
    asset_type: str
    classification: str
    source_id: str
    source_page_url: str
    official_domain_verified: bool = False
    confidence: float
    status: str = "NEEDS_REVIEW" # ACCEPTED, REJECTED_NON_OFFICIAL, NEEDS_REVIEW, FAILED

class GeneratedContent(BaseModel):
    marketing_description: str = ""
    short_description: str = ""
    item_features: List[str] = Field(default_factory=list)

class AssetResult(BaseModel):
    candidates: List[AssetCandidate] = Field(default_factory=list)
    assets: List[DigitalAsset] = Field(default_factory=list)

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
    content: Optional[GeneratedContent] = None
    asset_result: Optional[AssetResult] = None
