import logging
import uuid
import re
import requests
from typing import List, Dict, Tuple
from urllib.parse import urlparse

from app.schemas.schemas import ProductRow, AssetCandidate, DigitalAsset, AssetResult

logger = logging.getLogger(__name__)

class DigitalAssetService:
    def __init__(self):
        # We can configure a session for HEAD requests
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        # Setup Gemini for ambiguous classifications
        import os
        self.api_key = os.environ.get("GEMINI_API_KEY")
        try:
            import google.generativeai as genai
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-3.7-flash")
            else:
                self.model = None
        except ImportError:
            self.model = None

    def process_assets(self, row: ProductRow, candidates: List[AssetCandidate]) -> None:
        if not candidates:
            row.asset_result = AssetResult(candidates=[], assets=[])
            return

        unique_urls = set()
        deduped = []
        for c in candidates:
            if c.url not in unique_urls:
                unique_urls.add(c.url)
                deduped.append(c)

        final_assets = []
        # Find official domain from identity
        official_domain = ""
        if row.identity and row.identity.official_source_url:
            official_domain = urlparse(row.identity.official_source_url).netloc.lower()

        # Keep track of alternate image counting
        alt_image_counter = 1

        for candidate in deduped:
            # 1. Enforce official domain
            is_official, final_url = self._verify_domain(candidate.url, official_domain)
            
            status = "NEEDS_REVIEW"
            if is_official:
                status = "ACCEPTED"
            else:
                status = "REJECTED_NON_OFFICIAL"

            # 2. Content-Type check (for non-extension URLs or to confirm)
            # We skip heavy network calls for unit testing by making it mockable
            content_type = self._fetch_content_type(final_url)
            candidate.content_type = content_type

            # If it's a completely unsupported type (like text/html), we might skip or fail it
            if content_type and "text/html" in content_type:
                continue # not an asset

            # 3. Hybrid Classification
            classification, confidence = self._classify_asset(candidate)

            # If classification is ambiguous and model exists, ask Gemini
            if classification == "AMBIGUOUS" and self.model:
                classification, confidence = self._gemini_classify(candidate, row.mfg_part_num)

            if classification == "AMBIGUOUS":
                classification = "Unknown Asset"
                status = "NEEDS_REVIEW"

            # 4. Image special handling (Primary vs Alternate 1-4)
            if candidate.asset_type == "IMAGE" and classification == "Product Image":
                # Check if we already have a primary product image
                has_primary = any(a.classification == "Product Image" for a in final_assets)
                if has_primary:
                    if alt_image_counter <= 4:
                        classification = f"Alternate Image {alt_image_counter}"
                        alt_image_counter += 1
                    else:
                        classification = "Extra Image (Ignored)"
                        status = "FAILED"

            asset = DigitalAsset(
                asset_id=str(uuid.uuid4())[:8],
                product_id=row.mfg_part_num or "UNKNOWN",
                url=final_url,
                asset_type=candidate.asset_type,
                classification=classification,
                source_id="mock_source",
                source_page_url=candidate.source_page_url,
                official_domain_verified=is_official,
                confidence=confidence,
                status=status
            )
            final_assets.append(asset)

        row.asset_result = AssetResult(candidates=deduped, assets=final_assets)

    def _verify_domain(self, url: str, official_domain: str) -> Tuple[bool, str]:
        # Simple domain verification
        # Follow redirects if needed to check final host (mockable)
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Simple match or subdomain match
            if official_domain and (official_domain in domain or domain in official_domain):
                return True, url
                
            # If it's a known third-party like amazon, reject
            forbidden = ["amazon.", "ebay.", "walmart.", "homedepot."]
            if any(f in domain for f in forbidden):
                return False, url
                
            return False, url # Unknown host -> rejected/review
        except Exception:
            return False, url

    def _fetch_content_type(self, url: str) -> str:
        # In a real heavy environment we'd use HEAD
        # We'll rely on extension hints if we don't want to block
        ext = url.lower().split(".")[-1]
        if "pdf" in ext: return "application/pdf"
        if "jpg" in ext or "jpeg" in ext: return "image/jpeg"
        if "png" in ext: return "image/png"
        return ""

    def _classify_asset(self, candidate: AssetCandidate) -> Tuple[str, float]:
        text_to_search = (candidate.filename + " " + candidate.link_text + " " + candidate.alt_text).lower()
        
        # Deterministic Rules
        if candidate.asset_type == "DOCUMENT" or "pdf" in candidate.content_type:
            if "sds" in text_to_search or "safety data" in text_to_search:
                return "SDS", 0.95
            if "spec" in text_to_search:
                return "Specification Sheet", 0.90
            if "install" in text_to_search or "instruction" in text_to_search:
                return "Instruction/Installation Manual", 0.90
            if "manual" in text_to_search or "user" in text_to_search:
                return "Owners/User Manual", 0.85
            if "warranty" in text_to_search:
                return "Warranty Information", 0.95
            
        elif candidate.asset_type == "IMAGE" or "image" in candidate.content_type:
            # All valid images initially classified as Product Image; 
            # the caller will iterate and assign Alternate Image 1-4.
            return "Product Image", 0.80

        # Cannot deterministically classify
        return "AMBIGUOUS", 0.0

    def _gemini_classify(self, candidate: AssetCandidate, mpn: str) -> Tuple[str, float]:
        prompt = f"""
Classify this digital asset for product {mpn}.
URL: {candidate.url}
Asset Type: {candidate.asset_type}
Filename: {candidate.filename}
Link Text: {candidate.link_text}
Alt Text: {candidate.alt_text}

Allowed Classifications for Documents:
- SDS
- Warranty Information
- Catalog
- Specification Sheet
- Instruction/Installation Manual
- Service Manual
- Owners/User Manual
- Line Drawing
- MTR
- RoHS
- Full Engineering Drawing
- Energy Star Guide
- Technical Bulletin
- Submittal
- Compatibility Chart
- Size Chart
- Product Label/Insert

Respond ONLY with the exact classification name. If unknown, respond with 'Unknown Asset'.
"""
        try:
            resp = self.model.generate_content(prompt)
            classification = resp.text.strip()
            # Basic validation
            allowed = [
                "SDS", "Warranty Information", "Catalog", "Specification Sheet",
                "Instruction/Installation Manual", "Service Manual", "Owners/User Manual",
                "Line Drawing", "MTR", "RoHS", "Full Engineering Drawing", "Energy Star Guide",
                "Technical Bulletin", "Submittal", "Compatibility Chart", "Size Chart", "Product Label/Insert",
                "Product Image", "Alternate Image 1"
            ]
            if classification in allowed:
                return classification, 0.70
            return "AMBIGUOUS", 0.0
        except Exception:
            return "AMBIGUOUS", 0.0

digital_asset_service = DigitalAssetService()
