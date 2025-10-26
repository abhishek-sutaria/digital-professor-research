import logging
import re
from typing import Dict, List, Any, Optional
from scholarly import scholarly
from scrapers.base_scraper import BaseScraper
from config import Config

logger = logging.getLogger(__name__)

class GoogleScholarScraper(BaseScraper):
    """Google Scholar scraper for research papers, citations, and metrics"""
    
    def get_source_name(self) -> str:
        return "google_scholar"
    
    def search_person(self, name: str) -> List[Dict[str, Any]]:
        """Search for a person on Google Scholar"""
        candidates = []
        
        try:
            # Search for the person
            search_query = scholarly.search_author(name)
            
            for i, author in enumerate(search_query):
                if i >= 10:  # Limit to top 10 results
                    break
                
                # Extract author information
                author_info = {
                    'name': author.get('name', ''),
                    'affiliation': author.get('affiliation', ''),
                    'email': author.get('email', ''),
                    'interests': author.get('interests', []),
                    'citedby': author.get('citedby', 0),
                    'hindex': author.get('hindex', 0),
                    'i10index': author.get('i10index', 0),
                    'url_picture': author.get('url_picture', ''),
                    'scholar_id': author.get('scholar_id', ''),
                    'confidence_score': self._calculate_confidence(name, author)
                }
                
                candidates.append(author_info)
                
        except Exception as e:
            logger.error(f"Error searching Google Scholar for {name}: {e}")
        
        return candidates
    
    def _calculate_confidence(self, search_name: str, author_info: Dict) -> float:
        """Calculate confidence score for author match"""
        confidence = 0.0
        author_name = author_info.get('name', '').lower()
        search_name_lower = search_name.lower()
        
        # Name matching
        if search_name_lower in author_name:
            confidence += 0.4
        
        # Exact name match
        if author_name == search_name_lower:
            confidence += 0.3
        
        # Affiliation bonus
        if author_info.get('affiliation'):
            confidence += 0.1
        
        # Citation count bonus (more citations = more likely to be the right person)
        citedby = author_info.get('citedby', 0)
        if citedby > 1000:
            confidence += 0.2
        elif citedby > 100:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def scrape_person(self, person_info: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape detailed information about a person from Google Scholar"""
        scholar_id = person_info.get('scholar_id')
        if not scholar_id:
            logger.warning("No scholar_id provided for detailed scraping")
            return {}
        
        try:
            # Get detailed author information
            author = scholarly.fill(scholarly.search_author_id(scholar_id))
            
            result = {
                'basic_info': {
                    'name': author.get('name', ''),
                    'affiliation': author.get('affiliation', ''),
                    'email': author.get('email', ''),
                    'interests': author.get('interests', []),
                    'url_picture': author.get('url_picture', ''),
                    'scholar_id': scholar_id
                },
                'metrics': {
                    'citedby': author.get('citedby', 0),
                    'hindex': author.get('hindex', 0),
                    'i10index': author.get('i10index', 0),
                    'cites_per_year': author.get('cites_per_year', {})
                },
                'publications': [],
                'coauthors': []
            }
            
            # Get publications
            publications = author.get('publications', [])
            for pub in publications[:Config.MAX_PAPERS]:
                pub_info = self._extract_publication_info(pub)
                result['publications'].append(pub_info)
            
            # Get coauthors
            coauthors = author.get('coauthors', [])
            for coauthor in coauthors[:20]:  # Limit coauthors
                coauthor_info = {
                    'name': coauthor.get('name', ''),
                    'affiliation': coauthor.get('affiliation', ''),
                    'scholar_id': coauthor.get('scholar_id', '')
                }
                result['coauthors'].append(coauthor_info)
            
            return result
            
        except Exception as e:
            logger.error(f"Error scraping Google Scholar details for {scholar_id}: {e}")
            return {}
    
    def _extract_publication_info(self, pub: Dict) -> Dict[str, Any]:
        """Extract publication information"""
        return {
            'title': pub.get('bib', {}).get('title', ''),
            'authors': pub.get('bib', {}).get('author', ''),
            'year': pub.get('bib', {}).get('pub_year', ''),
            'venue': pub.get('bib', {}).get('venue', ''),
            'abstract': pub.get('bib', {}).get('abstract', ''),
            'citations': pub.get('num_citations', 0),
            'url': pub.get('pub_url', ''),
            'pdf_url': pub.get('eprint_url', ''),
            'doi': pub.get('bib', {}).get('doi', ''),
            'keywords': pub.get('bib', {}).get('keywords', ''),
            'publisher': pub.get('bib', {}).get('publisher', '')
        }
    
    def get_paper_content(self, paper_url: str) -> Optional[str]:
        """Attempt to get full paper content (if available)"""
        if not paper_url:
            return None
        
        try:
            response = self.make_request(paper_url)
            if response and response.status_code == 200:
                # This is a basic implementation - in practice, you'd need
                # to handle different paper formats and paywalls
                return response.text
        except Exception as e:
            logger.warning(f"Could not fetch paper content from {paper_url}: {e}")
        
        return None
    
    def search_papers_by_topic(self, topic: str, author_name: str = None) -> List[Dict]:
        """Search for papers by topic, optionally filtered by author"""
        papers = []
        
        try:
            search_query = scholarly.search_pubs(topic)
            
            for i, pub in enumerate(search_query):
                if i >= 50:  # Limit results
                    break
                
                # If author filter is specified, check if author is in the paper
                if author_name:
                    authors = pub.get('bib', {}).get('author', '').lower()
                    if author_name.lower() not in authors:
                        continue
                
                paper_info = self._extract_publication_info(pub)
                papers.append(paper_info)
                
        except Exception as e:
            logger.error(f"Error searching papers for topic {topic}: {e}")
        
        return papers



