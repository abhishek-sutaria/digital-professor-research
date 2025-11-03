import logging
import re
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from config import Config

logger = logging.getLogger(__name__)

class NewsScraper(BaseScraper):
    """News scraper for articles, interviews, and mentions"""
    
    def get_source_name(self) -> str:
        return "news"
    
    def search_person(self, name: str) -> List[Dict[str, Any]]:
        """Search for news articles about a person"""
        candidates = []
        
        # Search multiple news sources
        sources = [
            self._search_google_news,
            self._search_bing_news,
            self._search_newsapi
        ]
        
        for search_func in sources:
            try:
                results = search_func(name)
                candidates.extend(results)
            except Exception as e:
                logger.warning(f"News search failed for {name}: {e}")
        
        # Remove duplicates and sort by confidence
        unique_candidates = self._deduplicate_candidates(candidates)
        return sorted(unique_candidates, key=lambda x: x.get('confidence_score', 0), reverse=True)
    
    def _search_google_news(self, name: str) -> List[Dict]:
        """Search Google News"""
        candidates = []
        
        try:
            search_url = f"https://news.google.com/search?q={name}&hl=en&gl=US&ceid=US:en"
            response = self.make_request(search_url)
            
            if response:
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = soup.find_all('article', limit=20)
                
                for article in articles:
                    title_elem = article.find('h3')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text().strip()
                    link_elem = article.find('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    
                    # Extract source and time
                    source_elem = article.find('div', class_='vr1PYe')
                    source = source_elem.get_text().strip() if source_elem else ''
                    
                    time_elem = article.find('time')
                    published_time = time_elem.get('datetime', '') if time_elem else ''
                    
                    candidate = {
                        'title': title,
                        'url': url,
                        'source': source,
                        'published_time': published_time,
                        'confidence_score': self._calculate_confidence(name, title)
                    }
                    candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"Google News search failed: {e}")
        
        return candidates
    
    def _search_bing_news(self, name: str) -> List[Dict]:
        """Search Bing News"""
        candidates = []
        
        try:
            search_url = f"https://www.bing.com/news/search?q={name}&FORM=HDRSC6"
            response = self.make_request(search_url)
            
            if response:
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = soup.find_all('div', class_='news-card', limit=20)
                
                for article in articles:
                    title_elem = article.find('a', class_='title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text().strip()
                    url = title_elem.get('href', '')
                    
                    source_elem = article.find('span', class_='source')
                    source = source_elem.get_text().strip() if source_elem else ''
                    
                    time_elem = article.find('span', class_='time')
                    published_time = time_elem.get_text().strip() if time_elem else ''
                    
                    candidate = {
                        'title': title,
                        'url': url,
                        'source': source,
                        'published_time': published_time,
                        'confidence_score': self._calculate_confidence(name, title)
                    }
                    candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"Bing News search failed: {e}")
        
        return candidates
    
    def _search_newsapi(self, name: str) -> List[Dict]:
        """Search using NewsAPI (if API key available)"""
        # This would require NewsAPI key
        # For now, return empty list
        return []
    
    def _calculate_confidence(self, search_name: str, title: str) -> float:
        """Calculate confidence score for news article"""
        confidence = 0.0
        title_lower = title.lower()
        search_name_lower = search_name.lower()
        
        # Name in title
        if search_name_lower in title_lower:
            confidence += 0.6
        
        # Exact name match
        if search_name_lower == title_lower:
            confidence += 0.4
        
        # Interview or profile keywords
        interview_keywords = ['interview', 'profile', 'exclusive', 'speaks', 'talks']
        for keyword in interview_keywords:
            if keyword in title_lower:
                confidence += 0.1
                break
        
        return min(confidence, 1.0)
    
    def _deduplicate_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """Remove duplicate candidates based on URL"""
        seen_urls = set()
        unique_candidates = []
        
        for candidate in candidates:
            url = candidate.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_candidates.append(candidate)
        
        return unique_candidates
    
    def scrape_person(self, person_info: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape detailed information from news articles"""
        articles = []
        
        # Get top articles from search results
        search_results = person_info.get('search_results', [])
        
        for result in search_results[:Config.MAX_ARTICLES]:
            try:
                article_content = self._scrape_article_content(result.get('url', ''))
                if article_content:
                    article_info = {
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'source': result.get('source', ''),
                        'published_time': result.get('published_time', ''),
                        'content': article_content,
                        'confidence_score': result.get('confidence_score', 0)
                    }
                    articles.append(article_info)
            
            except Exception as e:
                logger.warning(f"Failed to scrape article {result.get('url', '')}: {e}")
        
        return {
            'articles': articles,
            'total_articles': len(articles),
            'sources': list(set([article['source'] for article in articles if article['source']]))
        }
    
    def _scrape_article_content(self, url: str) -> Optional[str]:
        """Scrape content from a news article URL"""
        if not url:
            return None
        
        try:
            response = self.make_request(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find main content
            content_selectors = [
                'article',
                '.article-content',
                '.post-content',
                '.entry-content',
                '.content',
                'main',
                '.main-content'
            ]
            
            content = None
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text()
                    break
            
            if not content:
                # Fallback to body text
                body = soup.find('body')
                if body:
                    content = body.get_text()
            
            if content:
                # Clean up content
                content = self.clean_text(content)
                # Limit content length
                if len(content) > Config.MAX_CONTENT_LENGTH:
                    content = content[:Config.MAX_CONTENT_LENGTH] + "..."
                
                return content
        
        except Exception as e:
            logger.warning(f"Error scraping article content from {url}: {e}")
        
        return None



