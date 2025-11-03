#!/usr/bin/env python3
"""
Person Information Scraper - Main CLI Application
Comprehensive web scraping tool for creating digital twin profiles
"""

import argparse
import logging
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from storage.cache_manager import CacheManager
from scrapers.google_scholar_scraper import GoogleScholarScraper
from scrapers.wikipedia_scraper import WikipediaScraper
from scrapers.news_scraper import NewsScraper
try:
    from scrapers.youtube_scraper import YouTubeScraper  # optional
except Exception:
    YouTubeScraper = None
try:
    from scrapers.github_scraper import GitHubScraper  # optional
except Exception:
    GitHubScraper = None
try:
    from scrapers.linkedin_scraper import LinkedInScraper  # optional
except Exception:
    LinkedInScraper = None
from scrapers.university_scraper import UniversityScraper
from processors.text_analyzer import TextAnalyzer
from processors.content_synthesizer import GeminiSynthesizer
from processors.pdf_generator import PDFGenerator
from processors.publications_enricher import PublicationsEnricher
from processors.paper_downloader import PaperDownloader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping_log.txt'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class PersonInformationScraper:
    """Main application class for person information scraping"""
    
    def __init__(self, output_dir: str = None, force_refresh: bool = False, overrides: Dict[str, Any] = None):
        self.output_dir = output_dir or Config.DEFAULT_OUTPUT_DIR
        self.force_refresh = force_refresh
        self.overrides = overrides or {}
        
        # Initialize components
        self.cache_manager = CacheManager()
        self.text_analyzer = TextAnalyzer()
        
        # Initialize scrapers
        self.scrapers = {
            'google_scholar': GoogleScholarScraper(self.cache_manager),
            'wikipedia': WikipediaScraper(self.cache_manager),
            'news': NewsScraper(self.cache_manager),
            'university': UniversityScraper(self.cache_manager)
        }
        if YouTubeScraper:
            self.scrapers['youtube'] = YouTubeScraper(self.cache_manager)
        if GitHubScraper:
            self.scrapers['github'] = GitHubScraper(self.cache_manager)
        if LinkedInScraper:
            self.scrapers['linkedin'] = LinkedInScraper(self.cache_manager)
        
        # Initialize processors
        self.synthesizer = GeminiSynthesizer()
        self.pdf_generator = PDFGenerator()
        self.paper_downloader = PaperDownloader(self.cache_manager)
        self.publications_enricher = PublicationsEnricher()
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def search_person(self, name: str) -> List[Dict[str, Any]]:
        """Search for a person across all sources"""
        logger.info(f"Searching for: {name}")
        
        all_candidates = []
        
        # Search each source
        for source_name, scraper in self.scrapers.items():
            try:
                logger.info(f"Searching {source_name}...")
                candidates = scraper.search_person(name)
                
                # Add source information
                for candidate in candidates:
                    candidate['source'] = source_name
                
                all_candidates.extend(candidates)
                logger.info(f"Found {len(candidates)} candidates from {source_name}")
                
            except Exception as e:
                logger.error(f"Error searching {source_name}: {e}")
                continue
        
        # Rank candidates by confidence
        ranked_candidates = self._rank_candidates(all_candidates)
        
        return ranked_candidates
    
    def _rank_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank candidates by confidence score"""
        # Group by source and calculate average confidence
        source_groups = {}
        for candidate in candidates:
            source = candidate.get('source', 'unknown')
            if source not in source_groups:
                source_groups[source] = []
            source_groups[source].append(candidate)
        
        # Calculate combined confidence
        for candidate in candidates:
            source = candidate.get('source', 'unknown')
            source_candidates = source_groups[source]
            
            # Average confidence within source
            avg_confidence = sum(c.get('confidence_score', 0) for c in source_candidates) / len(source_candidates)
            
            # Weight by source reliability
            source_weights = {
                'wikipedia': 0.9,
                'google_scholar': 0.8,
                'linkedin': 0.7,
                'github': 0.6,
                'university': 0.8,
                'news': 0.5,
                'youtube': 0.4
            }
            
            weight = source_weights.get(source, 0.5)
            candidate['combined_confidence'] = candidate.get('confidence_score', 0) * weight + avg_confidence * 0.1
        
        # Sort by combined confidence
        return sorted(candidates, key=lambda x: x.get('combined_confidence', 0), reverse=True)
    
    def select_person(self, candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Interactive person selection"""
        if not candidates:
            logger.error("No candidates found")
            return None
        
        # Auto-select if high confidence
        top_candidate = candidates[0]
        if top_candidate.get('combined_confidence', 0) > 0.5:  # Lowered threshold for auto-selection
            logger.info(f"Auto-selecting high confidence match: {top_candidate.get('name', 'Unknown')}")
            return top_candidate
        
        # Show options
        print(f"\nFound {len(candidates)} potential matches for your search:")
        print("=" * 60)
        
        for i, candidate in enumerate(candidates[:10], 1):  # Show top 10
            name = candidate.get('name', 'Unknown')
            title = candidate.get('title', '')
            company = candidate.get('company', '')
            affiliation = candidate.get('affiliation', '')
            confidence = candidate.get('combined_confidence', 0)
            
            print(f"{i}. {name}")
            if title:
                print(f"   Title: {title}")
            if company:
                print(f"   Company: {company}")
            if affiliation:
                print(f"   Affiliation: {affiliation}")
            print(f"   Confidence: {confidence:.2f}")
            print()
        
        # Auto-select the first candidate in non-interactive environments
        logger.info("Auto-selecting first candidate for non-interactive environment")
        return candidates[0]
    
    def scrape_person_data(self, person_info: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape comprehensive data for selected person"""
        # Avoid passing 'name' twice (positional + kw)
        profile_kwargs = dict(person_info)
        profile_name = profile_kwargs.pop('name', 'Unknown')
        person_id = self.cache_manager.create_person_profile(profile_name, **profile_kwargs)
        
        logger.info(f"Scraping data for: {person_info.get('name', 'Unknown')}")
        
        scraped_data = {}
        
        # Scrape from each source
        # Apply URL overrides if provided
        if self.overrides.get('wikipedia_url'):
            scraped_data['wikipedia'] = self._scrape_wikipedia_by_url(self.overrides['wikipedia_url'])

        for source_name, scraper in self.scrapers.items():
            try:
                logger.info(f"Scraping {source_name}...")
                
                # Check cache first
                if not self.force_refresh:
                    cached_data = self.cache_manager.get_scraped_data(person_id, source_name)
                    if cached_data:
                        logger.info(f"Using cached data for {source_name}")
                        scraped_data[source_name] = self._process_cached_data(cached_data)
                        continue
                
                # Scrape fresh data
                source_data = scraper.scrape_person(person_info)
                if source_data:
                    scraped_data[source_name] = source_data
                    
                    # Cache the data
                    self._cache_scraped_data(person_id, source_name, source_data)
                
                logger.info(f"Completed scraping {source_name}")
                
            except Exception as e:
                logger.error(f"Error scraping {source_name}: {e}")
                continue
        
        return scraped_data

    def _scrape_wikipedia_by_url(self, url: str) -> Dict[str, Any]:
        try:
            from scrapers.wikipedia_scraper import WikipediaScraper
            ws = WikipediaScraper(self.cache_manager)
            # Extract title from URL
            if "/wiki/" in url:
                title = url.split("/wiki/")[-1].replace('_', ' ')
                return ws.scrape_person({'title': title})
        except Exception as e:
            logger.warning(f"Failed direct Wikipedia scrape from URL {url}: {e}")
        return {}
    
    def _process_cached_data(self, cached_data: List[Dict]) -> Dict[str, Any]:
        """Process cached data into the expected format"""
        result = {}
        for item in cached_data:
            data_type = item.get('data_type', 'unknown')
            content = item.get('content', '')
            
            if data_type not in result:
                result[data_type] = []
            
            result[data_type].append(content)
        
        return result
    
    def _cache_scraped_data(self, person_id: int, source: str, data: Dict[str, Any]):
        """Cache scraped data"""
        for data_type, content in data.items():
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, str):
                        self.cache_manager.store_scraped_data(
                            person_id, source, data_type, item
                        )
            elif isinstance(content, str):
                self.cache_manager.store_scraped_data(
                    person_id, source, data_type, content
                )
    
    def analyze_and_synthesize(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze scraped data and synthesize insights"""
        logger.info("Analyzing and synthesizing data...")
        
        # Text analysis
        text_samples = self._extract_text_samples(scraped_data)
        text_analysis = self.text_analyzer.analyze_writing_style(text_samples)
        scraped_data['text_analysis'] = text_analysis
        
        # Publications enrichment if scholar data is missing or thin
        name_guess = scraped_data.get('wikipedia', {}).get('title') or ' '.join([str(x) for x in [
            scraped_data.get('linkedin', {}).get('name'),
            scraped_data.get('google_scholar', {}).get('basic_info', {}).get('name')
        ] if x])
        if name_guess:
            enriched_pubs = self.publications_enricher.enrich_by_author(name_guess, topic_hint='marketing branding', max_results=100)
            if enriched_pubs:
                # Strict author filter: Kevin Lane Keller + known affiliations
                filtered_pubs = self.publications_enricher.filter_by_exact_author(
                    enriched_pubs,
                    exact_name='kevin lane keller',
                    affiliation_keywords=['dartmouth', 'tuck', 'brand', 'branding', 'brand equity', 'journal of marketing', 'jmr', 'jcr']
                )
                if 'google_scholar' not in scraped_data:
                    scraped_data['google_scholar'] = {}
                scraped_data['google_scholar']['publications'] = filtered_pubs

        # Gemini synthesis (with chunking handled inside synthesizer later)
        synthesized_content = self.synthesizer.synthesize_person_profile(scraped_data)
        
        return synthesized_content
    
    def _extract_text_samples(self, scraped_data: Dict[str, Any]) -> List[str]:
        """Extract text samples for analysis"""
        text_samples = []
        
        # Extract from different sources
        sources_to_extract = [
            ('wikipedia', 'extract'),
            ('news', 'articles'),
            ('youtube', 'videos'),
            ('linkedin', 'summary'),
            ('university', 'biography')
        ]
        
        for source, field in sources_to_extract:
            if source in scraped_data:
                data = scraped_data[source]
                
                if field in data:
                    content = data[field]
                    if isinstance(content, list):
                        text_samples.extend(content)
                    elif isinstance(content, str):
                        text_samples.append(content)
        
        return text_samples
    
    def generate_outputs(self, person_name: str, scraped_data: Dict[str, Any], 
                        synthesized_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate final output files"""
        logger.info("Generating output files...")
        
        outputs = {}
        
        # Generate PDF
        pdf_path = self.pdf_generator.generate_pdf(
            person_name, synthesized_data, scraped_data, self.output_dir
        )
        outputs['pdf'] = pdf_path
        
        # Download papers
        papers = scraped_data.get('google_scholar', {}).get('publications', [])
        if papers:
            zip_path = self.paper_downloader.download_papers(
                papers, person_name, self.output_dir
            )
            outputs['papers_zip'] = zip_path
        
        # Save raw data
        raw_data_path = os.path.join(self.output_dir, f"{person_name.replace(' ', '_')}_raw_data.json")
        with open(raw_data_path, 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)
        outputs['raw_data'] = raw_data_path
        
        return outputs
    
    def run(self, person_name: str) -> Dict[str, str]:
        """Main execution method"""
        try:
            # Validate configuration
            Config.validate()
            
            logger.info(f"Starting Person Information Scraper for: {person_name}")
            
            # Step 1/2: If scholar_id override provided, lock identity and skip search
            if self.overrides.get('scholar_id'):
                selected_person = {
                    'name': person_name,
                    'scholar_id': self.overrides.get('scholar_id')
                }
                logger.info("Using provided Google Scholar ID for identity lock.")
            else:
                # Step 1: Search for person
                candidates = self.search_person(person_name)
                if not candidates:
                    raise ValueError("No candidates found for the given name")
                
                # Step 2: Select person
                selected_person = self.select_person(candidates)
                if not selected_person:
                    # Auto-select the highest confidence candidate if no user input
                    if candidates:
                        selected_person = candidates[0]
                        logger.info(f"Auto-selected highest confidence candidate: {selected_person.get('name', 'Unknown')}")
                    else:
                        raise ValueError("No person selected")
            
            # Step 3: Scrape data
            scraped_data = self.scrape_person_data(selected_person)
            if not scraped_data:
                raise ValueError("No data scraped")
            
            # Step 4: Analyze and synthesize
            synthesized_data = self.analyze_and_synthesize(scraped_data)
            
            # Step 5: Generate outputs
            outputs = self.generate_outputs(person_name, scraped_data, synthesized_data)
            
            logger.info("Person Information Scraper completed successfully!")
            return outputs
            
        except Exception as e:
            logger.error(f"Error in Person Information Scraper: {e}")
            raise

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Person Information Scraper - Create comprehensive digital twin profiles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Seth Godin"
  python main.py "Gary Vaynerchuk" --output-dir ./profiles
  python main.py "Ann Handley" --force-refresh
        """
    )
    
    parser.add_argument(
        'name',
        help='Name of the person to scrape information about'
    )
    
    parser.add_argument(
        '--output-dir',
        default='./output',
        help='Output directory for generated files (default: ./output)'
    )
    
    parser.add_argument(
        '--force-refresh',
        action='store_true',
        help='Force refresh of cached data'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    # URL/ID overrides
    parser.add_argument('--wikipedia-url', help='Explicit Wikipedia URL for the person')
    parser.add_argument('--scholar-id', help='Explicit Google Scholar ID for the person')
    parser.add_argument('--faculty-url', help='Explicit faculty profile URL for the person')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Create scraper instance
        scraper = PersonInformationScraper(
            output_dir=args.output_dir,
            force_refresh=args.force_refresh,
            overrides={
                'wikipedia_url': args.wikipedia_url,
                'scholar_id': args.scholar_id,
                'faculty_url': args.faculty_url,
            }
        )
        
        # Run scraper
        outputs = scraper.run(args.name)
        
        # Print results
        print("\n" + "="*60)
        print("PERSON INFORMATION SCRAPER - COMPLETED")
        print("="*60)
        print(f"Person: {args.name}")
        print(f"Output Directory: {args.output_dir}")
        print("\nGenerated Files:")
        for file_type, file_path in outputs.items():
            print(f"  {file_type.upper()}: {file_path}")
        
        print(f"\nTotal execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

