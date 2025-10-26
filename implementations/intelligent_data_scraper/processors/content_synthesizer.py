import logging
import time
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from config import Config

logger = logging.getLogger(__name__)

class GeminiSynthesizer:
    """Gemini API integration for content summarization and synthesis"""
    
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
    
    def synthesize_person_profile(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize comprehensive person profile using Gemini"""
        
        # Prepare data for synthesis
        synthesis_prompts = {
            'executive_summary': self._create_executive_summary_prompt(scraped_data),
            'personality_profile': self._create_personality_prompt(scraped_data),
            'domain_expertise': self._create_expertise_prompt(scraped_data),
            'professional_background': self._create_background_prompt(scraped_data),
            'writing_style': self._create_writing_style_prompt(scraped_data),
            'thought_leadership': self._create_thought_leadership_prompt(scraped_data),
            'network_influence': self._create_network_prompt(scraped_data)
        }
        
        synthesized_content = {}
        
        for section, prompt in synthesis_prompts.items():
            try:
                synthesized_content[section] = self._generate_with_chunking(prompt)
                logger.info(f"Successfully synthesized {section}")
            except Exception as e:
                logger.error(f"Error synthesizing {section}: {e}")
                try:
                    synthesized_content[section] = self._fallback_section(section, scraped_data)
                except Exception:
                    synthesized_content[section] = "Section pending – insufficient data or temporary error."
        
        return synthesized_content
    
    def _create_executive_summary_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for executive summary"""
        prompt = f"""
        Create a comprehensive 2-page executive summary for a digital twin profile. 
        Focus on capturing the complete essence of this person for AI replication.
        
        Available data:
        - Google Scholar: {data.get('google_scholar', {})}
        - Wikipedia: {data.get('wikipedia', {})}
        - News Articles: {data.get('news', {})}
        - YouTube Videos: {data.get('youtube', {})}
        - GitHub: {data.get('github', {})}
        - LinkedIn: {data.get('linkedin', {})}
        - University: {data.get('university', {})}
        
        Include:
        1. Core identity and professional role
        2. Key expertise areas and signature concepts
        3. Communication style and personality traits
        4. Notable achievements and influence
        5. Unique perspectives and approaches
        6. How they think and make decisions
        
        Write in a professional, comprehensive style suitable for AI training data.
        """
        return prompt
    
    def _create_personality_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for personality profile"""
        prompt = f"""
        Analyze and synthesize a detailed personality profile (6-8 pages) for digital twin creation.
        
        Data sources:
        - Writing samples: {data.get('writing_samples', [])}
        - Interview transcripts: {data.get('interviews', [])}
        - Social media posts: {data.get('social_media', [])}
        - Public statements: {data.get('public_statements', [])}
        - Text analysis: {data.get('text_analysis', {})}
        
        Analyze and describe:
        1. Communication style and tone
        2. Decision-making patterns and approach
        3. Core values and principles
        4. Behavioral traits and quirks
        5. How they handle different situations
        6. Leadership and collaboration style
        7. Problem-solving approach
        8. Emotional patterns and responses
        9. Motivations and drivers
        10. Unique personality markers
        
        Provide specific examples and quotes where possible.
        Focus on traits that would help an AI replicate their personality.
        """
        return prompt
    
    def _create_expertise_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for domain expertise"""
        # Curate top branding publications (title/year/venue/cites) up to 25
        pubs = (data.get('google_scholar', {}) or {}).get('publications', []) or []
        keywords = ['brand', 'branding', 'brand equity', 'positioning', 'resonance',
                    'loyalty', 'architecture', 'portfolio', 'imc', 'communication']
        def score_pub(p):
            title = (p.get('title') or '').lower()
            venue = (p.get('venue') or '').lower()
            abstract = (p.get('abstract') or '').lower()
            hits = sum(1 for k in keywords if k in title or k in venue or k in abstract)
            cites = int(p.get('citations') or 0)
            return hits * 1000 + cites
        curated = sorted(pubs, key=score_pub, reverse=True)[:25]
        curated_lines = [
            f"- {p.get('title','').strip()} | {p.get('year','')} | {p.get('venue','')} | cites:{p.get('citations',0)}"
            for p in curated
        ]
        curated_block = "\n".join(curated_lines) if curated_lines else "(no curated items)"

        outline = (
            "Core concepts to cover: Customer-Based Brand Equity (CBBE) pyramid; brand resonance; brand positioning; "
            "brand elements and secondary associations; integrated marketing communications (IMC); brand portfolios and architecture; "
            "measurement of brand equity; managing brands over time; co-branding/licensing/alliances; global branding; digital/social contexts."
        )

        prompt = f"""
        Produce a 12–15 page Domain Expertise & Knowledge chapter about Kevin Lane Keller.
        Write as a rigorous, structured narrative for AI training.

        Use these curated publications (title | year | venue | citations):
        {curated_block}

        {outline}

        Requirements:
        - Organize into sections/subsections; avoid bullet dumps.
        - Tie concepts back to papers informally (no formal citations).
        - Be didactic: definitions, explanations, examples, edge cases.
        - Keep to Keller's contributions; avoid generic marketing filler.
        - Flow: foundations → applications → measurement → stewardship.
        """
        return prompt
    
    def _create_background_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for professional background"""
        prompt = f"""
        Create a detailed professional background and journey (4-5 pages) for digital twin creation.
        
        Data sources:
        - Career history: {data.get('career_history', [])}
        - Education: {data.get('education', [])}
        - Companies/brands: {data.get('companies', [])}
        - Achievements: {data.get('achievements', [])}
        - Timeline: {data.get('timeline', [])}
        
        Document:
        1. Career evolution and key milestones
        2. Education and formative experiences
        3. Companies/brands they've built or worked with
        4. Major achievements and recognition
        5. Career transitions and pivots
        6. Mentors and influences
        7. Challenges overcome
        8. Current focus and future direction
        
        Focus on experiences that shaped their thinking and approach.
        """
        return prompt
    
    def _create_writing_style_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for writing style analysis"""
        prompt = f"""
        Analyze writing style and communication patterns (5-7 pages) for digital twin creation.
        
        Data sources:
        - Text analysis: {data.get('text_analysis', {})}
        - Writing samples: {data.get('writing_samples', [])}
        - Articles: {data.get('articles', [])}
        - Social media: {data.get('social_media', [])}
        
        Analyze:
        1. Vocabulary and linguistic patterns
        2. Storytelling techniques and narrative style
        3. Metaphors and analogies they use
        4. Sentence structure and rhythm
        5. Authentic quotes and catchphrases
        6. Tone variations across contexts
        7. Persuasion and argumentation style
        8. Humor and wit patterns
        9. Technical vs. accessible language use
        10. Cultural and contextual references
        
        Include specific examples and patterns.
        Focus on replicable communication styles.
        """
        return prompt
    
    def _create_thought_leadership_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for thought leadership"""
        prompt = f"""
        Synthesize thought leadership and public presence (5-7 pages) for digital twin creation.
        
        Data sources:
        - Books: {data.get('books', [])}
        - Articles: {data.get('articles', [])}
        - Speaking engagements: {data.get('speaking', [])}
        - Social media presence: {data.get('social_media', [])}
        - Interviews: {data.get('interviews', [])}
        
        Document:
        1. Books, articles, and key publications
        2. Speaking engagements and presentations
        3. Social media presence and engagement style
        4. Interviews and podcast appearances
        5. Media coverage and public perception
        6. Influence on industry and thought
        7. Controversies and debates they've engaged in
        8. Evolution of their public message
        9. Audience engagement and community building
        10. Legacy and lasting impact
        
        Focus on their public intellectual persona.
        """
        return prompt
    
    def _create_network_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for network and influence"""
        prompt = f"""
        Analyze network and influence (3-4 pages) for digital twin creation.
        
        Data sources:
        - Collaborators: {data.get('collaborators', [])}
        - Co-authors: {data.get('coauthors', [])}
        - Mentors: {data.get('mentors', [])}
        - References: {data.get('references', [])}
        - Influence metrics: {data.get('influence_metrics', {})}
        
        Analyze:
        1. Collaborators and mentors
        2. Who they reference and respect
        3. Their influence on the industry
        4. Network effects and relationships
        5. Community building and leadership
        6. Cross-industry connections
        7. Generational influence
        8. Geographic and cultural reach
        9. Professional vs. personal networks
        10. Legacy and succession planning
        
        Focus on relationship patterns and influence networks.
        """
        return prompt
    
    def extract_key_insights(self, content: str, max_insights: int = 10) -> List[str]:
        """Extract key insights from content using Gemini"""
        prompt = f"""
        Extract the {max_insights} most important insights from the following content.
        Each insight should be a clear, actionable statement.
        
        Content: {content}
        
        Return only the insights, one per line, without numbering or bullet points.
        """
        
        try:
            text = self._generate_with_chunking(prompt)
            insights = [line.strip() for line in text.split('\n') if line.strip()]
            return insights[:max_insights]
        except Exception as e:
            logger.error(f"Error extracting insights: {e}")
            return []
    
    def summarize_content(self, content: str, max_length: int = 500) -> str:
        """Summarize content using Gemini"""
        prompt = f"""
        Summarize the following content in approximately {max_length} words.
        Maintain the key points and tone of the original.
        
        Content: {content}
        """
        
        try:
            return self._generate_with_chunking(prompt)
        except Exception as e:
            logger.error(f"Error summarizing content: {e}")
            return content[:max_length] + "..." if len(content) > max_length else content
    
    def generate_quotes(self, data: Dict[str, Any], max_quotes: int = 20) -> List[str]:
        """Generate representative quotes using Gemini"""
        prompt = f"""
        Based on the following data about this person, generate {max_quotes} representative quotes
        that capture their voice, style, and key messages. Make them sound authentic to their personality.
        
        Data: {data}
        
        Return only the quotes, one per line, without quotation marks or attribution.
        """
        
        try:
            text = self._generate_with_chunking(prompt)
            quotes = [line.strip() for line in text.split('\n') if line.strip()]
            return quotes[:max_quotes]
        except Exception as e:
            logger.error(f"Error generating quotes: {e}")
            return []

    def _generate_with_chunking(self, prompt: str, max_retries: int = 5) -> str:
        """Generate content with retries and chunking to avoid timeouts."""
        # Basic retry loop
        backoff = 2
        for attempt in range(max_retries):
            try:
                # If prompt too long, split into chunks and map-reduce
                if len(prompt) > 8000:
                    chunks = self._split_prompt(prompt, chunk_size=4000)
                    partials: List[str] = []
                    for ch in chunks:
                        result = self.model.generate_content(ch)
                        partial = self._result_to_text(result)
                        partials.append(partial)
                    # Reduce
                    reduce_prompt = """
                    Combine the following sections into a cohesive, structured chapter:
                    
                    {}""".format("\n\n".join(partials))
                    red = self.model.generate_content(reduce_prompt)
                    return self._result_to_text(red)
                else:
                    res = self.model.generate_content(prompt)
                    return self._result_to_text(res)
            except Exception as e:
                logger.debug(f"Attempt {attempt+1} failed: {e}")
                time.sleep(backoff)
                backoff *= 2
        raise RuntimeError("generation failed after retries")

    def _split_prompt(self, text: str, chunk_size: int = 4000) -> List[str]:
        parts: List[str] = []
        i = 0
        while i < len(text):
            parts.append(text[i:i+chunk_size])
            i += chunk_size
        return parts

    def _result_to_text(self, result: Any) -> str:
        """Robustly extract text from a Gemini response."""
        try:
            if hasattr(result, 'text') and result.text:
                return result.text
        except Exception:
            pass
        try:
            # Fallback: concatenate parts
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

    def _fallback_section(self, section: str, data: Dict[str, Any]) -> str:
        """Last-resort synthesis using a minimal outline so the PDF isn't empty."""
        outlines = {
            'domain_expertise': "Summarize CBBE pyramid, brand resonance, positioning, IMC, brand architecture, measurement, and applications to digital/social. Provide 6–8 cohesive paragraphs with definitions and examples.",
            'professional_background': "Give a structured 3–4 page overview of roles, affiliations (Dartmouth/Tuck; earlier Stanford/Berkeley/UNC/Duke), major achievements, and influence.",
            'thought_leadership': "Synthesize books/articles, talks, and public stance on branding. Provide a 4–5 page narrative with notable ideas and their evolution.",
        }
        hint = outlines.get(section, "Provide a cohesive 2–3 page narrative summary of this section.")
        prompt = f"Create the section '{section.replace('_',' ').title()}' for Kevin Lane Keller. {hint}"
        try:
            res = self.model.generate_content(prompt)
            return self._result_to_text(res)
        except Exception:
            return "Section pending – insufficient data or temporary error."


