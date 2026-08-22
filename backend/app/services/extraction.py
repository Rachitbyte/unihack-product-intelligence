import json
import logging
import os
import uuid
from typing import List, Dict, Any

from app.schemas.schemas import ProductRow, ExtractionResult, ExtractedFact

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

class ExtractionService:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model_name = os.environ.get("GEMINI_EXTRACTION_MODEL", "gemini-1.5-flash")
        
        if self.api_key and genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None

    def extract(self, row: ProductRow) -> ExtractionResult:
        if not self.model:
            logger.warning("GEMINI API not configured. Cannot perform AI extraction.")
            return ExtractionResult(status="FAILED", reasoning="API Key not configured")

        if not row.retrieved_content:
            return ExtractionResult(status="FAILED", reasoning="No source content available for extraction")

        mpn = row.mfg_part_num
        content = row.retrieved_content
        source_url = row.identity.official_source_url if row.identity else "Unknown"
        
        # Determine source type (HTML vs PDF based on URL extension, for now assume HTML)
        source_type = "PDF" if source_url.lower().endswith(".pdf") else "HTML"
        source_id = str(uuid.uuid4())[:8]

        prompt = f"""
You are an expert Product Spec Extractor.
Extract all relevant product specifications from the provided source text for the product with MPN: {mpn}.
Do NOT normalize the values yet. Do NOT invent information.
For every fact you extract, you MUST provide the exact snippet from the text that proves it.

Source Text:
{content[:15000]} # Truncated for safety

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
                    confidence=float(f.get("confidence", 0.0))
                )
                facts.append(fact)
                
            return ExtractionResult(
                facts=facts,
                status=data.get("status", "FAILED"),
                reasoning=data.get("reasoning", "")
            )
            
        except Exception as e:
            err_str = str(e)
            logger.error(f"Error extracting specs for MPN {mpn}: {err_str}")
            
            if "429" in err_str or "Quota Exceeded" in err_str:
                return ExtractionResult(status="FAILED", reasoning="429 API/Quota Failure")
                
            return ExtractionResult(status="FAILED", reasoning=f"AI Error: {err_str}")

extraction_service = ExtractionService()
