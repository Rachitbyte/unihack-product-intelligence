import json
import logging
import os
import time
import urllib.parse
from typing import List, Dict, Any, Tuple
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from googlesearch import search as google_search

from app.schemas.schemas import ProductRow, IdentityResult
from app.services.reference_data import reference_db

logger = logging.getLogger(__name__)

DISTRIBUTORS = {
    "amazon", "ebay", "grainger", "mscdirect", "homedepot", "lowes",
    "zoro", "walmart", "target", "alibaba", "aliexpress", "wayfair",
    "fastenal", "mcmaster", "digikey", "mouser", "newark", "rs-online",
    "globalsources", "made-in-china", "homedepot.com", "lowes.com", "amazon.com"
}

GENERIC_PATHS = {"", "/", "/en", "/en/", "/home", "/index.html", "/default.aspx"}

# Tier 1 known domains
KNOWN_DOMAINS = {
    "freud inc (2435)": "freudtools.com",
    "freud": "freudtools.com",
    "diablo": "diablotools.com",
    "3m": "3m.com",
    "milwaukee": "milwaukeetool.com",
    "milwaukee accessory (4031)": "milwaukeetool.com",
    "milw": "milwaukeetool.com",
    "mirka": "mirka.com",
    "mirka abrasives inc (mirus)": "mirka.com"
}

class IdentityResolver:
    def __init__(self):
        self.max_retries = int(os.environ.get("SEARCH_MAX_RETRIES", "3"))

    def _is_distributor(self, url: str) -> bool:
        try:
            domain = urllib.parse.urlparse(url).netloc.lower()
            return any(dist in domain for dist in DISTRIBUTORS)
        except:
            return True
            
    def _domain_matches_manufacturer(self, url: str, manuf_name: str, brand_name: str, desc: str) -> Tuple[bool, bool]:
        if not manuf_name and not brand_name and not desc:
            return False, False
        try:
            domain = urllib.parse.urlparse(url).netloc.lower()
            
            # Check known domains
            manuf_lower = manuf_name.lower() if manuf_name else ""
            brand_lower = brand_name.lower() if brand_name else ""
            desc_lower = desc.lower() if desc else ""
            
            if manuf_lower in KNOWN_DOMAINS and KNOWN_DOMAINS[manuf_lower] in domain:
                return True, False
            if brand_lower in KNOWN_DOMAINS and KNOWN_DOMAINS[brand_lower] in domain:
                return True, False
                
            for k, v in KNOWN_DOMAINS.items():
                if v in domain and k in desc_lower:
                    return True, False
            
            manuf_clean = ''.join(e for e in manuf_lower if e.isalnum())
            brand_clean = ''.join(e for e in brand_lower if e.isalnum())
            
            # More forgiving: if domain contains the cleaned brand or manufacturer name
            if manuf_clean and manuf_clean in domain and len(manuf_clean) > 3:
                return True, False
            if brand_clean and brand_clean in domain and len(brand_clean) > 3:
                return True, False
                
            canonical_manuf = reference_db.normalize_manufacturer(manuf_name).lower()
            canon_clean = ''.join(e for e in canonical_manuf if e.isalnum())
            if canon_clean and canon_clean in domain and len(canon_clean) > 3:
                return True, False
                
            # Uncertain match: domain name is found in the description
            domain_main = domain.replace("www.", "").split(".")[0]
            if len(domain_main) > 3 and domain_main in desc_lower:
                return True, True
                
            return False, False
        except:
            return False, False

    def _resolve_true_manufacturer(self, row: ProductRow) -> str:
        manuf = row.part_manuf or ""
        brand = row.e1_brand or row.unilog_brand or row.dib_brand or ""
        desc = row.part_desc or ""
        mpn = row.mfg_part_num or ""
        
        if "--" in brand:
            brand = ""
            
        manuf_lower = manuf.lower()
        is_distrib = False
        
        if any(d in manuf_lower for d in DISTRIBUTORS):
            is_distrib = True
            
        distrib_keywords = ["supply", "industrial", "distributor", "wholesale", "fastener", "hardware", "packaging"]
        if any(k in manuf_lower for k in distrib_keywords):
            is_distrib = True
            
        candidate = manuf if not is_distrib else ""
        
        if candidate:
            return candidate if not brand else brand
            
        if brand:
            return brand
            
        words = desc.split()
        for word in words:
            if word.lower() == mpn.lower() or mpn.lower() in word.lower():
                continue
            if any(char.isdigit() for char in word) and word.lower() != "3m":
                continue
            clean_word = ''.join(e for e in word if e.isalnum())
            if len(clean_word) > 1:
                return clean_word
                
        return ""

    def _tier1_site_search(self, manuf: str, brand: str, desc: str, mpn: str) -> List[Dict[str, str]]:
        """Tier 1: Known manufacturer-domain discovery + flexible site search"""
        manuf_lower = manuf.lower() if manuf else ""
        brand_lower = brand.lower() if brand else ""
        desc_lower = desc.lower() if desc else ""
        
        possible_domains = []
        if manuf_lower in KNOWN_DOMAINS and KNOWN_DOMAINS[manuf_lower] not in possible_domains:
            possible_domains.append(KNOWN_DOMAINS[manuf_lower])
        if brand_lower in KNOWN_DOMAINS and KNOWN_DOMAINS[brand_lower] not in possible_domains:
            possible_domains.append(KNOWN_DOMAINS[brand_lower])
        for k, v in KNOWN_DOMAINS.items():
            if k in desc_lower and v not in possible_domains:
                possible_domains.append(v)
                
        if not possible_domains:
            return []
            
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        
        for domain in possible_domains:
            try:
                homepage_url = f"https://www.{domain}"
                
                # 1. URL Guessing
                common_paths = [f"/products/{mpn}", f"/product/{mpn}", f"/p/{mpn}", f"/{mpn}"]
                for path in common_paths:
                    guess_url = urllib.parse.urljoin(homepage_url, path)
                    try:
                        g_resp = requests.get(guess_url, timeout=10, headers=headers)
                        if g_resp.status_code == 200:
                            soup = BeautifulSoup(g_resp.text, 'html.parser')
                            title = soup.title.string if soup.title else mpn
                            
                            t_lower = title.lower()
                            if "search" in t_lower or "404" in t_lower or "not found" in t_lower or "error" in t_lower:
                                continue
                                
                            logger.info(f"Tier 1 URL Guessing succeeded: {guess_url}")
                            return [{
                                "url": guess_url,
                                "title": title,
                                "body": "Discovered via Tier 1 direct URL construction."
                            }]
                    except Exception as e:
                        logger.debug(f"Guess URL {guess_url} failed: {e}")
                
                # 2. Site Search Form Extraction
                resp = requests.get(homepage_url, timeout=10, headers=headers)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    forms = soup.find_all("form")
                    search_url = None
                    query_param = None
                    for form in forms:
                        action = form.get("action", "") or ""
                        inputs = form.find_all("input")
                        for inp in inputs:
                            type_ = inp.get("type", "").lower()
                            name = inp.get("name", "").lower()
                            if type_ in ["text", "search"] or "q" in name or "search" in name or "ntt" in name:
                                query_param = inp.get("name", "")
                                search_url = urllib.parse.urljoin(homepage_url, action)
                                break
                        if search_url and query_param:
                            break
                                
                    if search_url and query_param:
                        logger.info(f"Submitting Tier 1 search to {search_url} with {query_param}={mpn}")
                        s_resp = requests.get(search_url, params={query_param: mpn}, timeout=10, headers=headers)
                        if s_resp.status_code == 200:
                            s_soup = BeautifulSoup(s_resp.text, 'html.parser')
                            links = s_soup.find_all("a", href=True)
                            results = []
                            for link in links:
                                href = urllib.parse.urljoin(search_url, link.get("href"))
                                if mpn.lower() in href.lower() or mpn.lower() in link.get_text().lower():
                                    results.append({
                                        "url": href,
                                        "title": link.get_text(strip=True),
                                        "body": "Discovered via Tier 1 site search."
                                    })
                            if results:
                                return results
            except Exception as e:
                logger.warning(f"Tier 1 Site Search failed for {domain}: {e}")
            
        return []

    def _tier2_search(self, query: str) -> List[Dict[str, str]]:
        """Tier 2: External web search providers with bounded requests/retries"""
        results = []
        
        # 1. Primary: DuckDuckGo
        for attempt in range(self.max_retries):
            try:
                time.sleep(2.0 + attempt * 2) # Rate limit pacing
                with DDGS() as ddgs:
                    ddg_results = list(ddgs.text(query, max_results=5))
                    logger.info(f"DDG raw results: {ddg_results}")
                    if not ddg_results:
                        raise ValueError("Empty DDG results (likely rate limited)")
                    return [{"url": r.get("href"), "title": r.get("title", ""), "body": r.get("body", "")} for r in ddg_results if r.get("href")]
            except Exception as e:
                logger.warning(f"DDG Search failed attempt {attempt+1}: {e}")
                time.sleep(2 ** attempt) # Exponential backoff
                
        # 2. Fallback: Google Search
        for attempt in range(self.max_retries):
            try:
                time.sleep(2.0 + attempt * 2)
                g_results = list(google_search(query, num_results=5, sleep_interval=2.0))
                logger.info(f"Google raw results: {g_results}")
                if not g_results:
                    raise ValueError("Empty Google results (likely rate limited)")
                return [{"url": url, "title": "", "body": ""} for url in g_results]
            except Exception as e:
                logger.warning(f"Google Search failed attempt {attempt+1}: {e}")
                time.sleep(2 ** attempt)
                
        return []

    def _score_candidate(self, url: str, title: str, snippet: str, mpn: str) -> int:
        """Tier 3: Deterministic Candidate ranking"""
        score = 0
        try:
            parsed = urllib.parse.urlparse(url)
            path = parsed.path.lower()
            
            mpn_clean = ''.join(e for e in mpn.lower() if e.isalnum())
            path_clean = ''.join(e for e in path if e.isalnum())
            
            # Exact MPN in URL (very strong)
            if mpn_clean and mpn_clean in path_clean:
                score += 100
                
            # Product-specific PDF (strong)
            if path.endswith(".pdf"):
                score += 80
                
            # Exact MPN in page title/content/snippet (very strong)
            if mpn.lower() in title.lower() or mpn.lower() in snippet.lower():
                score += 80
                
            # Specific product identifier presence
            if "/product/" in path or "/p/" in path or "/item/" in path:
                score += 50
                
            # Generic homepage (reject/deprioritize)
            if parsed.path in GENERIC_PATHS:
                score -= 1000
                
        except Exception as e:
            logger.error(f"Error scoring candidate {url}: {e}")
            
        return score

    def resolve(self, row: ProductRow) -> IdentityResult:
        if not row.mfg_part_num:
            return IdentityResult(status="DISCOVERY_FAILED")

        mpn = row.mfg_part_num
        desc = row.part_desc or ""
        manuf = row.part_manuf or ""
        brand = row.e1_brand or row.unilog_brand or row.dib_brand or ""
        
        # Clean brand string if it matches placeholders
        if "--" in brand:
            brand = ""
            
        resolved_clue = self._resolve_true_manufacturer(row)
        logger.info(f"Resolved true manufacturer clue: '{resolved_clue}' from inputs.")
        
        result = IdentityResult(mpn=mpn)
        result.candidate_manufacturer = manuf
        result.candidate_brand = brand
        result.candidate_product_name = desc
        
        # --- TIER 1: Site Search ---
        search_results = self._tier1_site_search(resolved_clue, brand, desc, mpn)
        logger.info(f"Tier 1 results: {len(search_results)}")
        
        # --- TIER 2: External Search ---
        if not search_results:
            domain = KNOWN_DOMAINS.get(resolved_clue.lower())
            if domain:
                query_site = f'site:{domain} "{mpn}"'
                logger.info(f"Tier 2 query SITE: {query_site}")
                search_results = self._tier2_search(query_site)
                
        if not search_results:
            query = f'"{mpn}" "{resolved_clue}"'
            logger.info(f"Tier 2 query A: {query}")
            search_results = self._tier2_search(query)
            
        if not search_results:
            query_b = f'{mpn} {resolved_clue}'
            logger.info(f"Tier 2 query B: {query_b}")
            search_results = self._tier2_search(query_b)
            
        logger.info(f"Total search results: {len(search_results)}")
        
        if not search_results:
            result.status = "DISCOVERY_FAILED"
            return result
            
        # --- TIER 3: Ranking ---
        scored_candidates = []
        
        for sr in search_results:
            url = sr.get("url", "")
            title = sr.get("title", "")
            snippet = sr.get("body", "")
            
            if not url or not url.startswith("http"):
                continue
                
            # Reject Marketplaces/Distributors
            if self._is_distributor(url):
                logger.info(f"Rejected distributor: {url}")
                continue
                
            # Official manufacturer domain required
            is_match, is_uncertain = self._domain_matches_manufacturer(url, resolved_clue, brand, desc)
            if not is_match:
                logger.info(f"Rejected domain mismatch: {url}")
                continue
                
            score = self._score_candidate(url, title, snippet, mpn)
            logger.info(f"Candidate {url} scored {score} (uncertain: {is_uncertain})")
            scored_candidates.append({
                "url": url,
                "title": title,
                "snippet": snippet,
                "score": score,
                "is_uncertain": is_uncertain
            })
            
        if not scored_candidates:
            result.status = "DISCOVERY_FAILED"
            return result
            
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        best_candidate = scored_candidates[0]
        
        result.official_source_url = best_candidate["url"]
        result.matched_evidence_text = best_candidate["snippet"]
        
        # Status assignment
        if best_candidate["score"] < 0:
            # Generic homepage or really bad score
            result.status = "MANUFACTURER_FOUND_PRODUCT_NOT_FOUND"
            result.confidence = 0.3
            result.official_source_url = None
        elif 0 <= best_candidate["score"] < 50 or best_candidate.get("is_uncertain"):
            # Domain matched, but MPN wasn't really in URL or snippet, or domain match was uncertain
            result.status = "NEEDS_REVIEW"
            result.confidence = 0.5
        else:
            result.confidence = 0.95
            if best_candidate["url"].lower().endswith(".pdf"):
                result.status = "OFFICIAL_DOCUMENT_FOUND"
            else:
                result.status = "OFFICIAL_SOURCE_FOUND"
                
        return result

identity_resolver = IdentityResolver()
