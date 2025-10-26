import logging
import os
import zipfile
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
from scrapers.base_scraper import BaseScraper
from config import Config

logger = logging.getLogger(__name__)

class PaperDownloader:
    """Research paper downloader with ZIP file creation"""
    
    def __init__(self, cache_manager=None):
        self.cache_manager = cache_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': Config.USER_AGENT,
            'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    def download_papers(self, papers: List[Dict[str, Any]], person_name: str, output_dir: str) -> str:
        """Download research papers and create ZIP file"""
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Create ZIP file path
        zip_filename = f"{person_name.replace(' ', '_')}_papers.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        
        downloaded_papers = []
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, paper in enumerate(papers):
                try:
                    paper_info = self._download_single_paper(paper, i + 1)
                    if paper_info:
                        downloaded_papers.append(paper_info)
                        
                        # Add to ZIP file
                        if paper_info['content']:
                            filename = f"{i+1:02d}_{paper_info['safe_title']}.pdf"
                            zip_file.writestr(filename, paper_info['content'])
                        
                        # Add metadata file
                        metadata_filename = f"{i+1:02d}_{paper_info['safe_title']}_metadata.txt"
                        metadata_content = self._create_metadata_content(paper_info)
                        zip_file.writestr(metadata_filename, metadata_content)
                
                except Exception as e:
                    logger.warning(f"Failed to download paper {i+1}: {e}")
                    continue
        
        logger.info(f"Downloaded {len(downloaded_papers)} papers to {zip_path}")
        return zip_path
    
    def _download_single_paper(self, paper: Dict[str, Any], paper_number: int) -> Optional[Dict[str, Any]]:
        """Download a single research paper"""
        
        paper_info = {
            'title': paper.get('title', f'Paper {paper_number}'),
            'authors': paper.get('authors', ''),
            'year': paper.get('year', ''),
            'venue': paper.get('venue', ''),
            'abstract': paper.get('abstract', ''),
            'url': paper.get('url', ''),
            'pdf_url': paper.get('pdf_url', ''),
            'doi': paper.get('doi', ''),
            'citations': paper.get('citations', 0),
            'content': None,
            'download_status': 'failed'
        }
        
        # Create safe filename
        safe_title = self._create_safe_filename(paper_info['title'])
        paper_info['safe_title'] = safe_title
        
        # Try to download PDF
        # Build list of candidate URLs (flatten)
        pdf_urls = []
        for u in [paper_info.get('pdf_url'), paper_info.get('url')]:
            if u:
                pdf_urls.append(u)
        pdf_urls.extend(self._generate_pdf_urls(paper_info))
        
        for url in pdf_urls:
            if not url:
                continue
            
            try:
                content = self._download_pdf_content(url)
                if content:
                    paper_info['content'] = content
                    paper_info['download_status'] = 'success'
                    paper_info['download_url'] = url
                    break
            
            except Exception as e:
                logger.warning(f"Failed to download from {url}: {e}")
                continue
        
        # If PDF download failed, try to get abstract/content
        if not paper_info['content'] and paper_info['abstract']:
            paper_info['content'] = self._create_text_content(paper_info)
            paper_info['download_status'] = 'abstract_only'
        
        return paper_info
    
    def _download_pdf_content(self, url: str) -> Optional[bytes]:
        """Download PDF content from URL"""
        try:
            response = self.session.get(url, timeout=30, stream=True, allow_redirects=True)
            response.raise_for_status()
            
            # Check if it's actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                return None
            
            # Download content
            content = response.content
            
            # Basic PDF validation
            if content.startswith(b'%PDF'):
                return content
            
            return None
        
        except Exception as e:
            logger.warning(f"Error downloading PDF from {url}: {e}")
            return None
    
    def _generate_pdf_urls(self, paper_info: Dict[str, Any]) -> List[str]:
        """Generate potential PDF URLs for a paper"""
        urls = []
        
        # Try common PDF hosting patterns
        title = paper_info.get('title', '')
        authors = paper_info.get('authors', '')
        doi = paper_info.get('doi', '')
        
        # arXiv URL
        if 'arxiv' in paper_info.get('url', '').lower():
            arxiv_id = self._extract_arxiv_id(paper_info['url'])
            if arxiv_id:
                urls.append(f"https://arxiv.org/pdf/{arxiv_id}.pdf")
        
        # ResearchGate URL
        if 'researchgate' in paper_info.get('url', '').lower():
            urls.append(paper_info['url'] + '/download')
        
        # Academia.edu URL
        if 'academia.edu' in paper_info.get('url', '').lower():
            urls.append(paper_info['url'].replace('/document/', '/download/'))
        
        # DOI-based URL
        if doi:
            urls.append(f"https://doi.org/{doi}")
        
        return urls
    
    def _extract_arxiv_id(self, url: str) -> Optional[str]:
        """Extract arXiv ID from URL"""
        import re
        pattern = r'arxiv\.org/(?:abs|pdf)/(\d+\.\d+(?:v\d+)?)'
        match = re.search(pattern, url)
        return match.group(1) if match else None
    
    def _create_safe_filename(self, title: str) -> str:
        """Create safe filename from title"""
        import re
        
        # Remove special characters
        safe_title = re.sub(r'[^\w\s-]', '', title)
        
        # Replace spaces with underscores
        safe_title = re.sub(r'\s+', '_', safe_title)
        
        # Limit length
        safe_title = safe_title[:50]
        
        return safe_title
    
    def _create_metadata_content(self, paper_info: Dict[str, Any]) -> str:
        """Create metadata content for a paper"""
        metadata = f"""Title: {paper_info['title']}
Authors: {paper_info['authors']}
Year: {paper_info['year']}
Venue: {paper_info['venue']}
DOI: {paper_info['doi']}
Citations: {paper_info['citations']}
Download Status: {paper_info['download_status']}
Download URL: {paper_info.get('download_url', 'N/A')}

Abstract:
{paper_info['abstract']}

---
Downloaded by Person Information Scraper
Generated on: {self._get_current_timestamp()}
"""
        return metadata
    
    def _create_text_content(self, paper_info: Dict[str, Any]) -> bytes:
        """Create text content when PDF is not available"""
        content = f"""Title: {paper_info['title']}
Authors: {paper_info['authors']}
Year: {paper_info['year']}
Venue: {paper_info['venue']}
DOI: {paper_info['doi']}
Citations: {paper_info['citations']}

Abstract:
{paper_info['abstract']}

Note: Full PDF was not available for download. This file contains the abstract and metadata only.
"""
        return content.encode('utf-8')
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_paper_sources(self, papers: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Get paper sources and availability"""
        sources = {
            'arxiv': [],
            'researchgate': [],
            'academia': [],
            'publisher': [],
            'unknown': []
        }
        
        for paper in papers:
            url = paper.get('url', '').lower()
            
            if 'arxiv' in url:
                sources['arxiv'].append(paper)
            elif 'researchgate' in url:
                sources['researchgate'].append(paper)
            elif 'academia.edu' in url:
                sources['academia'].append(paper)
            elif any(pub in url for pub in ['ieee', 'acm', 'springer', 'elsevier', 'wiley']):
                sources['publisher'].append(paper)
            else:
                sources['unknown'].append(paper)
        
        return sources
    
    def estimate_download_success(self, papers: List[Dict[str, Any]]) -> Dict[str, int]:
        """Estimate download success rate"""
        sources = self.get_paper_sources(papers)
        
        # Estimate success rates by source
        success_rates = {
            'arxiv': 0.95,  # High success rate
            'researchgate': 0.70,  # Medium success rate
            'academia': 0.60,  # Medium success rate
            'publisher': 0.30,  # Low success rate (paywalls)
            'unknown': 0.20  # Low success rate
        }
        
        estimates = {}
        total_papers = len(papers)
        
        for source, papers_list in sources.items():
            if papers_list:
                estimated_success = int(len(papers_list) * success_rates[source])
                estimates[source] = estimated_success
        
        estimates['total_estimated'] = sum(estimates.values())
        estimates['total_papers'] = total_papers
        
        return estimates


