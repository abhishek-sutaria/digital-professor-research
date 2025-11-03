"""
Citation Tracker
Tracks which papers are used in which sections and provides citation formatting
"""

import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class PaperReference:
    """Reference to a paper used in citation"""
    paper_id: str
    title: str
    authors: str
    year: str
    is_downloaded: bool = False
    
    def format_citation(self) -> str:
        """Format inline citation"""
        if self.is_downloaded:
            return f"[From: {self.title}, {self.authors} {self.year}]"
        else:
            return f"[From: {self.title}, {self.authors} {self.year} - metadata only]"


class CitationTracker:
    """Tracks citations across sections and papers"""
    
    def __init__(self):
        # section_name -> list of paper_ids
        self.section_papers: Dict[str, List[str]] = defaultdict(list)
        
        # paper_id -> list of section_names
        self.paper_sections: Dict[str, Set[str]] = defaultdict(set)
        
        # paper_id -> PaperReference
        self.paper_refs: Dict[str, PaperReference] = {}
    
    def register_paper(self, paper_id: str, title: str, authors: str, 
                      year: str, is_downloaded: bool = False):
        """Register a paper with its metadata"""
        self.paper_refs[paper_id] = PaperReference(
            paper_id=paper_id,
            title=title,
            authors=authors,
            year=year,
            is_downloaded=is_downloaded
        )
    
    def add_citation(self, section_name: str, paper_id: str):
        """Add a citation of paper in section"""
        if paper_id not in self.paper_refs:
            logger.warning(f"Paper {paper_id} not registered, skipping citation")
            return
        
        # Add to section's paper list
        if paper_id not in self.section_papers[section_name]:
            self.section_papers[section_name].append(paper_id)
        
        # Add to paper's section set
        self.paper_sections[paper_id].add(section_name)
    
    def format_inline_citation(self, paper_id: str) -> str:
        """Get formatted inline citation for a paper"""
        if paper_id in self.paper_refs:
            return self.paper_refs[paper_id].format_citation()
        return f"[From: Unknown Paper]"
    
    def get_section_papers(self, section_name: str) -> List[str]:
        """Get all papers cited in a section"""
        return self.section_papers.get(section_name, [])
    
    def get_paper_sections(self, paper_id: str) -> List[str]:
        """Get all sections that cite a paper"""
        return sorted(list(self.paper_sections.get(paper_id, set())))
    
    def get_all_sections(self) -> List[str]:
        """Get all section names that have citations"""
        return list(self.section_papers.keys())
    
    def get_all_papers(self) -> List[str]:
        """Get all paper IDs that are cited"""
        return list(self.paper_sections.keys())
    
    def get_paper_ref(self, paper_id: str) -> Optional[PaperReference]:
        """Get PaperReference for a paper"""
        return self.paper_refs.get(paper_id)
    
    def get_statistics(self) -> Dict:
        """Get citation statistics"""
        return {
            'total_papers': len(self.paper_refs),
            'cited_papers': len(self.paper_sections),
            'total_sections': len(self.section_papers),
            'papers_by_status': {
                'downloaded': sum(1 for p in self.paper_refs.values() if p.is_downloaded),
                'metadata_only': sum(1 for p in self.paper_refs.values() if not p.is_downloaded)
            },
            'section_paper_counts': {
                section: len(papers) 
                for section, papers in self.section_papers.items()
            }
        }


