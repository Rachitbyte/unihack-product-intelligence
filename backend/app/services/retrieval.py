import logging
import requests
import os
from bs4 import BeautifulSoup
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from diskcache import Cache
from app.schemas.schemas import IdentityResult

logger = logging.getLogger(__name__)

# Use a local cache directory
CACHE_DIR = os.path.join(os.path.dirname(__file__), "../../../cache/retrieval")
os.makedirs(CACHE_DIR, exist_ok=True)
cache = Cache(CACHE_DIR)

class RetrievedSource:
    def __init__(self, url: str, content: str, status_code: int, candidates: list = None):
        self.url = url
        self.content = content
        self.status_code = status_code
        self.success = status_code == 200 and bool(content)
        self.candidates = candidates or []

class SourceRetrievalService:
    def __init__(self):
        # Configure requests session with retry logic
        self.session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

    def fetch_source(self, identity: IdentityResult) -> Optional[RetrievedSource]:
        if identity.status not in ["OFFICIAL_SOURCE_FOUND", "OFFICIAL_DOCUMENT_FOUND", "NEEDS_REVIEW", "OFFICIAL_SOURCE_BLOCKED"] or not identity.official_source_url:
            logger.info("Skipping retrieval: No valid official URL to fetch.")
            return None

        url = identity.official_source_url
        
        # Check Cache
        cached = cache.get(url)
        if cached:
            logger.info(f"Cache hit for {url}")
            # Reconstruct from cache dict
            from app.schemas.schemas import AssetCandidate
            candidates = [AssetCandidate(**c) for c in cached.get("candidates", [])]
            return RetrievedSource(
                url=url, 
                content=cached.get("content", ""), 
                status_code=cached.get("status_code", 200),
                candidates=candidates
            )
            
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # Parse HTML
                soup = BeautifulSoup(response.text, "html.parser")
                
                # --- Phase 8: Asset Extraction ---
                candidates = []
                
                from urllib.parse import urljoin
                from app.schemas.schemas import AssetCandidate
                
                # Extract Images
                for img in soup.find_all("img"):
                    src = img.get("src")
                    if src:
                        full_url = urljoin(url, src)
                        alt = img.get("alt", "").strip()
                        candidates.append(AssetCandidate(
                            url=full_url,
                            asset_type="IMAGE",
                            filename=full_url.split("/")[-1].split("?")[0],
                            alt_text=alt,
                            source_page_url=url
                        ))
                
                # Extract Document Links
                for a in soup.find_all("a", href=True):
                    href = a.get("href")
                    full_url = urljoin(url, href)
                    link_text = a.get_text(strip=True)
                    lower_href = href.lower()
                    
                    if lower_href.endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx")) or "sds" in lower_href or "manual" in lower_href:
                        candidates.append(AssetCandidate(
                            url=full_url,
                            asset_type="DOCUMENT",
                            filename=full_url.split("/")[-1].split("?")[0],
                            link_text=link_text,
                            source_page_url=url
                        ))

                # Get raw HTML for deterministic table parsing later
                raw_html = response.text
                
                # Write to Cache
                cache.set(url, {
                    "content": raw_html,
                    "status_code": 200,
                    "candidates": [c.model_dump() if hasattr(c, 'model_dump') else c.dict() for c in candidates]
                }, expire=86400) # Cache for 1 day
                
                return RetrievedSource(url=url, content=raw_html, status_code=200, candidates=candidates)
            else:
                logger.warning(f"Failed to fetch {url}, status code: {response.status_code}")
                identity.status = "OFFICIAL_SOURCE_BLOCKED"
                
                # Try Google Cache fallback
                try:
                    cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"
                    logger.info(f"Attempting Google Cache fallback: {cache_url}")
                    c_resp = self.session.get(cache_url, headers=self.headers, timeout=10)
                    if c_resp.status_code == 200:
                        return RetrievedSource(url=url, content=c_resp.text, status_code=200)
                except Exception as ce:
                    logger.warning(f"Google Cache fallback failed: {ce}")
                    
                # Ultimate Fallback: the search snippet
                evidence = identity.matched_evidence_text or ""
                fallback_html = f"<html><body><h1>{identity.candidate_product_name}</h1><p>Source Blocked. Available Evidence: {evidence}</p></body></html>"
                return RetrievedSource(url=url, content=fallback_html, status_code=response.status_code)
                
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            identity.status = "OFFICIAL_SOURCE_BLOCKED"
            
            # Try Google Cache fallback
            try:
                cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"
                logger.info(f"Attempting Google Cache fallback: {cache_url}")
                c_resp = self.session.get(cache_url, headers=self.headers, timeout=10)
                if c_resp.status_code == 200:
                    return RetrievedSource(url=url, content=c_resp.text, status_code=200)
            except Exception as ce:
                logger.warning(f"Google Cache fallback failed: {ce}")
                
            evidence = getattr(identity, "matched_evidence_text", "") or ""
            fallback_html = f"<html><body><h1>{identity.candidate_product_name}</h1><p>Source Blocked (Timeout). Available Evidence: {evidence}</p></body></html>"
            return RetrievedSource(url=url, content=fallback_html, status_code=0)

retrieval_service = SourceRetrievalService()
