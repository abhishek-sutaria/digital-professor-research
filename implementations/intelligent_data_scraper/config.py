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
    
    # User Agent for web scraping
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required. Please set it in .env file")
        return True

