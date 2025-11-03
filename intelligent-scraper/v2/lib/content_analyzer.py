"""
Content Analyzer
Extracts and analyzes content from downloaded papers
"""

import logging
import sys
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
import fitz  # PyMuPDF
import re

# Add parent paths for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

logger = logging.getLogger(__name__)


@dataclass
class PaperContent:
    """Analyzed content from a paper"""
    paper_id: str
    title: str
    authors: str
    year: str
    abstract: str
    key_points: List[str]
    methodologies: List[str]
    notable_quotes: List[str]
    full_text: str
    citations: int = 0  # Citation count for sorting


class ContentAnalyzer:
    """Analyzes paper content and extracts key information"""
    
    def __init__(self):
        pass
    
    def analyze_all_papers(self, papers: List, download_results: List[Dict[str, Any]]) -> Dict[str, PaperContent]:
        """
        Analyze all downloaded papers
        
        Args:
            papers: List of PaperMetadata objects
            download_results: List of download result dicts
            
        Returns:
            Dict mapping paper_id to PaperContent
        """
        analyzed_papers = {}
        
        for idx, (paper, result) in enumerate(zip(papers, download_results)):
            if result.get('success'):
                try:
                    content = self.analyze_paper(paper, result['file_path'])
                    analyzed_papers[paper.title] = content
                    logger.info(f"Analyzed: {paper.title[:60]}")
                except Exception as e:
                    logger.error(f"Error analyzing paper: {e}")
            else:
                # Store metadata-only paper
                analyzed_papers[paper.title] = PaperContent(
                    paper_id=f"paper_{idx}",
                    title=paper.title,
                    authors=paper.authors,
                    year=paper.year,
                    abstract=paper.abstract or '',
                    key_points=[],
                    methodologies=[],
                    notable_quotes=[],
                    full_text='',
                    citations=paper.citations  # Preserve citation count for sorting
                )
        
        logger.info(f"Analyzed {len([c for c in analyzed_papers.values() if c.full_text])} papers with full text")
        return analyzed_papers
    
    def analyze_paper(self, paper, file_path: str) -> PaperContent:
        """
        Analyze a single paper PDF
        
        Args:
            paper: PaperMetadata object
            file_path: Path to downloaded PDF
            
        Returns:
            PaperContent object
        """
        # Extract text from PDF
        full_text = self._extract_text_from_pdf(file_path)
        
        # Extract structured information
        abstract = self._extract_abstract(full_text)
        key_points = self._extract_key_points(full_text)
        methodologies = self._extract_methodologies(full_text)
        notable_quotes = self._extract_quotes(full_text)
        
        return PaperContent(
            paper_id=paper.title,
            title=paper.title,
            authors=paper.authors,
            year=paper.year,
            abstract=abstract or paper.abstract or '',
            key_points=key_points,
            methodologies=methodologies,
            notable_quotes=notable_quotes,
            full_text=full_text,
            citations=paper.citations  # Preserve citation count
        )
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            
            for page in doc:
                text += page.get_text()
            
            doc.close()
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def _extract_abstract(self, text: str) -> Optional[str]:
        """Extract abstract from text"""
        # Look for "Abstract" section
        patterns = [
            r'Abstract\s*\n\s*([^A-Z]{200,1500})',
            r'ABSTRACT\s*\n\s*([^A-Z]{200,1500})',
            r'Summary\s*\n\s*([^A-Z]{200,1500})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                abstract = match.group(1).strip()
                # Clean up
                abstract = re.sub(r'\s+', ' ', abstract)
                abstract = abstract[:1000]  # Limit length
                return abstract
        
        # If no abstract found, take first few sentences
        sentences = re.split(r'[.!?]\s+', text[:2000])
        if len(sentences) > 3:
            return '. '.join(sentences[:3]) + '.'
        
        return None
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text"""
        key_points = []
        
        # Look for section headings that might indicate key points
        # Methods, Results, Conclusion, Findings, etc.
        sections = re.findall(
            r'(?:^|\n)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\n',
            text[:5000]
        )
        
        # Look for bullet points or numbered lists
        bullets = re.findall(r'(?:^|\n)[•\-\*\d+\.]\s+([^•\-\*\n]{50,300})', text)
        
        # Combine and deduplicate
        key_points.extend([s for s in sections if len(s) > 5])
        key_points.extend(bullets[:10])
        
        # Limit and clean
        key_points = list(set(key_points))[:15]
        key_points = [kp.strip() for kp in key_points if len(kp.strip()) > 20]
        
        return key_points
    
    def _extract_methodologies(self, text: str) -> List[str]:
        """Extract methodological approaches"""
        methodologies = []
        
        # Look for methodology-related keywords
        methodology_keywords = [
            r'survey\s+(?:method|study|design)',
            r'experiment(al)?',
            r'qualitative\s+analysis',
            r'quantitative\s+analysis',
            r'case\s+study',
            r'field\s+study',
            r'longitudinal\s+study',
            r'meta[-\s]?analysis',
            r'statistical\s+analysis'
        ]
        
        for pattern in methodology_keywords:
            matches = re.findall(pattern, text[:5000], re.IGNORECASE)
            if matches:
                methodologies.extend(matches[:3])
        
        return list(set(methodologies))
    
    def _extract_quotes(self, text: str) -> List[str]:
        """Extract notable quotes"""
        # Look for text in quotation marks
        quotes = re.findall(r'"([^"]{50,300})"', text[:3000])
        
        # Limit to most relevant
        return quotes[:5]

