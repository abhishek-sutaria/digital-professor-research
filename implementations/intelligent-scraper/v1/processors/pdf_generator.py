import logging
import os
from typing import Dict, List, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, ListFlowable, ListItem, KeepTogether
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from datetime import datetime

logger = logging.getLogger(__name__)

class PDFGenerator:
    """PDF generator with structured sections matching the report template"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.lightgrey,
            borderPadding=5
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.darkblue
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=14
        ))
        
        # Quote style
        self.styles.add(ParagraphStyle(
            name='Quote',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20,
            rightIndent=20,
            textColor=colors.darkgrey,
            fontName='Times-Italic'
        ))
        
        # Caption style
        self.styles.add(ParagraphStyle(
            name='Caption',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=colors.grey
        ))
    
    def generate_pdf(self, person_name: str, synthesized_data: Dict[str, Any], 
                    scraped_data: Dict[str, Any], output_dir: str) -> str:
        """Generate comprehensive PDF report"""
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Create PDF filename
        safe_name = person_name.replace(' ', '_').replace('/', '_')
        pdf_filename = f"{safe_name}_profile.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        story = []
        
        # Title page
        story.extend(self._create_title_page(person_name, scraped_data))
        story.append(PageBreak())
        
        # Table of contents
        story.extend(self._create_table_of_contents())
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._create_executive_summary(synthesized_data.get('executive_summary', '')))
        story.append(PageBreak())
        
        # Personality Profile
        story.extend(self._create_personality_profile(synthesized_data.get('personality_profile', '')))
        story.append(PageBreak())
        
        # Domain Expertise
        story.extend(self._create_domain_expertise(synthesized_data.get('domain_expertise', ''), scraped_data))
        story.append(PageBreak())
        
        # Professional Background
        story.extend(self._create_professional_background(synthesized_data.get('professional_background', ''), scraped_data))
        story.append(PageBreak())
        
        # Writing Style Analysis
        story.extend(self._create_writing_style_analysis(synthesized_data.get('writing_style', ''), scraped_data))
        story.append(PageBreak())
        
        # Thought Leadership
        story.extend(self._create_thought_leadership(synthesized_data.get('thought_leadership', ''), scraped_data))
        story.append(PageBreak())
        
        # Network & Influence
        story.extend(self._create_network_influence(synthesized_data.get('network_influence', ''), scraped_data))
        story.append(PageBreak())
        
        # Appendix
        story.extend(self._create_appendix(scraped_data))
        
        # Build PDF with header/footer
        self._header_title = person_name
        doc.build(story, onFirstPage=self._page_decor, onLaterPages=self._page_decor)
        
        logger.info(f"Generated PDF report: {pdf_path}")
        return pdf_path

    def _page_decor(self, canvas, doc):
        """Draw header and page number"""
        canvas.saveState()
        # Header
        header_text = f"Digital Twin Profile · {getattr(self, '_header_title', '')}"
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.grey)
        canvas.drawString(doc.leftMargin, doc.height + doc.topMargin - 10, header_text)
        # Footer page number
        page_num = canvas.getPageNumber()
        canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 20, f"Page {page_num}")
        canvas.restoreState()
    
    def _create_title_page(self, person_name: str, scraped_data: Dict[str, Any]) -> List:
        """Create title page"""
        story = []
        
        # Main title
        story.append(Paragraph(f"Digital Twin Profile", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Person name
        story.append(Paragraph(f"{person_name}", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Subtitle
        story.append(Paragraph("Comprehensive Information Profile for AI Replication", self.styles['Heading2']))
        story.append(Spacer(1, 0.5*inch))
        
        # Basic info table
        basic_info = self._extract_basic_info(scraped_data)
        if basic_info:
            info_table = self._create_info_table(basic_info)
            story.append(info_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Generated date
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", self.styles['Caption']))
        story.append(Spacer(1, 0.2*inch))
        
        # Disclaimer
        disclaimer = """
        <b>Disclaimer:</b> This profile is generated from publicly available information and is intended 
        for educational and research purposes. All information has been collected from open sources 
        and is subject to verification.
        """
        story.append(Paragraph(disclaimer, self.styles['Caption']))
        
        return story
    
    def _create_table_of_contents(self) -> List:
        """Create table of contents"""
        story = []
        
        story.append(Paragraph("Table of Contents", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        toc_items = [
            "1. Executive Summary",
            "2. Personality Profile",
            "3. Domain Expertise & Knowledge",
            "4. Professional Background & Journey",
            "5. Content & Writing Style Analysis",
            "6. Thought Leadership & Public Presence",
            "7. Network & Influence",
            "8. Appendix"
        ]
        
        for item in toc_items:
            story.append(Paragraph(item, self.styles['CustomBodyText']))
            story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _create_executive_summary(self, content: str) -> List:
        """Create executive summary section"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        if content and not content.lower().startswith("error generating"):
            story.extend(self._render_rich_text(content))
        else:
            story.append(Paragraph("Section pending – generated summary will appear here.", self.styles['CustomBodyText']))
        
        return story
    
    def _create_personality_profile(self, content: str) -> List:
        """Create personality profile section"""
        story = []
        
        story.append(Paragraph("Personality Profile", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        if content and not content.lower().startswith("error generating"):
            story.extend(self._render_rich_text(content))
        else:
            story.append(Paragraph("Section pending – analysis in progress.", self.styles['CustomBodyText']))
        
        return story
    
    def _create_domain_expertise(self, content: str, scraped_data: Dict[str, Any]) -> List:
        """Create domain expertise section"""
        story = []
        
        story.append(Paragraph("Domain Expertise & Knowledge", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        if content and not content.lower().startswith("error generating"):
            story.extend(self._render_rich_text(content))
        else:
            story.append(Paragraph("Section pending – synthesis will be populated after enrichment.", self.styles['CustomBodyText']))
        
        # Add research papers summary
        papers = scraped_data.get('google_scholar', {}).get('publications', [])
        if papers:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Research Publications", self.styles['SubsectionHeader']))
            
            for i, paper in enumerate(papers[:10], 1):  # Limit to 10 papers
                paper_text = f"""
                <b>{i}. {paper.get('title', 'Untitled')}</b><br/>
                Authors: {paper.get('authors', 'Unknown')}<br/>
                Year: {paper.get('year', 'Unknown')}<br/>
                Venue: {paper.get('venue', 'Unknown')}<br/>
                Citations: {paper.get('citations', 0)}<br/>
                """
                story.append(Paragraph(paper_text, self.styles['CustomBodyText']))
                story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _create_professional_background(self, content: str, scraped_data: Dict[str, Any]) -> List:
        """Create professional background section"""
        story = []
        
        story.append(Paragraph("Professional Background & Journey", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        if content and not content.lower().startswith("error generating"):
            story.extend(self._render_rich_text(content))
        else:
            story.append(Paragraph("Section pending – background details to follow.", self.styles['CustomBodyText']))
        
        # Add LinkedIn experience if available
        linkedin_data = scraped_data.get('linkedin', {})
        experience = linkedin_data.get('experience', [])
        if experience:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Career Timeline", self.styles['SubsectionHeader']))
            
            for exp in experience[:10]:  # Limit to 10 experiences
                exp_text = f"""
                <b>{exp.get('title', 'Unknown Position')}</b><br/>
                {exp.get('company', 'Unknown Company')}<br/>
                {exp.get('duration', 'Unknown Duration')}<br/>
                """
                story.append(Paragraph(exp_text, self.styles['CustomBodyText']))
                story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _create_writing_style_analysis(self, content: str, scraped_data: Dict[str, Any]) -> List:
        """Create writing style analysis section"""
        story = []
        
        story.append(Paragraph("Content & Writing Style Analysis", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        if content and not content.lower().startswith("error generating"):
            story.extend(self._render_rich_text(content))
        else:
            story.append(Paragraph("Section pending – communication style synthesis to follow.", self.styles['CustomBodyText']))
        
        # Add text analysis results
        text_analysis = scraped_data.get('text_analysis', {})
        if text_analysis:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Text Analysis Results", self.styles['SubsectionHeader']))
            
            # Basic stats
            basic_stats = text_analysis.get('basic_stats', {})
            if basic_stats:
                stats_text = f"""
                <b>Writing Statistics:</b><br/>
                Average words per sentence: {basic_stats.get('average_words_per_sentence', 0):.1f}<br/>
                Average characters per word: {basic_stats.get('average_characters_per_word', 0):.1f}<br/>
                Vocabulary richness: {basic_stats.get('vocabulary_richness', 0):.2f}<br/>
                """
                story.append(Paragraph(stats_text, self.styles['CustomBodyText']))
            
            # Personality traits
            personality_traits = text_analysis.get('personality_traits', {})
            if personality_traits:
                traits_text = f"""
                <b>Personality Traits:</b><br/>
                Communication Style: {personality_traits.get('communication_style', 'Unknown')}<br/>
                Formality Level: {personality_traits.get('formality', 'Unknown')}<br/>
                Emotional Tone: {personality_traits.get('emotional_tone', 'Unknown')}<br/>
                Confidence Level: {personality_traits.get('confidence', 'Unknown')}<br/>
                """
                story.append(Paragraph(traits_text, self.styles['CustomBodyText']))
        
        return story
    
    def _create_thought_leadership(self, content: str, scraped_data: Dict[str, Any]) -> List:
        """Create thought leadership section"""
        story = []
        
        story.append(Paragraph("Thought Leadership & Public Presence", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        if content and not content.lower().startswith("error generating"):
            story.extend(self._render_rich_text(content))
        else:
            story.append(Paragraph("Section pending – public presence synthesis to follow.", self.styles['CustomBodyText']))
        
        # Add news articles
        news_data = scraped_data.get('news', {})
        articles = news_data.get('articles', [])
        if articles:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Media Coverage", self.styles['SubsectionHeader']))
            
            for i, article in enumerate(articles[:10], 1):  # Limit to 10 articles
                article_text = f"""
                <b>{i}. {article.get('title', 'Untitled')}</b><br/>
                Source: {article.get('source', 'Unknown')}<br/>
                Date: {article.get('published_time', 'Unknown')}<br/>
                """
                story.append(Paragraph(article_text, self.styles['CustomBodyText']))
                story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _create_network_influence(self, content: str, scraped_data: Dict[str, Any]) -> List:
        """Create network and influence section"""
        story = []
        
        story.append(Paragraph("Network & Influence", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        if content and not content.lower().startswith("error generating"):
            story.extend(self._render_rich_text(content))
        else:
            story.append(Paragraph("Section pending – collaborators and influence synthesis to follow.", self.styles['CustomBodyText']))
        
        # Add co-authors and collaborators
        scholar_data = scraped_data.get('google_scholar', {})
        coauthors = scholar_data.get('coauthors', [])
        if coauthors:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Key Collaborators", self.styles['SubsectionHeader']))
            
            for coauthor in coauthors[:10]:  # Limit to 10 co-authors
                coauthor_text = f"""
                <b>{coauthor.get('name', 'Unknown')}</b><br/>
                Affiliation: {coauthor.get('affiliation', 'Unknown')}<br/>
                """
                story.append(Paragraph(coauthor_text, self.styles['CustomBodyText']))
                story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _create_appendix(self, scraped_data: Dict[str, Any]) -> List:
        """Create appendix section"""
        story = []
        
        story.append(Paragraph("Appendix", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        # Data sources
        story.append(Paragraph("Data Sources", self.styles['SubsectionHeader']))
        sources_text = """
        This profile was generated using data from the following sources:<br/>
        • Google Scholar - Research papers and citations<br/>
        • Wikipedia - Biographical information<br/>
        • News Articles - Media coverage and interviews<br/>
        • YouTube - Video transcripts and presentations<br/>
        • GitHub - Code contributions and projects<br/>
        • LinkedIn - Professional background<br/>
        • University Profiles - Academic information<br/>
        """
        story.append(Paragraph(sources_text, self.styles['CustomBodyText']))
        
        # Methodology
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Methodology", self.styles['SubsectionHeader']))
        methodology_text = """
        The information in this profile was collected using automated web scraping techniques
        and processed using natural language processing and AI synthesis. All data was collected
        from publicly available sources and is subject to verification.<br/><br/>
        
        <b>Data Collection:</b> Automated scraping from multiple sources with rate limiting
        and respect for robots.txt files.<br/><br/>
        
        <b>Data Processing:</b> Text analysis, sentiment analysis, and pattern recognition
        using NLTK and custom algorithms.<br/><br/>
        
        <b>Content Synthesis:</b> AI-powered summarization and synthesis using Google's
        Gemini API to create coherent, comprehensive profiles.<br/><br/>
        
        <b>Quality Assurance:</b> Cross-validation across multiple sources and confidence
        scoring for data accuracy.
        """
        story.append(Paragraph(methodology_text, self.styles['CustomBodyText']))
        
        # Statistics
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Data Statistics", self.styles['SubsectionHeader']))
        
        stats = self._calculate_data_stats(scraped_data)
        stats_text = f"""
        <b>Data Collection Summary:</b><br/>
        • Research Papers: {stats.get('papers', 0)}<br/>
        • News Articles: {stats.get('articles', 0)}<br/>
        • YouTube Videos: {stats.get('videos', 0)}<br/>
        • GitHub Repositories: {stats.get('repos', 0)}<br/>
        • Total Data Points: {stats.get('total', 0)}<br/>
        • Data Collection Date: {datetime.now().strftime('%Y-%m-%d')}<br/>
        """
        story.append(Paragraph(stats_text, self.styles['CustomBodyText']))
        
        return story
    
    def _extract_basic_info(self, scraped_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract basic information for title page"""
        info = {}
        
        # Try to get basic info from different sources
        if 'wikipedia' in scraped_data:
            wiki_data = scraped_data['wikipedia']
            info['Full Name'] = wiki_data.get('title', '')
            info['Occupation'] = wiki_data.get('structured_info', {}).get('occupation', '')
        
        if 'google_scholar' in scraped_data:
            scholar_data = scraped_data['google_scholar']
            basic_info = scholar_data.get('basic_info', {})
            if not info.get('Full Name'):
                info['Full Name'] = basic_info.get('name', '')
            info['Affiliation'] = basic_info.get('affiliation', '')
            info['Research Interests'] = ', '.join(basic_info.get('interests', [])[:5])
        
        if 'linkedin' in scraped_data:
            linkedin_data = scraped_data['linkedin']
            if not info.get('Occupation'):
                info['Occupation'] = linkedin_data.get('title', '')
            info['Company'] = linkedin_data.get('company', '')
        
        return info
    
    def _create_info_table(self, info: Dict[str, str]) -> Table:
        """Create information table"""
        data = []
        for key, value in info.items():
            if value:
                data.append([key, value])
        
        if not data:
            return None
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _calculate_data_stats(self, scraped_data: Dict[str, Any]) -> Dict[str, int]:
        """Calculate data statistics"""
        stats = {
            'papers': 0,
            'articles': 0,
            'videos': 0,
            'repos': 0,
            'total': 0
        }
        
        # Count papers
        if 'google_scholar' in scraped_data:
            papers = scraped_data['google_scholar'].get('publications', [])
            stats['papers'] = len(papers)
        
        # Count articles
        if 'news' in scraped_data:
            articles = scraped_data['news'].get('articles', [])
            stats['articles'] = len(articles)
        
        # Count videos
        if 'youtube' in scraped_data:
            videos = scraped_data['youtube'].get('videos', [])
            stats['videos'] = len(videos)
        
        # Count repositories
        if 'github' in scraped_data:
            repos = scraped_data['github'].get('repositories', [])
            stats['repos'] = len(repos)
        
        stats['total'] = sum(stats.values())
        return stats

    def _render_rich_text(self, content: str) -> List:
        """Convert raw section text into styled flowables (paragraphs, lists, quotes)."""
        flowables: List = []
        if not content:
            return flowables
        # Normalize line endings
        text = content.replace('\r\n', '\n').replace('\r', '\n')
        blocks = [b.strip() for b in text.split('\n\n') if b.strip()]
        for block in blocks:
            lines = block.split('\n')
            # Detect bullet list
            if all(l.strip().startswith(('-', '•', '*')) for l in lines if l.strip()):
                items = []
                for l in lines:
                    t = l.lstrip('-•*').strip()
                    items.append(ListItem(Paragraph(self._convert_markdown_to_reportlab(t), self.styles['CustomBodyText']), leftIndent=10))
                flowables.append(ListFlowable(items, bulletType='bullet', start='•', leftIndent=15, spaceBefore=4, spaceAfter=6))
                continue
            # Detect numbered list
            import re
            if all(re.match(r"^\s*\d+\.\s+", l) for l in lines if l.strip()):
                items = []
                for l in lines:
                    t = re.sub(r"^\s*\d+\.\s+", "", l).strip()
                    items.append(ListItem(Paragraph(self._convert_markdown_to_reportlab(t), self.styles['CustomBodyText']), leftIndent=10))
                flowables.append(ListFlowable(items, bulletType='1', start='1', leftIndent=15, spaceBefore=4, spaceAfter=6))
                continue
            # Detect quote block ("...")
            if block.startswith('"') and block.endswith('"') and len(block) > 2:
                flowables.append(Paragraph(self._convert_markdown_to_reportlab(block), self.styles['Quote']))
                continue
            # Regular paragraph
            flowables.append(Paragraph(self._convert_markdown_to_reportlab(block), self.styles['CustomBodyText']))
            flowables.append(Spacer(1, 0.08*inch))
        # Ensure grouping
        return [KeepTogether(flowables)] if flowables else flowables

    def _convert_markdown_to_reportlab(self, text: str) -> str:
        """Convert markdown formatting to ReportLab-compatible markup."""
        import re
        
        # Escape HTML first
        text = self._escape_html(text)
        
        # Convert markdown bold **text** to <b>text</b>
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        
        # Convert markdown italic *text* to <i>text</i>
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        
        # Convert markdown headers # Header to bold
        text = re.sub(r'^#+\s*(.*)$', r'<b>\1</b>', text, flags=re.MULTILINE)
        
        # Clean up any remaining ** artifacts
        text = re.sub(r'\*\*', '', text)
        
        # Convert line breaks to <br/> for proper spacing
        text = text.replace('\n', '<br/>')
        
        return text

    def _escape_html(self, text: str) -> str:
        # Very light escaping; ReportLab supports simple inline markup
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
