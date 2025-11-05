import os
from typing import Optional

class Config:
    """Configuration class for TDR Agent"""
    
    # Default configuration
    DEFAULT_HOSTNAME = "localhost:8000"  # Change this to your API server hostname
    DEFAULT_API_TOKEN = ""  # Set your API token here
    DEFAULT_OPENAI_API_KEY = ""  # Set your OpenRouter API key here
    DEFAULT_AI_PROVIDER = "deepseek"  # AI provider: "openai" or "deepseek"
    DEFAULT_OPENAI_MODEL = "deepseek/deepseek-chat"  # Model via OpenRouter
    DEFAULT_OPENAI_BASE_URL = "https://openrouter.ai/api/v1"  # OpenRouter API endpoint
    
    # Environment variables override defaults
    HOSTNAME = os.getenv('TDR_HOSTNAME', DEFAULT_HOSTNAME)
    API_TOKEN = os.getenv('TDR_API_TOKEN', DEFAULT_API_TOKEN)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', DEFAULT_OPENAI_API_KEY)
    AI_PROVIDER = os.getenv('AI_PROVIDER', DEFAULT_AI_PROVIDER)
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', DEFAULT_OPENAI_MODEL)
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', DEFAULT_OPENAI_BASE_URL)
    
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
    def update_config(cls, hostname: str, api_token: str, openai_api_key: str = None, ai_provider: str = None, openai_model: str = None, openai_base_url: str = None):
        """Update configuration dynamically"""
        cls.HOSTNAME = hostname
        cls.API_TOKEN = api_token
        cls.API_BASE_URL = f"https://{hostname}" if not hostname.startswith(('http://', 'https://')) else hostname
        
        if openai_api_key is not None:
            cls.OPENAI_API_KEY = openai_api_key
        if ai_provider is not None:
            cls.AI_PROVIDER = ai_provider
        if openai_model is not None:
            cls.OPENAI_MODEL = openai_model
        if openai_base_url is not None:
            cls.OPENAI_BASE_URL = openai_base_url
    
    @classmethod
    def get_config_dict(cls) -> dict:
        """Get current configuration as dictionary"""
        return {
            'hostname': cls.HOSTNAME,
            'api_token': cls.API_TOKEN,
            'api_base_url': cls.API_BASE_URL,
            'openrouter_api_key': cls.OPENAI_API_KEY,  # Using new name for external interface
            'ai_provider': cls.AI_PROVIDER,
            'openrouter_model': cls.OPENAI_MODEL,  # Using new name for external interface
            'openrouter_base_url': cls.OPENAI_BASE_URL  # Using new name for external interface
        }
