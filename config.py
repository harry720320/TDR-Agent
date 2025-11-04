import os
from typing import Optional

class Config:
    """Configuration class for TDR Agent"""
    
    # Default configuration
    DEFAULT_HOSTNAME = "localhost:8000"  # Change this to your API server hostname
    DEFAULT_API_TOKEN = ""  # Set your API token here
    DEFAULT_OPENAI_API_KEY = ""  # Set your OpenAI API key here
    DEFAULT_OPENAI_MODEL = "gpt-5-mini"  # OpenAI model to use
    
    # Environment variables override defaults
    HOSTNAME = os.getenv('TDR_HOSTNAME', DEFAULT_HOSTNAME)
    API_TOKEN = os.getenv('TDR_API_TOKEN', DEFAULT_API_TOKEN)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', DEFAULT_OPENAI_API_KEY)
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', DEFAULT_OPENAI_MODEL)
    
    # API Configuration
    API_BASE_URL = f"https://{HOSTNAME}" if not HOSTNAME.startswith(('http://', 'https://')) else HOSTNAME
    
    @classmethod
    def get_headers(cls) -> dict:
        """Get default headers for API requests"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if cls.API_TOKEN:
            headers['X-API-KEY'] = cls.API_TOKEN
            
        return headers
    
    @classmethod
    def update_config(cls, hostname: str, api_token: str, openai_api_key: str = None, openai_model: str = None):
        """Update configuration dynamically"""
        cls.HOSTNAME = hostname
        cls.API_TOKEN = api_token
        cls.API_BASE_URL = f"https://{hostname}" if not hostname.startswith(('http://', 'https://')) else hostname
        
        if openai_api_key is not None:
            cls.OPENAI_API_KEY = openai_api_key
        if openai_model is not None:
            cls.OPENAI_MODEL = openai_model
    
    @classmethod
    def get_config_dict(cls) -> dict:
        """Get current configuration as dictionary"""
        return {
            'hostname': cls.HOSTNAME,
            'api_token': cls.API_TOKEN,
            'api_base_url': cls.API_BASE_URL,
            'openai_api_key': cls.OPENAI_API_KEY,
            'openai_model': cls.OPENAI_MODEL
        }
