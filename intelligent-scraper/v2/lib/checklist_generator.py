"""
Checklist Generator
Generates detailed checklists showing paper usage across sections
"""

import logging
import csv
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ChecklistEntry:
    """Single entry in paper checklist"""
    index: int
    title: str
    authors: str
    year: str
    venue: str
    citations: int
    doi: Optional[str]
    download_status: str
    file_path: Optional[str]
    sections_used: List[str]
    access_suggestions: List[str]


class ChecklistGenerator:
    """Generates paper checklists in multiple formats"""
    
    def __init__(self, citation_tracker):
        self.citation_tracker = citation_tracker
        self.logger = logging.getLogger(__name__)
    
    def generate_all_formats(self, papers: List, download_results: List[Dict[str, Any]], 
                            person_name: str, output_dir: str):
        """
        Generate checklist in all formats
        
        Args:
            papers: List of PaperMetadata objects
            download_results: List of download result dicts
            person_name: Person's name for filenames
            output_dir: Output directory path
        """
        # Create checklist entries
        entries = self._create_entries(papers, download_results)
        
        # Generate each format
        safe_name = person_name.replace(' ', '_')
        base_name = f"{output_dir}/{safe_name}_checklist"
        
        self._generate_html(entries, f"{base_name}.html")
        self._generate_csv(entries, f"{base_name}.csv")
        self._generate_json(entries, f"{base_name}.json")
        
        self.logger.info(f"Generated checklist files: {base_name}.{{html,csv,json}}")
    
    def _create_entries(self, papers: List, download_results: List[Dict[str, Any]]) -> List[ChecklistEntry]:
        """Create checklist entries from papers and download results"""
        entries = []
        
        for idx, (paper, result) in enumerate(zip(papers, download_results), 1):
            # Determine download status
            if result.get('success'):
                download_status = "✓ Downloaded"
                file_path = result.get('file_path')
            else:
                download_status = "✗ Not Available"
                file_path = None
            
            # Get sections where this paper is cited
            sections = self.citation_tracker.get_paper_sections(paper.title)
            
            # Generate access suggestions if not downloaded
            access_suggestions = []
            if not result.get('success'):
                if paper.doi:
                    access_suggestions.append(f"DOI: https://doi.org/{paper.doi}")
                if paper.url:
                    access_suggestions.append(f"Publisher: {paper.url}")
                if paper.pub_url:
                    access_suggestions.append(f"Scholar: {paper.pub_url}")
                
                # Suggest library access
                access_suggestions.append("Consider: institutional library access, interlibrary loan, or author contact")
            
            entry = ChecklistEntry(
                index=idx,
                title=paper.title,
                authors=paper.authors,
                year=paper.year,
                venue=paper.venue,
                citations=paper.citations,
                doi=paper.doi,
                download_status=download_status,
                file_path=file_path,
                sections_used=sections if sections else [],
                access_suggestions=access_suggestions
            )
            
            entries.append(entry)
        
        return entries
    
    def _generate_html(self, entries: List[ChecklistEntry], output_path: str):
        """Generate HTML checklist"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Paper Checklist</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; font-weight: bold; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        tr:hover { background-color: #f5f5f5; }
        .downloaded { color: green; font-weight: bold; }
        .not-available { color: red; font-weight: bold; }
        .sections { font-size: 0.9em; color: #666; }
    </style>
</head>
<body>
    <h1>Paper Checklist</h1>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Title</th>
                <th>Authors</th>
                <th>Year</th>
                <th>Venue</th>
                <th>Citations</th>
                <th>DOI</th>
                <th>Status</th>
                <th>Sections Used In</th>
                <th>Access Suggestions</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for entry in entries:
            status_class = "downloaded" if entry.download_status == "✓ Downloaded" else "not-available"
            sections_str = ", ".join(entry.sections_used) if entry.sections_used else "(not cited)"
            suggestions_str = "<br>".join(entry.access_suggestions) if entry.access_suggestions else "-"
            
            html += f"""
            <tr>
                <td>{entry.index}</td>
                <td>{entry.title}</td>
                <td>{entry.authors}</td>
                <td>{entry.year}</td>
                <td>{entry.venue}</td>
                <td>{entry.citations}</td>
                <td>{entry.doi or '-'}</td>
                <td class="{status_class}">{entry.download_status}</td>
                <td class="sections">{sections_str}</td>
                <td class="sections">{suggestions_str}</td>
            </tr>
"""
        
        html += """
        </tbody>
    </table>
</body>
</html>
"""
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_csv(self, entries: List[ChecklistEntry], output_path: str):
        """Generate CSV checklist"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Index', 'Title', 'Authors', 'Year', 'Venue', 'Citations',
                'DOI', 'Download Status', 'File Path', 'Sections Used In', 'Access Suggestions'
            ])
            
            # Write rows
            for entry in entries:
                writer.writerow([
                    entry.index,
                    entry.title,
                    entry.authors,
                    entry.year,
                    entry.venue,
                    entry.citations,
                    entry.doi or '',
                    entry.download_status,
                    entry.file_path or '',
                    '; '.join(entry.sections_used) if entry.sections_used else '',
                    ' | '.join(entry.access_suggestions) if entry.access_suggestions else ''
                ])
    
    def _generate_json(self, entries: List[ChecklistEntry], output_path: str):
        """Generate JSON checklist"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'entries': [asdict(entry) for entry in entries],
            'summary': {
                'total_papers': len(entries),
                'downloaded': sum(1 for e in entries if e.download_status == "✓ Downloaded"),
                'not_available': sum(1 for e in entries if e.download_status == "✗ Not Available"),
                'cited_papers': sum(1 for e in entries if e.sections_used)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def generate_download_prompt_file(self, papers: List, download_results: List[Dict[str, Any]], 
                                     person_name: str, output_dir: str):
        """
        Generate a text file with a prompt listing all undownloaded papers
        
        Args:
            papers: List of PaperMetadata objects
            download_results: List of download result dicts
            person_name: Person's name for filename
            output_dir: Output directory path
        """
        # Filter undownloaded papers
        undownloaded_papers = []
        for paper, result in zip(papers, download_results):
            if not result.get('success', False):
                undownloaded_papers.append(paper)
        
        if not undownloaded_papers:
            self.logger.info("All papers downloaded - skipping download prompt file generation")
            return
        
        # Generate file path
        safe_name = person_name.replace(' ', '_')
        output_path = Path(output_dir) / f"{safe_name}_download_prompt.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate content
        prompt_text = "Show me how to download the research papers from here by actually downloading the following research papers:\n\n"
        
        # Add numbered list of papers
        for idx, paper in enumerate(undownloaded_papers, 1):
            prompt_text += f"{idx}. {paper.title}\n"
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(prompt_text)
        
        self.logger.info(f"Generated download prompt file: {output_path} ({len(undownloaded_papers)} undownloaded papers)")


