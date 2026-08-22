import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.schemas.schemas import IdentityResult

logger = logging.getLogger(__name__)

class RetrievedSource:
    def __init__(self, url: str, content: str, status_code: int):
        self.url = url
        self.content = content
        self.status_code = status_code
        self.success = status_code == 200 and bool(content)

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
                # Clean HTML
                soup = BeautifulSoup(response.text, "html.parser")
                # Remove scripts and styles
                for script_or_style in soup(["script", "style", "noscript", "meta"]):
                    script_or_style.decompose()
                
                # Get text
                text = soup.get_text(separator="\n", strip=True)
                
                # We could compress it further by removing multiple newlines
                clean_text = "\n".join(line for line in text.splitlines() if line.strip())
                
                return RetrievedSource(url=url, content=clean_text, status_code=200)
            else:
                logger.warning(f"Failed to fetch {url}, status code: {response.status_code}")
                return RetrievedSource(url=url, content="", status_code=response.status_code)
                
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return RetrievedSource(url=url, content="", status_code=0)

retrieval_service = SourceRetrievalService()
