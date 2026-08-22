import json
import logging
import os
import urllib.parse
from typing import List, Dict, Any

from app.schemas.schemas import ProductRow, IdentityResult
from app.services.reference_data import reference_db

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

DISTRIBUTORS = {
    "amazon", "ebay", "grainger", "mscdirect", "homedepot", "lowes",
    "zoro", "walmart", "target", "alibaba", "aliexpress", "wayfair",
    "fastenal", "mcmaster", "digikey", "mouser", "newark", "rs-online"
}

class IdentityResolver:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model_name = os.environ.get("GEMINI_IDENTITY_MODEL", "gemini-1.5-flash")
        
        if self.api_key and genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name, tools='google_search_retrieval')
        else:
            self.model = None

    def _is_distributor(self, url: str) -> bool:
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            for dist in DISTRIBUTORS:
                if dist in domain:
                    return True
            return False
        except:
            return True

    def resolve(self, row: ProductRow) -> IdentityResult:
        if not self.model:
            logger.warning("GEMINI API not configured. Cannot perform AI search.")
            return IdentityResult(status="FAILED", mpn=row.mfg_part_num or "")

        if not row.mfg_part_num:
            return IdentityResult(status="FAILED")

        # Gather signals
        mpn = row.mfg_part_num
        desc = row.part_desc or ""
        
        clues = [row.part_manuf, row.e1_brand, row.unilog_brand, row.dib_brand]
        valid_clues = [c for c in clues if c]
        
        # Formulate Prompt - Only asking for Candidates
        prompt = f"""
You are an expert Product Intelligence Engine.
Your task is to find candidate sources for a product using Google Search.
MPN (Primary Signal): {mpn}
Description (Supporting): {desc}
Other Brand/Manuf Clues: {', '.join(valid_clues)}

Search for the product and find candidate URLs.
Do NOT attempt to verify the identity yourself. Just extract what you find.

Respond STRICTLY in JSON format with exactly these fields:
{{
  "candidate_manufacturer": "Manufacturer name if found",
  "candidate_brand": "Brand name if found",
  "candidate_product_name": "Product title from search",
  "candidate_classpath": "Category if found",
  "urls": [
    {{
      "url": "https://...",
      "snippet": "Snippet of text from the search result containing the MPN if possible",
      "has_mpn": true/false (whether the MPN is explicitly visible in the snippet or URL)
    }}
  ]
}}
"""
        
        result = IdentityResult(mpn=mpn)
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            data = json.loads(text)
            
            result.candidate_manufacturer = data.get("candidate_manufacturer", "")
            result.candidate_brand = data.get("candidate_brand", "")
            result.candidate_product_name = data.get("candidate_product_name", "")
            result.candidate_classpath = data.get("candidate_classpath", "")
            
            urls = data.get("urls", [])
            
            # Deterministic Backend Verification
            verified_url = None
            best_evidence = ""
            best_confidence = 0.0
            
            for u in urls:
                url_str = u.get("url", "")
                snippet = u.get("snippet", "")
                has_mpn = u.get("has_mpn", False)
                
                # Check 1: HTTPS
                if not url_str.startswith("https://"):
                    continue
                    
                # Check 2: Distributor/Marketplace
                if self._is_distributor(url_str):
                    continue
                    
                # Check 3: MPN presence
                # (Since this is phase 3 search, we rely on the snippet/URL for MPN presence)
                mpn_in_url = mpn.lower() in url_str.lower()
                mpn_in_snippet = mpn.lower() in snippet.lower()
                
                if has_mpn or mpn_in_url or mpn_in_snippet:
                    # We have a non-distributor HTTPS link with the MPN
                    verified_url = url_str
                    best_evidence = snippet
                    # Higher confidence if MPN is strictly in the URL structure or explicit text
                    best_confidence = 0.9 if mpn_in_url else 0.8
                    break
            
            if verified_url:
                result.official_source_url = verified_url
                result.matched_evidence_text = best_evidence
                result.confidence = best_confidence
                result.status = "VERIFIED"
            else:
                # Fallback to NEEDS_REVIEW if we only found distributors or unverified links
                if urls:
                    result.official_source_url = urls[0].get("url", "")
                    result.matched_evidence_text = urls[0].get("snippet", "")
                    result.confidence = 0.4
                    result.status = "NEEDS_REVIEW"
                else:
                    result.status = "FAILED"
            
            return result
            
        except Exception as e:
            logger.error(f"Error resolving identity for MPN {mpn}: {e}")
            result.status = "FAILED"
            return result

identity_resolver = IdentityResolver()
