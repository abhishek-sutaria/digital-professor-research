"""
Report Generator
Generates comprehensive reports with inline citations using Gemini API
"""

import logging
import os
import sys
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import google.generativeai as genai
from google.api_core import exceptions as api_exceptions
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY
import re

# Add parent paths for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config import Config
from lib.citation_tracker import CitationTracker

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates reports with inline citations"""
    
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required. Set it in .env file")
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        self.model_name = Config.GEMINI_MODEL
        self.fallback_models = Config.GEMINI_FALLBACK_MODELS
        self.current_model_index = 0
        self.logger = logging.getLogger(__name__)
    
    def generate_all_sections(self, person_name: str, person_info: Dict[str, Any], 
                             paper_contents: Dict[str, Any], 
                             citation_tracker: CitationTracker) -> Dict[str, str]:
        """
        Generate all 10 report sections with inline citations
        
        Returns:
            Dict of section_name -> generated content
        """
        self.logger.info(f"Generating report sections for {person_name}...")
        
        sections = {}
        section_configs = self._get_section_configs()
        
        for section_key, section_config in section_configs.items():
            try:
                self.logger.info(f"Generating {section_key}...")
                
                # Prepare paper excerpts for this section
                paper_excerpts = self._prepare_paper_excerpts_for_section(
                    section_key, paper_contents
                )
                
                # Generate section
                content = self._generate_section(
                    person_name, 
                    section_key,
                    section_config,
                    paper_excerpts,
                    citation_tracker
                )
                
                sections[section_key] = content
                self.logger.info(f"✓ Generated {section_key}")
                
                # Brief pause between sections
                time.sleep(1)
                
            except Exception as e:
                error_msg = str(e)
                if isinstance(e, RuntimeError) and "quota exceeded" in error_msg.lower():
                    self.logger.error(f"Error generating {section_key}: API quota exceeded. Consider waiting or upgrading to paid tier.")
                    sections[section_key] = f"[Error: API quota exceeded for {section_key}. Please wait and retry, or upgrade to paid tier.]"
                else:
                    self.logger.error(f"Error generating {section_key}: {type(e).__name__}: {error_msg}")
                    sections[section_key] = f"[Error generating {section_key}: {error_msg[:200]}]"
        
        return sections
    
    def _get_section_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get configuration for each section"""
        return {
            'executive_summary': {
                'title': 'Executive Summary',
                'length': '2-3 pages',
                'focus': 'Complete overview of person and their contributions'
            },
            'personality_profile': {
                'title': 'Personality Profile & Communication Style',
                'length': '6-8 pages',
                'focus': 'Communication patterns, personality traits, values'
            },
            'intellectual_profile': {
                'title': 'Intellectual Profile & Mindset',
                'length': '8-10 pages',
                'focus': 'Core beliefs, problem-solving, decision-making, innovation'
            },
            'domain_expertise': {
                'title': 'Domain Expertise & Knowledge Base',
                'length': '10-12 pages',
                'focus': 'Key concepts, frameworks, methodologies, contributions'
            },
            'research_methodology': {
                'title': 'Research Methodology & Approach',
                'length': '6-8 pages',
                'focus': 'Methodological preferences, study designs, validation'
            },
            'professional_background': {
                'title': 'Professional Background & Journey',
                'length': '4-5 pages',
                'focus': 'Career evolution, education, achievements'
            },
            'evolution_ideas': {
                'title': 'Evolution of Ideas & Thinking',
                'length': '6-8 pages',
                'focus': 'Conceptual development over time, intellectual trajectory'
            },
            'thought_leadership': {
                'title': 'Thought Leadership & Public Presence',
                'length': '5-7 pages',
                'focus': 'Books, articles, speaking, public engagement'
            },
            'collaboration_network': {
                'title': 'Collaboration & Network Influence',
                'length': '4-5 pages',
                'focus': 'Co-author networks, collaborations, influence'
            },
            'bibliography': {
                'title': 'Complete Bibliography & References',
                'length': '3-4 pages',
                'focus': 'Full references for all cited papers'
            }
        }
    
    def _prepare_paper_excerpts_for_section(self, section_key: str, 
                                           paper_contents: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Prepare relevant paper excerpts for a section
        
        Returns:
            List of paper excerpt dicts with title, year, authors, key_points
        """
        excerpts = []
        
        # Separate downloaded from metadata-only papers
        downloaded_papers = [(pid, content) for pid, content in paper_contents.items() if content.full_text]
        metadata_only_papers = [(pid, content) for pid, content in paper_contents.items() if not content.full_text]
        
        # Sort downloaded papers by content richness
        sorted_downloaded = sorted(
            downloaded_papers,
            key=lambda x: len(x[1].key_points) + len(x[1].full_text[:500]),
            reverse=True
        )
        
        # Sort metadata papers by citations (impact proxy)
        sorted_metadata = sorted(
            metadata_only_papers,
            key=lambda x: x[1].citations,  # Use citation count
            reverse=True  # Most cited papers first
        )
        
        # Take all downloaded papers first, then top metadata papers up to 20 total
        papers_to_include = list(sorted_downloaded[:15])  # Max 15 downloaded
        remaining_slots = 20 - len(papers_to_include)
        papers_to_include.extend(sorted_metadata[:remaining_slots])
        
        # Take papers up to limit
        for paper_id, content in papers_to_include:
            excerpt = {
                'id': paper_id,
                'title': content.title,
                'authors': content.authors,
                'year': content.year,
                'abstract': content.abstract[:500] if content.abstract else '',
                'key_points': content.key_points[:10],  # Top 10 key points
                'methodologies': content.methodologies[:5],
                'is_downloaded': bool(content.full_text)
            }
            excerpts.append(excerpt)
        
        return excerpts
    
    def _generate_section(self, person_name: str, section_key: str, 
                         section_config: Dict[str, Any],
                         paper_excerpts: List[Dict[str, str]],
                         citation_tracker: CitationTracker) -> str:
        """Generate a single section with inline citations"""
        
        # Build prompt with paper excerpts
        prompt = self._build_section_prompt(
            person_name, section_key, section_config, paper_excerpts
        )
        
        # Generate content
        content = self._generate_with_retries(prompt)
        
        # Parse and track citations
        self._extract_and_track_citations(content, section_key, paper_excerpts, citation_tracker)
        
        return content
    
    def _build_section_prompt(self, person_name: str, section_key: str,
                             section_config: Dict[str, Any],
                             paper_excerpts: List[Dict[str, str]]) -> str:
        """Build prompt for section generation"""
        
        # Build paper excerpts text
        paper_text = ""
        for idx, excerpt in enumerate(paper_excerpts, 1):
            status = "[DOWNLOADED]" if excerpt['is_downloaded'] else "[METADATA ONLY]"
            
            paper_text += f"\n{idx}. \"{excerpt['title']}\" ({excerpt['year']}) by {excerpt['authors']} {status}\n"
            
            if excerpt['abstract']:
                paper_text += f"   Abstract: {excerpt['abstract'][:300]}...\n"
            
            if excerpt['key_points']:
                for point in excerpt['key_points'][:5]:
                    paper_text += f"   - {point}\n"
        
        # Build full prompt
        prompt = f"""
Generate a {section_config['length']} "{section_config['title']}" section for {person_name}.

Focus on: {section_config['focus']}

Available research papers and key points:
{paper_text}

CRITICAL MANDATORY REQUIREMENTS (MUST FOLLOW):
1. Write in PARAGRAPH form (not bullet points or lists)
2. **YOU MUST add a citation at the END of EVERY single paragraph** - no exceptions
3. Citation format: [From: Paper Title, Author Year]
4. If paper not downloaded, add: [From: Paper Title, Author Year - metadata only]
5. **EVERY paragraph MUST end with a citation** - this is mandatory
6. Each paragraph should be 3-5 sentences
7. Be specific about which paper supports each claim
8. If you don't cite papers, the output is INVALID

Example paragraph format:
"This section discusses important concepts from their research. The analysis reveals key patterns in their methodology and approach to problem-solving. [From: Paper Title, Author Year]"

**REMEMBER: EVERY paragraph MUST end with a citation from the papers list above. NO exceptions.**

Generate the complete section now:
"""
        
        return prompt
    
    def _extract_and_track_citations(self, content: str, section_key: str,
                                     paper_excerpts: List[Dict[str, str]],
                                     citation_tracker: CitationTracker):
        """
        Extract citations from generated content and track them
        
        Citation format: [From: Title, Author Year] or [From: Title, Author Year - metadata only]
        """
        # Find all citations in the text
        citations = re.findall(
            r'\[From:\s+([^,]+),\s+([^\]]+)\](?:\s*-\s*metadata only)?',
            content
        )
        
        self.logger.debug(f"Found {len(citations)} citations in {section_key}")
        
        # Track each citation
        for title, author_year in citations:
            # Match to paper excerpt
            for excerpt in paper_excerpts:
                if title in excerpt['title'] or excerpt['title'] in title:
                    # Extract paper ID and track citation
                    citation_tracker.add_citation(section_key, excerpt['id'])
                    self.logger.debug(f"Tracked citation: {excerpt['title'][:50]} in {section_key}")
                    break
        
        if not citations:
            self.logger.warning(f"No citations found in {section_key} section")
            # Debug: show first 500 chars of generated content
            self.logger.debug(f"Generated content sample: {content[:500]}")
    
    def _generate_with_retries(self, prompt: str, max_retries: int = 3) -> str:
        """Generate content with retry logic and proper error handling"""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                # Handle long prompts by chunking
                if len(prompt) > 8000:
                    return self._generate_with_chunking(prompt)
                else:
                    result = self.model.generate_content(prompt)
                    return self._extract_text(result)
                    
            except api_exceptions.ResourceExhausted as e:
                # Quota exceeded - handle specially
                last_exception = e
                self.logger.error(f"Attempt {attempt + 1} failed: API quota exceeded (429)")
                self.logger.error(f"Error details: {str(e)[:300]}")
                
                # Extract retry delay from error if available
                retry_delay = Config.GEMINI_QUOTA_RETRY_DELAY
                error_str = str(e)
                if "retry_delay" in error_str or "Please retry in" in error_str:
                    # Try to extract delay from error message
                    import re as regex
                    delay_match = regex.search(r'retry in ([\d.]+)s', error_str, regex.IGNORECASE)
                    if delay_match:
                        extracted_delay = float(delay_match.group(1))
                        retry_delay = max(extracted_delay, 30)  # Minimum 30 seconds
                
                if attempt < max_retries - 1:
                    self.logger.warning(f"Waiting {retry_delay:.1f} seconds before retry (quota exceeded)...")
                    time.sleep(retry_delay)
                    # Try fallback model on next attempt
                    if attempt == max_retries - 2:  # Last retry attempt
                        fallback_model = self._get_fallback_model()
                        if fallback_model:
                            self.logger.info(f"Trying fallback model: {fallback_model}")
                            self.model = genai.GenerativeModel(fallback_model)
                            self.model_name = fallback_model
                else:
                    # Final attempt - try fallback model
                    fallback_model = self._get_fallback_model()
                    if fallback_model:
                        self.logger.info(f"Primary model quota exceeded, trying fallback model: {fallback_model}")
                        self.model = genai.GenerativeModel(fallback_model)
                        self.model_name = fallback_model
                        # One more attempt with fallback
                        try:
                            result = self.model.generate_content(prompt)
                            return self._extract_text(result)
                        except Exception as fallback_error:
                            self.logger.error(f"Fallback model also failed: {fallback_error}")
                    
            except Exception as e:
                # Other exceptions - log at ERROR level
                last_exception = e
                self.logger.error(f"Attempt {attempt + 1} failed: {type(e).__name__}: {str(e)[:300]}")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.debug(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
        
        # All retries exhausted
        error_msg = f"Generation failed after {max_retries} retries"
        if last_exception:
            error_msg += f": {type(last_exception).__name__}"
            if isinstance(last_exception, api_exceptions.ResourceExhausted):
                error_msg += " (API quota exceeded - consider waiting or upgrading to paid tier)"
        raise RuntimeError(error_msg)
    
    def _get_fallback_model(self) -> Optional[str]:
        """Get next fallback model when primary model quota is exceeded"""
        if not self.fallback_models:
            return None
        
        # Try next fallback model
        if self.current_model_index < len(self.fallback_models):
            fallback = self.fallback_models[self.current_model_index]
            self.current_model_index += 1
            return fallback
        
        return None
    
    def _generate_with_chunking(self, prompt: str) -> str:
        """Generate content for long prompts using chunking"""
        # Split prompt into parts
        chunks = self._split_prompt(prompt, chunk_size=4000)
        partials = []
        
        for chunk in chunks:
            result = self.model.generate_content(chunk)
            partials.append(self._extract_text(result))
        
        # Combine results
        reduce_prompt = "Combine the following sections into a cohesive narrative:\n\n" + "\n\n---\n\n".join(partials)
        result = self.model.generate_content(reduce_prompt)
        return self._extract_text(result)
    
    def _split_prompt(self, text: str, chunk_size: int = 4000) -> List[str]:
        """Split long text into chunks"""
        chunks = []
        i = 0
        while i < len(text):
            chunks.append(text[i:i+chunk_size])
            i += chunk_size
        return chunks
    
    def _extract_text(self, result) -> str:
        """Extract text from Gemini response"""
        try:
            if hasattr(result, 'text') and result.text:
                return result.text
        except Exception:
            pass
        
        # Fallback: concatenate parts
        try:
            parts = []
            for c in getattr(result, 'candidates', []) or []:
                content = getattr(c, 'content', None)
                if not content:
                    continue
                for p in getattr(content, 'parts', []) or []:
                    val = getattr(p, 'text', None)
                    if val:
                        parts.append(val)
            return "\n".join(parts) if parts else ""
        except Exception:
            return ""
    
    def generate_pdf(self, person_name: str, sections: Dict[str, str],
                    citation_tracker: CitationTracker, output_dir: str) -> str:
        """
        Generate PDF report from sections
        
        Returns:
            Path to generated PDF
        """
        self.logger.info(f"Generating PDF report...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        safe_name = person_name.replace(' ', '_')
        pdf_path = os.path.join(output_dir, f"{safe_name}_profile.pdf")
        
        # Set up PDF styles
        styles = getSampleStyleSheet()
        body_style = ParagraphStyle(
            name='Body',
            parent=styles['Normal'],
            alignment=TA_JUSTIFY,
            leading=14,
            fontSize=11
        )
        h1_style = styles['Heading1']
        h2_style = styles['Heading2']
        
        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            leftMargin=72,
            rightMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Title page
        story.append(Paragraph(f"{person_name} - Digital Twin Profile", h1_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph(
            "Comprehensive Analysis with Research Paper Citations",
            body_style
        ))
        story.append(PageBreak())
        
        # Add sections
        section_configs = self._get_section_configs()
        for section_key, section_config in section_configs.items():
            content = sections.get(section_key, '')
            
            if content and section_key != 'bibliography':
                # Add section title
                story.append(Paragraph(section_config['title'], h1_style))
                story.append(Spacer(1, 12))
                
                # Add content with citations
                self._add_section_content(story, content, body_style)
                story.append(PageBreak())
        
        # Bibliography section
        self._add_bibliography(story, citation_tracker, h1_style, h2_style, body_style)
        
        # Build PDF
        try:
            doc.build(story)
            self.logger.info(f"Generated PDF: {pdf_path}")
            return pdf_path
        except Exception as e:
            self.logger.error(f"Error generating PDF: {e}")
            raise
    
    def _add_section_content(self, story, content: str, body_style):
        """Add section content to PDF story"""
        # Split into paragraphs
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            if para.strip():
                formatted = self._convert_markdown_to_reportlab(para.strip())
                story.append(Paragraph(formatted, body_style))
                story.append(Spacer(1, 8))
    
    def _convert_markdown_to_reportlab(self, text: str) -> str:
        """Convert markdown formatting to ReportLab-compatible markup"""
        # Escape HTML special chars first
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        
        # Convert markdown bold (**text**)
        text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
        
        # Convert markdown italic (*text*) - only if not already part of bold
        text = re.sub(r'(?<!\*)\*([^*<]+?)\*(?!\*)', r'<i>\1</i>', text)
        
        # Convert headers (# Header)
        text = re.sub(r'^#+\s*(.*)$', r'<b>\1</b>', text, flags=re.MULTILINE)
        
        # Clean up any remaining ** artifacts
        text = text.replace('**', '')
        
        # Fix nested tag issues
        text = re.sub(r'<b>([^<]*)<i>([^<]*)</b></i>', r'<b>\1<i>\2</i></b>', text)
        text = re.sub(r'<i>([^<]*)<b>([^<]*)</i></b>', r'<i>\1<b>\2</b></i>', text)
        
        # Convert single line breaks to <br/>
        text = text.replace('\n', '<br/>')
        
        return text
    
    def _add_bibliography(self, story, citation_tracker: CitationTracker,
                         h1_style, h2_style, body_style):
        """Add bibliography section"""
        story.append(Paragraph("Complete Bibliography & References", h1_style))
        story.append(Spacer(1, 12))
        
        # Get all cited papers
        cited_papers = citation_tracker.get_all_papers()
        
        if not cited_papers:
            story.append(Paragraph("No papers were cited in this report.", body_style))
            return
        
        # Group by download status
        downloaded_refs = []
        metadata_refs = []
        
        for paper_id in cited_papers:
            ref = citation_tracker.get_paper_ref(paper_id)
            if ref:
                if ref.is_downloaded:
                    downloaded_refs.append(ref)
                else:
                    metadata_refs.append(ref)
        
        # Add downloaded papers
        if downloaded_refs:
            story.append(Paragraph("Downloaded Papers", h2_style))
            story.append(Spacer(1, 8))
            
            for ref in downloaded_refs:
                bib_entry = f"{ref.authors}. {ref.title}. {ref.year}."
                story.append(Paragraph(bib_entry, body_style))
                story.append(Spacer(1, 4))
        
        # Add metadata-only papers
        if metadata_refs:
            story.append(Paragraph("Additional References (Metadata Only)", h2_style))
            story.append(Spacer(1, 8))
            
            for ref in metadata_refs:
                bib_entry = f"{ref.authors}. {ref.title}. {ref.year}. (Citation from available metadata)"
                story.append(Paragraph(bib_entry, body_style))
                story.append(Spacer(1, 4))

