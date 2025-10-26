import requests
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
from ratelimit import limits, sleep_and_retry
from config import Config

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Base class for all scrapers with common functionality"""
    
    def __init__(self, cache_manager=None):
        self.cache_manager = cache_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': Config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
    @sleep_and_retry
    @limits(calls=Config.REQUESTS_PER_MINUTE, period=60)
    def make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make a rate-limited HTTP request with retry logic"""
        for attempt in range(Config.MAX_RETRIES):
            try:
                response = self.session.get(
                    url, 
                    timeout=Config.REQUEST_TIMEOUT,
                    **kwargs
                )
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed for {url}: {e}")
                if attempt < Config.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All attempts failed for {url}")
                    return None
        
        return None
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and accessible"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def normalize_url(self, url: str, base_url: str = None) -> str:
        """Normalize URL"""
        if base_url:
            return urljoin(base_url, url)
        return url
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        return urlparse(url).netloc
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common HTML entities
        replacements = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&nbsp;': ' ',
        }
        
        for entity, char in replacements.items():
            text = text.replace(entity, char)
        
        return text.strip()
    
    def extract_metadata(self, response: requests.Response, url: str) -> Dict[str, Any]:
        """Extract metadata from HTTP response"""
        return {
            'url': url,
            'status_code': response.status_code,
            'content_type': response.headers.get('content-type', ''),
            'content_length': len(response.content),
            'scraped_at': time.time(),
            'domain': self.extract_domain(url)
        }
    
    def should_cache(self, data_type: str, content: str) -> bool:
        """Determine if content should be cached"""
        if not content or len(content.strip()) < 50:
            return False
        
        # Don't cache very large content
        if len(content) > Config.MAX_CONTENT_LENGTH:
            return False
        
        return True
    
    def store_data(self, person_id: int, source: str, data_type: str, 
                  content: str, metadata: Dict = None, url: str = None):
        """Store scraped data in cache"""
        if self.cache_manager and self.should_cache(data_type, content):
            self.cache_manager.store_scraped_data(
                person_id, source, data_type, content, metadata, url
            )
    
    def get_cached_data(self, person_id: int, source: str, data_type: str) -> List[Dict]:
        """Get cached data"""
        if self.cache_manager:
            return self.cache_manager.get_scraped_data(person_id, source, data_type)
        return []
    
    @abstractmethod
    def search_person(self, name: str) -> List[Dict[str, Any]]:
        """Search for a person and return potential matches"""
        pass
    
    @abstractmethod
    def scrape_person(self, person_info: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape detailed information about a person"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Return the name of this scraper source"""
        pass



