import json
import logging
import google.generativeai as genai
from typing import List, Dict, Any
from app.schemas.schemas import ProductRow, IdentityResult
from app.services.reference_data import reference_db
import os

logger = logging.getLogger(__name__)

# Configure API Key if available
# We expect this to be set in the environment or .env file
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class IdentityResolver:
    def __init__(self):
        # We use a Gemini model with tools enabled
        # In this environment, we might use a standard model
        # Using gemini-1.5-flash since 3.7 might not be standardly named yet in the SDK
        self.model = genai.GenerativeModel('gemini-1.5-flash', tools='google_search_retrieval')

    def resolve(self, row: ProductRow) -> IdentityResult:
        if not GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set. Cannot perform AI search.")
            return IdentityResult(status="FAILED", reasoning="API Key not configured")

        if not row.mfg_part_num:
            return IdentityResult(status="FAILED", reasoning="No MPN provided, which is the primary signal.")

        # 1. Gather signals
        mpn = row.mfg_part_num
        desc = row.part_desc or ""
        
        # Build candidate manufacturers from clues
        clues = [row.part_manuf, row.e1_brand, row.unilog_brand, row.dib_brand]
        valid_clues = [c for c in clues if c]
        
        # Normalize the primary clue if possible
        normalized_manuf = ""
        if row.part_manuf:
            normalized_manuf = reference_db.normalize_manufacturer(row.part_manuf)
            
        # 2. Formulate Prompt
        prompt = f"""
You are an expert Product Intelligence Engine.
Your task is to resolve the official identity and manufacturer of a product based on the following clues.
MPN (Primary Signal): {mpn}
Description (Supporting): {desc}
Other Brand/Manuf Clues: {', '.join(valid_clues)}

Use the Google Search tool to find the OFFICIAL manufacturer page or a highly trusted industrial distributor page for this exact MPN.
You must NOT guess or hallucinate.

Respond STRICTLY in JSON format with exactly these fields:
{{
  "resolved_manufacturer": "Official manufacturer name",
  "resolved_brand": "Brand name if applicable, else empty",
  "resolved_product_name": "Clean product name/title",
  "resolved_classpath": "Category or class if apparent, else empty",
  "confidence": 0.0 to 1.0 (float),
  "status": "VERIFIED" (if found official site), "NEEDS_REVIEW" (if found distributor but not official), "CONFLICT" (if ambiguous), or "FAILED",
  "evidence_urls": ["URL1", "URL2"],
  "reasoning": "Brief explanation of how you determined the identity and confidence"
}}
"""
        
        # 3. Call AI
        try:
            response = self.model.generate_content(prompt)
            
            # 4. Parse Response
            text = response.text
            # Extract JSON block
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            data = json.loads(text)
            
            # Clean up and structure
            res = IdentityResult(
                resolved_manufacturer=data.get("resolved_manufacturer", ""),
                resolved_brand=data.get("resolved_brand", ""),
                resolved_product_name=data.get("resolved_product_name", ""),
                resolved_classpath=data.get("resolved_classpath", ""),
                confidence=float(data.get("confidence", 0.0)),
                status=data.get("status", "FAILED"),
                evidence_urls=data.get("evidence_urls", []),
                reasoning=data.get("reasoning", "")
            )
            return res
            
        except Exception as e:
            logger.error(f"Error resolving identity for MPN {mpn}: {e}")
            return IdentityResult(status="FAILED", reasoning=f"AI Error: {str(e)}")

identity_resolver = IdentityResolver()
