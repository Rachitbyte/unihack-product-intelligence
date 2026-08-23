import json
import logging
import os
import uuid
import hashlib
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from diskcache import Cache
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from app.schemas.schemas import ProductRow, ExtractionResult, ExtractedFact

try:
    import google.generativeai as genai
    from google.api_core.exceptions import ResourceExhausted
except ImportError:
    genai = None
    ResourceExhausted = Exception

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(os.path.dirname(__file__), "../../../cache/extraction")
os.makedirs(CACHE_DIR, exist_ok=True)
cache = Cache(CACHE_DIR)

class ExtractionService:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model_name = os.environ.get("GEMINI_EXTRACTION_MODEL", "gemini-3.5-flash-lite")
        self.max_retries = int(os.environ.get("GEMINI_MAX_RETRIES", "3"))
        
        if self.api_key and genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None
            
    def _deterministic_extract(self, html_content: str, source_id: str, source_url: str, source_type: str) -> List[ExtractedFact]:
        facts = []
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Simple heuristic: Look for tables
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all(["th", "td"])
                    if len(cells) == 2:
                        key = cells[0].get_text(strip=True)
                        val = cells[1].get_text(strip=True)
                        if key and val and len(key) < 50 and len(val) < 100:
                            # Avoid extracting huge blocks of text
                            facts.append(ExtractedFact(
                                attribute=key,
                                raw_value=val,
                                evidence_text=f"{key}: {val}",
                                source_id=source_id,
                                source_url=source_url,
                                source_type=source_type,
                                confidence=0.9
                            ))
                            
            # We could add JSON-LD parsing here as well
            # For brevity, returning table facts. If we found more than 3 facts, we consider it successful.
        except Exception as e:
            logger.error(f"Deterministic extraction error: {e}")
            
        return facts

    def extract(self, row: ProductRow) -> ExtractionResult:
        if not row.retrieved_content:
            return ExtractionResult(status="FAILED", reasoning="No source content available for extraction")

        mpn = row.mfg_part_num
        content = row.retrieved_content
        source_url = row.identity.official_source_url if row.identity else "Unknown"
        
        source_type = "PDF" if source_url.lower().endswith(".pdf") else "HTML"
        source_id = str(uuid.uuid4())[:8]
        
        # 1. Deterministic Extraction
        if source_type == "HTML":
            det_facts = self._deterministic_extract(content, source_id, source_url, source_type)
            if len(det_facts) >= 3:
                return ExtractionResult(facts=det_facts, status="SUCCESS", reasoning="Deterministic table extraction")
                
        # 2. Prepare text for AI Fallback
        if source_type == "HTML":
            soup = BeautifulSoup(content, "html.parser")
            for script in soup(["script", "style", "noscript", "meta"]):
                script.decompose()
            clean_text = " ".join(soup.get_text(separator=" ", strip=True).split())
        else:
            clean_text = content
            
        clean_text = clean_text[:15000] # Safe limit
        
        if not self.model:
            return ExtractionResult(facts=det_facts, status="PARTIAL" if det_facts else "FAILED", reasoning="No AI available, fallback to deterministic")

        # Check Cache
        content_hash = hashlib.md5(f"{mpn}_{clean_text[:1000]}".encode()).hexdigest()
        cached = cache.get(content_hash)
        if cached:
            logger.info("Cache hit for extraction")
            return ExtractionResult(**cached)
            
        prompt = f"""
You are an expert Product Spec Extractor.
Extract all relevant product specifications from the provided source text for the product with MPN: {mpn}.
Do NOT normalize the values yet. Do NOT invent information.
For every fact you extract, you MUST provide the exact snippet from the text that proves it.

Source Text:
{clean_text}

Respond STRICTLY in JSON format:
{{
  "status": "SUCCESS" or "PARTIAL",
  "reasoning": "Brief explanation",
  "facts": [
    {{
      "attribute": "e.g., Weight, Length, Material, Color, Voltage",
      "raw_value": "e.g., 5.5 lbs, 12 inches, Brass",
      "evidence_text": "Exact quote from text",
      "confidence": 0.0 to 1.0
    }}
  ]
}}
"""
        try:
            for attempt in range(self.max_retries):
                try:
                    response = self.model.generate_content(prompt)
                    text = response.text
                    
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0].strip()
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0].strip()
                        
                    data = json.loads(text)
                    
                    facts = []
                    for f in data.get("facts", []):
                        fact = ExtractedFact(
                            attribute=f.get("attribute", ""),
                            raw_value=f.get("raw_value", ""),
                            evidence_text=f.get("evidence_text", ""),
                            source_id=source_id,
                            source_url=source_url,
                            source_type=source_type,
                            confidence=float(f.get("confidence", 0.9))
                        )
                        facts.append(fact)
                        
                    res = ExtractionResult(
                        facts=facts,
                        status=data.get("status", "FAILED"),
                        reasoning=data.get("reasoning", "")
                    )
                    
                    cache.set(content_hash, res.dict(), expire=86400)
                    return res
                    
                except ResourceExhausted:
                    if attempt == self.max_retries - 1:
                        # Fallback to deterministic facts if quota exhausted
                        return ExtractionResult(facts=det_facts, status="AI_QUOTA_EXCEEDED", reasoning="Quota exhausted, partial deterministic facts returned")
                    import time
                    time.sleep(2 ** attempt)
                except Exception as e:
                    # JSON parse error, etc
                    if attempt == self.max_retries - 1:
                        return ExtractionResult(facts=det_facts, status="FAILED", reasoning=str(e))
                        
        except Exception as e:
            logger.error(f"Error extracting specs for MPN {mpn}: {e}")
            return ExtractionResult(facts=det_facts, status="FAILED", reasoning=str(e))
            
        return ExtractionResult(facts=det_facts, status="FAILED", reasoning="Unknown error")

extraction_service = ExtractionService()
