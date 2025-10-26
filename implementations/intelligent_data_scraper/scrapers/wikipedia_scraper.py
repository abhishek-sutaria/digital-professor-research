import logging
import re
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from config import Config

logger = logging.getLogger(__name__)

class WikipediaScraper(BaseScraper):
    """Wikipedia scraper for biographical information"""
    
    def get_source_name(self) -> str:
        return "wikipedia"
    
    def search_person(self, name: str) -> List[Dict[str, Any]]:
        """Search for a person on Wikipedia"""
        candidates = []
        
        try:
            # Wikipedia search API
            search_url = f"https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': name,
                'srlimit': 10
            }
            
            response = self.make_request(search_url, params=params)
            if not response:
                return candidates
            
            data = response.json()
            search_results = data.get('query', {}).get('search', [])
            
            for result in search_results:
                # Extract basic info from search result
                candidate = {
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'size': result.get('size', 0),
                    'wordcount': result.get('wordcount', 0),
                    'pageid': result.get('pageid', ''),
                    'confidence_score': self._calculate_confidence(name, result)
                }
                candidates.append(candidate)
            
        except Exception as e:
            logger.error(f"Error searching Wikipedia for {name}: {e}")
        
        return candidates
    
    def _calculate_confidence(self, search_name: str, result: Dict) -> float:
        """Calculate confidence score for Wikipedia page match"""
        confidence = 0.0
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        search_name_lower = search_name.lower()
        
        # Title matching
        if search_name_lower in title:
            confidence += 0.4
        
        # Exact title match
        if title == search_name_lower:
            confidence += 0.3
        
        # Snippet contains name
        if search_name_lower in snippet:
            confidence += 0.2
        
        # Page size bonus (longer pages are usually more detailed)
        wordcount = result.get('wordcount', 0)
        if wordcount > 1000:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def scrape_person(self, person_info: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape detailed information from Wikipedia page"""
        pageid = person_info.get('pageid')
        title = person_info.get('title')
        
        if not pageid and not title:
            logger.warning("No pageid or title provided for Wikipedia scraping")
            return {}
        
        try:
            # Get page content
            if pageid:
                content_url = f"https://en.wikipedia.org/w/api.php"
                params = {
                    'action': 'query',
                    'format': 'json',
                    'pageids': pageid,
                    'prop': 'extracts|info|images',
                    'exintro': True,
                    'explaintext': True,
                    'inprop': 'url'
                }
            else:
                # Use title to get page
                content_url = f"https://en.wikipedia.org/w/api.php"
                params = {
                    'action': 'query',
                    'format': 'json',
                    'titles': title,
                    'prop': 'extracts|info|images',
                    'exintro': True,
                    'explaintext': True,
                    'inprop': 'url'
                }
            
            response = self.make_request(content_url, params=params)
            if not response:
                return {}
            
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            
            if not pages:
                return {}
            
            page_data = list(pages.values())[0]
            
            result = {
                'title': page_data.get('title', ''),
                'extract': page_data.get('extract', ''),
                'fullurl': page_data.get('fullurl', ''),
                'pageid': page_data.get('pageid', ''),
                'length': page_data.get('length', 0),
                'touched': page_data.get('touched', ''),
                'images': page_data.get('images', [])
            }
            
            # Extract structured information
            result['structured_info'] = self._extract_structured_info(result['extract'])
            
            return result
            
        except Exception as e:
            logger.error(f"Error scraping Wikipedia page for {title}: {e}")
            return {}
    
    def _extract_structured_info(self, text: str) -> Dict[str, Any]:
        """Extract structured information from Wikipedia text"""
        info = {
            'birth_date': None,
            'birth_place': None,
            'occupation': None,
            'education': None,
            'awards': [],
            'notable_works': [],
            'quotes': []
        }
        
        # Extract birth information
        birth_patterns = [
            r'born\s+([^,]+),\s*([^.]*)',
            r'born\s+on\s+([^,]+),\s*([^.]*)',
            r'born\s+([^.]*)'
        ]
        
        for pattern in birth_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    info['birth_date'] = match.group(1).strip()
                    info['birth_place'] = match.group(2).strip()
                else:
                    info['birth_date'] = match.group(1).strip()
                break
        
        # Extract occupation
        occupation_patterns = [
            r'is\s+(?:an?\s+)?([^.]*?)(?:,|\.|$)',
            r'was\s+(?:an?\s+)?([^.]*?)(?:,|\.|$)',
            r'known\s+for\s+([^.]*)'
        ]
        
        for pattern in occupation_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                occupation = match.group(1).strip()
                if len(occupation) > 10 and len(occupation) < 100:
                    info['occupation'] = occupation
                    break
        
        # Extract education
        education_patterns = [
            r'studied\s+at\s+([^.]*)',
            r'graduated\s+from\s+([^.]*)',
            r'earned\s+(?:a\s+)?([^.]*?)\s+from\s+([^.]*)',
            r'degree\s+from\s+([^.]*)'
        ]
        
        for pattern in education_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    info['education'] = f"{match.group(1)} from {match.group(2)}"
                else:
                    info['education'] = match.group(1).strip()
                break
        
        # Extract quotes (text in quotes)
        quote_pattern = r'"([^"]{20,200})"'
        quotes = re.findall(quote_pattern, text)
        info['quotes'] = quotes[:5]  # Limit to 5 quotes
        
        return info



