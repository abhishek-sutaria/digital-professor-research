#!/usr/bin/env python3
"""
Workflow 3: Paper-Referenced Profile Generator
Main orchestrator for generating profiles with paper citations
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict
from tqdm import tqdm

# Add parent directories to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import Config
from lib.person_searcher import PersonSearcher
from lib.paper_download_manager import PaperDownloadManager
from lib.content_analyzer import ContentAnalyzer
from lib.citation_tracker import CitationTracker
from lib.report_generator import ReportGenerator
from lib.checklist_generator import ChecklistGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workflow3_paper_profile.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PaperReferencedProfileGenerator:
    """Main orchestrator for paper-referenced profile generation"""
    
    def __init__(self, output_dir: str = "./output", rate_limit: float = 1.0):
        self.output_dir = output_dir
        self.rate_limit = rate_limit
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize components
        self.person_searcher = PersonSearcher()
        self.paper_downloader = PaperDownloadManager(
            output_dir=output_dir,
            rate_limit=rate_limit,
            logger=logger
        )
        self.content_analyzer = ContentAnalyzer()
        self.report_generator = ReportGenerator()
    
    def run(self, person_name: str = None, scholar_id: str = None, max_papers: int = 100) -> Dict[str, str]:
        """
        Run the complete workflow
        
        Args:
            person_name: Name of the person (optional if scholar_id provided)
            scholar_id: Google Scholar ID (more reliable)
            max_papers: Maximum papers to fetch
        
        Returns:
            Dict with output file paths
        """
        identifier = scholar_id if scholar_id else person_name
        logger.info(f"Starting Paper-Referenced Profile Generation for: {identifier}")
        
        try:
            # Step 1: Search person and fetch papers
            logger.info("Step 1: Searching for person and papers...")
            person_info, papers = self.person_searcher.search_person(
                person_name=person_name,
                scholar_id=scholar_id,
                max_papers=max_papers
            )
            
            if not papers:
                logger.error("No papers found for this person")
                raise ValueError("No papers found")
            
            logger.info(f"Found {len(papers)} papers")
            
            # Get person name from person_info if not provided
            if not person_name and 'name' in person_info:
                person_name = person_info['name']
            
            # Step 2: Download papers
            logger.info("Step 2: Downloading papers...")
            
            # Convert to DownloadResults format and download
            download_results = []
            papers_dir = Path(self.output_dir) / f"{person_name.replace(' ', '_')}_papers"
            papers_dir.mkdir(parents=True, exist_ok=True)
            
            # Temporarily override output_dir for downloads
            original_output_dir = self.paper_downloader.output_dir
            self.paper_downloader.output_dir = papers_dir
            
            for idx, paper in enumerate(papers, 1):
                result = self.paper_downloader.download_paper(paper, paper_index=idx)
                download_results.append({
                    'success': result.success,
                    'file_path': result.file_path,
                    'source': result.source,
                    'error': result.error,
                    'file_size': result.file_size
                })
            
            # Restore original output_dir
            self.paper_downloader.output_dir = original_output_dir
            
            downloaded_count = sum(1 for r in download_results if r.get('success'))
            logger.info(f"Downloaded {downloaded_count}/{len(papers)} papers")
            
            # Step 3: Analyze paper content
            logger.info("Step 3: Analyzing paper content...")
            paper_contents = self.content_analyzer.analyze_all_papers(papers, download_results)
            
            # Step 4: Initialize citation tracker and register papers
            logger.info("Step 4: Registering papers with citation tracker...")
            citation_tracker = CitationTracker()
            
            for idx, (paper, result) in enumerate(zip(papers, download_results)):
                citation_tracker.register_paper(
                    paper_id=paper.title,
                    title=paper.title,
                    authors=paper.authors,
                    year=paper.year,
                    is_downloaded=result.get('success', False)
                )
            
            # Step 5: Generate report sections with citations
            logger.info("Step 5: Generating report sections...")
            sections = self.report_generator.generate_all_sections(
                person_name, person_info, paper_contents, citation_tracker
            )
            
            logger.info(f"Generated {len(sections)} report sections")
            
            # Step 6: Generate PDF
            logger.info("Step 6: Generating PDF report...")
            pdf_path = self.report_generator.generate_pdf(
                person_name, sections, citation_tracker, self.output_dir
            )
            
            # Step 7: Generate checklist
            logger.info("Step 7: Generating checklist...")
            checklist_gen = ChecklistGenerator(citation_tracker)
            checklist_gen.generate_all_formats(
                papers, download_results, person_name, self.output_dir
            )
            
            # Generate download prompt file for undownloaded papers
            checklist_gen.generate_download_prompt_file(
                papers, download_results, person_name, self.output_dir
            )
            
            # Prepare output summary
            outputs = {
                'pdf': pdf_path,
                'papers_folder': os.path.join(self.output_dir, f"{person_name.replace(' ', '_')}_papers"),
                'checklist_html': os.path.join(self.output_dir, f"{person_name.replace(' ', '_')}_checklist.html"),
                'checklist_csv': os.path.join(self.output_dir, f"{person_name.replace(' ', '_')}_checklist.csv"),
                'checklist_json': os.path.join(self.output_dir, f"{person_name.replace(' ', '_')}_checklist.json"),
                'download_prompt': os.path.join(self.output_dir, f"{person_name.replace(' ', '_')}_download_prompt.txt")
            }
            
            logger.info("✓ Paper-Referenced Profile Generation completed successfully!")
            
            return outputs
            
        except Exception as e:
            logger.error(f"Error in workflow: {e}")
            raise


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Workflow 3: Paper-Referenced Profile Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using Scholar ID (recommended - more reliable):
  python workflow3_paper_profile/main.py --scholar-id x8xNLZQAAAAJ
  
  # Using person name (may be blocked by Google Scholar):
  python workflow3_paper_profile/main.py "Kevin Lane Keller"
  
  # Find Scholar ID:
  1. Go to scholar.google.com
  2. Search for the person
  3. Click their profile
  4. Copy ID from URL: scholar.google.com/citations?user=<ID>
        """
    )
    
    parser.add_argument(
        'person_name',
        nargs='?',
        help='Name of the person to generate profile for (optional if --scholar-id provided)'
    )
    
    parser.add_argument(
        '--scholar-id',
        help='Google Scholar ID (more reliable than name search, bypasses bot detection)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='./workflow3_output',
        help='Output directory (default: ./workflow3_output)'
    )
    
    parser.add_argument(
        '--max-papers',
        type=int,
        default=100,
        help='Maximum number of papers to analyze (default: 100)'
    )
    
    parser.add_argument(
        '--rate-limit',
        type=float,
        default=1.0,
        help='Rate limit in seconds between requests (default: 1.0)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Validate that at least one identifier is provided
    if not args.person_name and not args.scholar_id:
        parser.error("Must provide either person_name or --scholar-id")
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Validate config
        Config.validate()
        
        # Create generator
        generator = PaperReferencedProfileGenerator(
            output_dir=args.output_dir,
            rate_limit=args.rate_limit
        )
        
        # Run workflow
        outputs = generator.run(
            person_name=args.person_name,
            scholar_id=args.scholar_id,
            max_papers=args.max_papers
        )
        
        # Print results
        print("\n" + "="*60)
        print("PAPER-REFERENCED PROFILE GENERATION COMPLETED")
        print("="*60)
        if args.scholar_id:
            print(f"Scholar ID: {args.scholar_id}")
        if args.person_name:
            print(f"Person: {args.person_name}")
        print(f"Output Directory: {args.output_dir}")
        print("\nGenerated Files:")
        for file_type, file_path in outputs.items():
            print(f"  {file_type.upper()}: {file_path}")
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

