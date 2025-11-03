import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the Person Information Scraper"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Optional API Keys
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
    
    # Scraping Configuration
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
    RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', 2.0))
    
    # Output Configuration
    DEFAULT_OUTPUT_DIR = 'output'
    MAX_CONTENT_LENGTH = 1000000  # 1MB max per content piece
    
    # Rate Limiting
    REQUESTS_PER_MINUTE = 30
    REQUESTS_PER_HOUR = 1000
    
    # Content Limits
    MAX_ARTICLES = 50
    MAX_TWEETS = 500
    MAX_VIDEOS = 20
    MAX_PAPERS = 100
    
    # Gemini Configuration
    GEMINI_MODEL = 'gemini-2.5-flash'
    MAX_TOKENS = 8192
    GEMINI_FALLBACK_MODELS = ['gemini-2.0-flash', 'gemini-1.5-flash']
    GEMINI_QUOTA_RETRY_DELAY = int(os.getenv('GEMINI_QUOTA_RETRY_DELAY', 60))  # Seconds
    
    # Unpaywall Configuration
    UNPAYWALL_EMAIL = os.getenv('UNPAYWALL_EMAIL', 'abhishek.sutaria@gmail.com')
    
    # Paper Selection Configuration
    PAPER_SELECTION_STRATEGY = os.getenv('PAPER_SELECTION_STRATEGY', 'citations')  # 'citations', 'first-author', 'hybrid'
    MAX_PAPERS_TO_ANALYZE = int(os.getenv('MAX_PAPERS_TO_ANALYZE', 70))
    
    # Download Configuration
    DOWNLOAD_TIMEOUT = int(os.getenv('DOWNLOAD_TIMEOUT', 60))
    ENABLE_ARXIV_DOWNLOADS = os.getenv('ENABLE_ARXIV_DOWNLOADS', 'true').lower() == 'true'
    ENABLE_DOI_RESOLUTION = os.getenv('ENABLE_DOI_RESOLUTION', 'true').lower() == 'true'
    ENABLE_UNPAYWALL = os.getenv('ENABLE_UNPAYWALL', 'true').lower() == 'true'
    
    # Digital Twin Report Configuration
    DIGITAL_TWIN_REPORT_LENGTH = int(os.getenv('DIGITAL_TWIN_REPORT_LENGTH', 60))  # Target pages
    CITATION_STYLE = os.getenv('CITATION_STYLE', 'inline_with_paper_title')
    
    # User Agent for web scraping
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required. Please set it in .env file")
        return True

