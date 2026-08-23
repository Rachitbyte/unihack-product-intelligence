import json
import logging
import os
import hashlib
from diskcache import Cache
from app.schemas.schemas import ProductRow, GeneratedContent
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

try:
    import google.generativeai as genai
    from google.api_core.exceptions import ResourceExhausted
except ImportError:
    genai = None
    ResourceExhausted = Exception

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(os.path.dirname(__file__), "../../../cache/content")
os.makedirs(CACHE_DIR, exist_ok=True)
cache = Cache(CACHE_DIR)

class ContentGenerationService:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model_name = os.environ.get("GEMINI_CONTENT_MODEL", "gemini-3.5-flash-lite")
        self.max_retries = int(os.environ.get("GEMINI_MAX_RETRIES", "3"))
        
        if self.api_key and genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None

    def generate(self, row: ProductRow) -> GeneratedContent:
        if not self.model:
            logger.warning("GEMINI API not configured. Cannot perform AI content generation.")
            return GeneratedContent()

        if not row.extraction or not row.extraction.facts:
            return GeneratedContent()

        # Strict Scope: ONLY use genuinely validated facts
        # DO NOT use NOT_VALIDATED_REFERENCE_DATA_MISSING facts
        validated_facts = [
            f for f in row.extraction.facts 
            if f.is_valid and f.validation_status == "VALIDATED"
        ]
        
        if not validated_facts:
            return GeneratedContent()

        facts_text = "\n".join([f"- {f.attribute}: {f.normalized_value}" for f in validated_facts])
        
        # Check Cache
        content_hash = hashlib.md5(f"{row.mfg_part_num}_{facts_text}".encode()).hexdigest()
        cached = cache.get(content_hash)
        if cached:
            logger.info("Cache hit for content generation")
            return GeneratedContent(**cached)

        prompt = f"""
You are an expert e-commerce copywriter.
Generate a marketing description, short description, and item features (bullet points) based STRICTLY on the following verified facts for the product {row.mfg_part_num}.

Verified Facts:
{facts_text}

CRITICAL CONSTRAINTS:
1. You MUST NOT invent, infer, or hallucinate any specifications, features, or benefits that are not explicitly supported by the verified facts provided above.
2. Do not add facts from your general knowledge.
3. The 'item_features' list must contain AT MOST 20 bullets.
4. Output strictly as JSON.

Respond STRICTLY in JSON format:
{{
  "marketing_description": "Engaging paragraph describing the product based ONLY on facts.",
  "short_description": "A concise 1-2 sentence description.",
  "item_features": [
    "Feature 1 based on facts",
    "Feature 2 based on facts"
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
                    
                    features = data.get("item_features", [])
                    # Backend enforcement: at most 20 features
                    if isinstance(features, list):
                        features = features[:20]
                    else:
                        features = []
                        
                    res = GeneratedContent(
                        marketing_description=data.get("marketing_description", ""),
                        short_description=data.get("short_description", ""),
                        item_features=features
                    )
                    
                    cache.set(content_hash, res.dict(), expire=86400)
                    return res
                    
                except ResourceExhausted:
                    if attempt == self.max_retries - 1:
                        logger.error("AI_QUOTA_EXCEEDED for content generation")
                        return GeneratedContent()
                    import time
                    time.sleep(2 ** attempt)
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        logger.error(f"Error parsing content generation for MPN {row.mfg_part_num}: {e}")
                        return GeneratedContent()
                        
        except Exception as e:
            err_str = str(e)
            logger.error(f"Error generating content for MPN {row.mfg_part_num}: {err_str}")
            return GeneratedContent()

content_generation_service = ContentGenerationService()
