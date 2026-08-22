import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.schemas.schemas import IdentityResult

logger = logging.getLogger(__name__)

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
        if identity.status not in ["VERIFIED", "NEEDS_REVIEW"] or not identity.official_source_url:
            logger.info("Skipping retrieval: No valid official URL to fetch.")
            return None

        url = identity.official_source_url
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
                # Keep it simple: look for a hrefs ending in common doc extensions or containing keywords
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

                # --- Clean HTML for text extraction ---
                for script_or_style in soup(["script", "style", "noscript", "meta"]):
                    script_or_style.decompose()
                
                # Get text
                text = soup.get_text(separator="\n", strip=True)
                clean_text = "\n".join(line for line in text.splitlines() if line.strip())
                
                return RetrievedSource(url=url, content=clean_text, status_code=200, candidates=candidates)
            else:
                logger.warning(f"Failed to fetch {url}, status code: {response.status_code}")
                return RetrievedSource(url=url, content="", status_code=response.status_code)
                
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return RetrievedSource(url=url, content="", status_code=0)

retrieval_service = SourceRetrievalService()
