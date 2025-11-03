"""
Person Searcher
Searches for person across sources and fetches their research papers
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import sys
import os

# Add parent paths for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from lib.scholar_client import ScholarClient
from scrapers.wikipedia_scraper import WikipediaScraper
from storage.cache_manager import CacheManager
from processors.publications_enricher import PublicationsEnricher

try:
    from scholarly import scholarly
    HAVE_SCHOLARLY = True
except Exception:
    HAVE_SCHOLARLY = False

logger = logging.getLogger(__name__)


@dataclass
class PaperMetadata:
    """Basic paper metadata - compatible with PaperDownloadManager"""
    title: str
    authors: str
    year: str
    venue: str
    citations: int
    doi: Optional[str] = None
    pdf_url: Optional[str] = None  # Kept for compatibility
    abstract: Optional[str] = None
    url: Optional[str] = None  # Kept for compatibility
    scholar_id: Optional[str] = None
    pub_url: Optional[str] = None  # Kept for compatibility
    # Add PaperDownloadManager-compatible fields
    author_position: int = -1  # 1 = first author, 2 = second, etc.
    urls: List[str] = None  # List of all URLs to try
    
    def __post_init__(self):
        """Set default for urls list"""
        if self.urls is None:
            self.urls = []


class PersonSearcher:
    """Search for person and fetch their papers"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.scholar_client = ScholarClient(rate_limit=1.0)
        self.wikipedia_scraper = WikipediaScraper(self.cache_manager)
        self.publications_enricher = PublicationsEnricher()
    
    def search_person(self, person_name: str = None, scholar_id: str = None, 
                     max_papers: int = 100) -> Tuple[Dict[str, Any], List[PaperMetadata]]:
        """
        Search for person and fetch their papers
        
        Args:
            person_name: Name of the person to search for (optional if scholar_id provided)
            scholar_id: Google Scholar ID (more reliable than name search)
            max_papers: Maximum number of papers to fetch
            
        Returns:
            Tuple of (person_info dict, papers list)
        """
        if not person_name and not scholar_id:
            raise ValueError("Must provide either person_name or scholar_id")
        
        # Determine search strategy
        if scholar_id:
            logger.info(f"Fetching papers using Scholar ID: {scholar_id}")
            return self._fetch_by_scholar_id(scholar_id, person_name, max_papers)
        else:
            logger.info(f"Searching for person: {person_name}")
            return self._fetch_by_name(person_name, max_papers)
    
    def _fetch_by_scholar_id(self, scholar_id: str, person_name: Optional[str], 
                            max_papers: int) -> Tuple[Dict[str, Any], List[PaperMetadata]]:
        """
        Fetch papers using Google Scholar ID with comprehensive URL extraction
        
        Args:
            scholar_id: Google Scholar user ID
            person_name: Optional name for Wikipedia lookup
            max_papers: Maximum papers to fetch
            
        Returns:
            Tuple of (person_info dict, papers list)
        """
        # Search Wikipedia if name provided
        wiki_info = {}
        if person_name:
            wiki_info = self._search_wikipedia(person_name)
        
        # Fetch papers using Scholar ID with enhanced extraction
        papers = []
        try:
            logger.info("Fetching papers from Google Scholar using ID...")
            
            if not HAVE_SCHOLARLY:
                raise RuntimeError("scholarly library is not installed")
            
            # Get author
            author = scholarly.search_author_id(scholar_id)
            time.sleep(1.0)
            
            # Fill author to get publications
            filled = scholarly.fill(author)
            author_name = filled.get('name') or 'Unknown'
            author_name_clean = author_name.lower().strip()
            
            logger.info(f"Found {len(filled.get('publications', []))} total publications for {author_name}")
            
            # Process publications with comprehensive URL extraction
            publications = filled.get('publications', [])
            
            # Sort by citations (descending) to ensure we get TOP papers by impact
            publications.sort(key=lambda p: p.get('num_citations', 0), reverse=True)
            logger.info(f"Sorted publications by citation count (highest first)")
            
            for i, pub in enumerate(publications[:max_papers]):
                try:
                    bib = pub.get('bib', {})
                    
                    # Try filling individual paper to get ALL available URLs
                    # This is critical for getting ResearchGate, arXiv, institution PDFs
                    try:
                        filled_pub = scholarly.fill(pub)
                        time.sleep(1.0)
                        pub = filled_pub  # Use filled publication
                        bib = pub.get('bib', {})
                    except Exception as fill_error:
                        logger.debug(f"Could not fill paper {i+1}: {fill_error}")
                    
                    # Extract ALL URLs from filled publication
                    urls = []
                    eprint_url = pub.get('eprint_url')
                    pub_url = pub.get('pub_url')
                    
                    if eprint_url:
                        urls.append(eprint_url)
                    if pub_url and pub_url != eprint_url:
                        urls.append(pub_url)
                    
                    # CRITICAL: Check epubs_src_bib_info for ResearchGate, CloudFront, etc.
                    if 'epubs_src_bib_info' in pub:
                        epubs = pub.get('epubs_src_bib_info', {})
                        if isinstance(epubs, dict):
                            for key, value in epubs.items():
                                if isinstance(value, dict) and value.get('link'):
                                    if value['link'] not in urls:
                                        urls.append(value['link'])
                    
                    # Check bib for any URL fields
                    bib_url = bib.get('url')
                    if bib_url and bib_url not in urls:
                        urls.append(bib_url)
                    
                    # Detect author position
                    authors_str = bib.get('author', '')
                    author_position = self._detect_author_position(authors_str, author_name, author_name_clean)
                    
                    # Handle authors - could be list or string
                    if isinstance(authors_str, list):
                        authors_str = ', '.join(authors_str)
                    
                    paper = PaperMetadata(
                        title=bib.get('title', ''),
                        authors=authors_str if authors_str else 'Unknown',
                        year=str(bib.get('pub_year', 'Unknown')),
                        venue=bib.get('venue', ''),
                        citations=pub.get('num_citations', 0),
                        doi=bib.get('doi', ''),
                        pdf_url=urls[0] if urls else None,  # First URL for compatibility
                        pub_url=pub_url,
                        url=urls[0] if urls else None,  # First URL for compatibility
                        abstract=bib.get('abstract', '')[:1000] if bib.get('abstract') else '',
                        scholar_id=None,
                        author_position=author_position,
                        urls=urls
                    )
                    
                    if paper.title:  # Only add if has title
                        papers.append(paper)
                        
                except Exception as e:
                    logger.warning(f"Error processing publication {i+1}: {e}")
                    continue
            
            # Update person_name if not provided
            if not person_name:
                person_name = author_name
                
        except Exception as e:
            logger.error(f"Error fetching papers with Scholar ID: {e}")
            logger.info("Scholar ID fetch failed, trying fallback methods...")
            # If Scholar ID fails, try fallback
            if person_name:
                papers = self._fetch_with_fallback(person_name, max_papers)
        
        # Combine person info
        person_info = {
            'name': person_name or 'Unknown',
            'scholar_id': scholar_id,
            'wikipedia': wiki_info,
            'total_papers_found': len(papers),
            'source': 'scholar_id'
        }
        
        logger.info(f"Found {len(papers)} papers using Scholar ID")
        return person_info, papers
    
    def _fetch_by_name(self, person_name: str, max_papers: int) -> Tuple[Dict[str, Any], List[PaperMetadata]]:
        """
        Fetch papers using person name (may be blocked by Google)
        
        Args:
            person_name: Name of the person
            max_papers: Maximum papers to fetch
            
        Returns:
            Tuple of (person_info dict, papers list)
        """
        # Search Wikipedia for basic info
        wiki_info = self._search_wikipedia(person_name)
        
        # Try Google Scholar first
        papers = self._fetch_scholar_papers(person_name, max_papers)
        
        # If Scholar failed (0 papers), try fallback
        if not papers:
            logger.warning("Google Scholar search returned 0 papers")
            logger.info("Attempting fallback to CrossRef/Semantic Scholar...")
            papers = self._fetch_with_fallback(person_name, max_papers)
        
        # Combine person info
        person_info = {
            'name': person_name,
            'wikipedia': wiki_info,
            'total_papers_found': len(papers),
            'source': 'scholar' if papers else 'fallback'
        }
        
        logger.info(f"Found {len(papers)} papers for {person_name}")
        return person_info, papers
    
    def _search_wikipedia(self, person_name: str) -> Dict[str, Any]:
        """Search Wikipedia for person"""
        try:
            logger.info("Searching Wikipedia...")
            candidates = self.wikipedia_scraper.search_person(person_name)
            
            if candidates:
                # Get top match
                top_match = candidates[0]
                logger.info(f"Found Wikipedia page: {top_match.get('title')}")
                return top_match
            else:
                logger.warning("No Wikipedia page found")
                return {}
                
        except Exception as e:
            logger.error(f"Error searching Wikipedia: {e}")
            return {}
    
    def _fetch_scholar_papers(self, person_name: str, max_papers: int) -> List[PaperMetadata]:
        """Fetch papers from Google Scholar"""
        papers = []
        
        try:
            logger.info("Fetching papers from Google Scholar...")
            
            # Use scholar_client to fetch papers
            author_name, pubs = self.scholar_client.fetch_top_pubs_by_name(person_name, top_n=max_papers)
            
            logger.info(f"Found {len(pubs)} publications for {author_name}")
            
            # Process publications
            for idx, pub in enumerate(pubs):
                try:
                    paper = self._parse_publication(pub, idx)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.debug(f"Error parsing publication {idx}: {e}")
                    continue
            
        except Exception as e:
            logger.warning(f"Error fetching papers from Google Scholar: {e}")
            logger.warning("This may be due to rate limiting or network issues")
            # Return empty list instead of raising - system can work with zero papers
        
        return papers
    
    def _fetch_with_fallback(self, person_name: str, max_papers: int) -> List[PaperMetadata]:
        """
        Fallback to CrossRef/Semantic Scholar when Google Scholar fails
        
        Args:
            person_name: Name of the person
            max_papers: Maximum papers to fetch
            
        Returns:
            List of PaperMetadata from alternative sources
        """
        papers = []
        
        try:
            logger.info("Using CrossRef/Semantic Scholar as fallback...")
            
            # Use publications enricher to fetch from alternative sources
            enriched_pubs = self.publications_enricher.enrich_by_author(
                person_name, 
                topic_hint='',  # No topic restriction
                max_results=max_papers
            )
            
            if enriched_pubs:
                logger.info(f"Found {len(enriched_pubs)} papers from fallback sources")
                
                # Sort by citations (descending) to ensure we get TOP papers by impact
                enriched_pubs.sort(key=lambda p: p.get('citations', 0), reverse=True)
                logger.info(f"Sorted fallback publications by citation count (highest first)")
                
                # Convert enriched publications to PaperMetadata format
                for idx, pub in enumerate(enriched_pubs[:max_papers]):
                    try:
                        paper = PaperMetadata(
                            title=pub.get('title', ''),
                            authors=pub.get('authors', 'Unknown'),
                            year=str(pub.get('year', 'Unknown')),
                            venue=pub.get('venue', ''),
                            citations=pub.get('citations', 0),
                            doi=pub.get('doi', ''),
                            pdf_url=pub.get('url', ''),
                            pub_url=pub.get('url', ''),
                            url=pub.get('url', ''),
                            abstract='',
                            scholar_id=None
                        )
                        papers.append(paper)
                    except Exception as e:
                        logger.debug(f"Error converting enriched pub {idx}: {e}")
                        continue
            else:
                logger.warning("No papers found from fallback sources")
                
        except Exception as e:
            logger.error(f"Fallback fetch failed: {e}")
        
        return papers
    
    def _detect_author_position(self, authors_str: str, author_name: str, author_name_clean: str) -> int:
        """
        Detect the author's position in the author list
        
        Args:
            authors_str: Comma-separated author names or list
            author_name: Full author name for matching
            author_name_clean: Lowercase version of author name
            
        Returns:
            Position (1 = first author, 2 = second, etc., -1 if not found)
        """
        if not authors_str:
            return -1
        
        # Convert to string if list
        if isinstance(authors_str, list):
            authors_str = ', '.join(authors_str)
        
        # Split by comma
        author_list = [a.strip() for a in authors_str.split(',')]
        
        # Try to find match
        for idx, author in enumerate(author_list, 1):
            author_lower = author.lower()
            # Check if any part of the name matches
            name_parts = author_name_clean.split()
            if any(part in author_lower for part in name_parts if len(part) > 2):
                return idx
        
        return -1
    
    def _parse_publication(self, pub: Dict, index: int) -> Optional[PaperMetadata]:
        """Parse a publication entry from Google Scholar"""
        try:
            title = pub.get('title', '').strip()
            
            if not title:
                return None
            
            authors = pub.get('authors', '')
            year = pub.get('year', '')
            venue = pub.get('venue', '')
            urls = pub.get('urls', [])
            
            # Handle authors - could be list or string
            if isinstance(authors, list):
                authors = ', '.join(authors)
            
            # Get first URL as pdf_url
            pdf_url = urls[0] if urls else None
            
            return PaperMetadata(
                title=title,
                authors=authors if authors else 'Unknown',
                year=str(year) if year else 'Unknown',
                venue=venue if venue else '',
                citations=pub.get('citations', 0),
                pdf_url=pdf_url,
                pub_url=pdf_url,
                url=pdf_url,
                abstract='',
                scholar_id=None,
                author_position=-1,  # Not detected in this simple parse
                urls=urls if urls else []
            )
            
        except Exception as e:
            logger.debug(f"Error parsing publication: {e}")
            return None

