# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-19

### Added
- **Hybrid Natural Language Processing System**
  - Rule-based parsing for common queries (fast and free)
  - AI-powered parsing via OpenRouter for complex queries
  - Support for multiple AI providers (OpenAI and DeepSeek via OpenRouter)

- **AI-Powered Response Analysis**
  - Intelligent explanation of API responses in natural language
  - Multi-language support (Simplified Chinese, Traditional Chinese, Japanese, Korean, Arabic, Russian, English)
  - Automatic language detection from user queries
  - Security-focused analysis with risk assessment and recommendations

- **Web Interface**
  - Modern, responsive UI built with React and Tailwind CSS
  - Real-time query processing and API request generation
  - Interactive configuration panel
  - API response display with AI-powered explanations
  - Copy-to-clipboard functionality

- **API Integration**
  - Support for OpenText Core TDR API endpoints
  - Automatic parameter extraction (dates, limits, IDs, etc.)
  - CORS proxy to bypass browser restrictions
  - Comprehensive error handling and troubleshooting tools

- **Configuration Management**
  - Web-based configuration interface
  - Persistent configuration storage in `tdr_config.json`
  - Support for OpenRouter API integration
  - Configurable AI provider selection (OpenAI/DeepSeek)
  - Model selection for each provider

- **Multi-language Support**
  - Automatic language detection
  - Localized prompts for query parsing and response explanation
  - Support for 7 languages: English, Simplified Chinese, Traditional Chinese, Japanese, Korean, Arabic, Russian

### Technical Details
- Built with Flask (Python backend) and React (frontend)
- Uses OpenRouter API for AI model access
- Supports both OpenAI and DeepSeek models
- Configuration stored in JSON format
- Comprehensive logging and error handling

### Files
- `app.py` - Main Flask application
- `config.py` - Configuration management
- `templates/index.html` - React frontend UI
- `openapi.json` - API specification
- `requirements.txt` - Python dependencies

