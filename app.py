from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import re
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from config import Config
import openai
import requests
import os
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_language(text: str) -> str:
    """Detect the language of the input text"""
    # Remove spaces and get total character count
    total_chars = len(re.sub(r'\s', '', text))
    
    if total_chars == 0:
        return 'en'  # Default to English if no characters
    
    # Traditional Chinese characters (more specific range for Traditional Chinese)
    traditional_chars = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]', text))
    
    # Simplified Chinese characters (common simplified characters)
    simplified_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    
    # Chinese characters (CJK Unified Ideographs - both Simplified and Traditional)
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    
    # Japanese characters (Hiragana, Katakana, some Kanji)
    japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]', text))
    
    # Korean characters
    korean_chars = len(re.findall(r'[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]', text))
    
    # Arabic characters
    arabic_chars = len(re.findall(r'[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\ufb50-\ufdff\ufe70-\ufeff]', text))
    
    # Cyrillic characters (Russian, etc.)
    cyrillic_chars = len(re.findall(r'[\u0400-\u04ff]', text))
    
    # Calculate ratios
    chinese_ratio = chinese_chars / total_chars
    japanese_ratio = japanese_chars / total_chars
    korean_ratio = korean_chars / total_chars
    arabic_ratio = arabic_chars / total_chars
    cyrillic_ratio = cyrillic_chars / total_chars
    
    # Detect Traditional Chinese by checking for specific traditional characters
    # These are characters that are distinctly different in Traditional vs Simplified Chinese
    traditional_specific_chars = len(re.findall(r'[繁體學習實務資訊網電腦資料庫員顯組織異執威脅偵測應報議評風險等級關鍵發現執麼異為麼們被認為潛擊解釋簡潔與於個會對來說過時這樣還從根據將讓夠進處設置測試連態應請數詢端點標題援幫說]', text))
    # Debug logging for language detection
    logger.info(f"Language detection for '{text}': chinese_ratio={chinese_ratio:.3f}, traditional_specific_chars={traditional_specific_chars}")
    
    # Determine language based on highest ratio
    max_ratio = max(chinese_ratio, japanese_ratio, korean_ratio, arabic_ratio, cyrillic_ratio)
    
    if max_ratio > 0.3:  # If any non-Latin script has significant presence
        # Check for Traditional Chinese first - if any traditional-specific characters are found, use Traditional Chinese
        if chinese_ratio > 0.3 and traditional_specific_chars > 0:
            logger.info(f"Detected Traditional Chinese: chinese_ratio={chinese_ratio:.3f}, traditional_specific_chars={traditional_specific_chars}")
            return 'zh-tw'
        elif chinese_ratio == max_ratio:
            logger.info(f"Detected Simplified Chinese: chinese_ratio={chinese_ratio:.3f}")
            return 'zh'
        elif japanese_ratio == max_ratio:
            return 'ja'
        elif korean_ratio == max_ratio:
            return 'ko'
        elif arabic_ratio == max_ratio:
            return 'ar'
        elif cyrillic_ratio == max_ratio:
            return 'ru'
    
    # Default to English for Latin-based languages
    return 'en'

app = Flask(__name__)
CORS(app)

# Load OpenAPI specification
with open('openapi.json', 'r', encoding='utf-8') as f:
    openapi_spec = json.load(f)

class NaturalLanguageProcessor:
    """Processes natural language queries and converts them to API requests"""
    
    def __init__(self, openapi_spec: dict):
        self.openapi_spec = openapi_spec
        self.endpoints = self._parse_endpoints()
        
    def _parse_endpoints(self) -> Dict[str, dict]:
        """Parse OpenAPI endpoints and their parameters"""
        endpoints = {}
        for path, methods in self.openapi_spec.get('paths', {}).items():
            for method, details in methods.items():
                endpoint_key = f"{method.upper()} {path}"
                endpoints[endpoint_key] = {
                    'path': path,
                    'method': method.upper(),
                    'summary': details.get('summary', ''),
                    'description': details.get('description', ''),
                    'parameters': details.get('parameters', []),
                    'operationId': details.get('operationId', '')
                }
        return endpoints
    
    def process_query(self, query: str) -> Dict:
        """Process natural language query and return API request details"""
        query_lower = query.lower().strip()
        detected_language = detect_language(query)
        logger.info(f"Processing query: '{query}' (detected language: {detected_language})")
        
        # First try rule-based approach
        intent_result = self._extract_intent(query_lower)
        if intent_result:
            endpoint_key, extracted_params = intent_result
            endpoint_info = self.endpoints[endpoint_key]
            logger.info(f"Rule-based match found: {endpoint_key} with params: {extracted_params}")
            
            # Build API request
            api_request = self._build_api_request(endpoint_info, extracted_params)
            
            return {
                'endpoint': endpoint_key,
                'summary': endpoint_info['summary'],
                'api_request': api_request,
                'natural_language_query': query,
                'extracted_parameters': extracted_params,
                'processing_method': 'rule_based',
                'detected_language': detected_language
            }
        
        # If rule-based approach fails, try OpenAI
        logger.info("Rule-based parsing failed, trying AI...")
        ai_result = openai_parser.parse_query(query, detected_language)
        
        if ai_result:
            endpoint_key = ai_result['endpoint']
            extracted_params = ai_result['parameters']
            logger.info(f"OpenAI match found: {endpoint_key} with params: {extracted_params}")
            
            # Find endpoint info
            endpoint_info = None
            for key, info in self.endpoints.items():
                if key == endpoint_key:
                    endpoint_info = info
                    break
            
            if endpoint_info:
                # Build API request
                api_request = self._build_api_request(endpoint_info, extracted_params)
                
                return {
                    'endpoint': endpoint_key,
                    'summary': endpoint_info['summary'],
                    'api_request': api_request,
                    'natural_language_query': query,
                    'extracted_parameters': extracted_params,
                    'processing_method': 'openai',
                    'confidence': ai_result.get('confidence', 0.8),
                    'detected_language': detected_language
                }
        
        # If both methods fail
        logger.warning(f"Both rule-based and OpenAI parsing failed for query: '{query}'")
        return {
            'error': 'Could not understand the query. Please try rephrasing your request.',
            'suggestions': self._get_suggestion_queries(),
            'processing_method': 'failed'
        }
    
    def _extract_intent(self, query: str) -> Optional[Tuple[str, Dict]]:
        """Extract intent and parameters from natural language query"""
        
        # User-related queries
        if any(keyword in query for keyword in ['user', 'users', 'risky user', 'anomalous user']):
            if 'summary' in query or 'describe' in query or 'details' in query:
                user_id = self._extract_user_id(query)
                if user_id:
                    return f"GET /threats/users/{{user_id}}/summary/", {
                        'user_id': user_id,
                        'date[eq]': self._extract_date(query)
                    }
            else:
                return "GET /threats/users/", {
                    'limit': self._extract_limit(query, default=10),
                    'date[eq]': self._extract_date(query)
                }
        
        # Device-related queries
        elif any(keyword in query for keyword in ['device', 'devices', 'risky device', 'anomalous device']):
            if 'summary' in query or 'describe' in query or 'details' in query:
                device_id = self._extract_device_id(query)
                if device_id:
                    return f"GET /threats/devices/{{device_id}}/summary/", {
                        'device_id': device_id,
                        'date[eq]': self._extract_date(query)
                    }
            else:
                return "GET /threats/devices/", {
                    'limit': self._extract_limit(query, default=10),
                    'date[eq]': self._extract_date(query)
                }
        
        # Rare process queries
        elif any(keyword in query for keyword in ['rare process', 'process', 'processes', 'execution', 'executions']):
            if 'summary' in query or 'describe' in query or 'details' in query:
                alert_id = self._extract_alert_id(query)
                if alert_id:
                    return f"GET /threats/rare-processes/{{alert_id}}/summary/", {
                        'alert_id': alert_id
                    }
            else:
                return "GET /threats/rare-processes/", {
                    'limit': self._extract_limit(query, default=10),
                    'date[eq]': self._extract_date(query)
                }
        
        # Organization summary queries
        elif any(keyword in query for keyword in ['organization', 'org', 'company', 'overall', 'summary']):
            return "GET /threats/org/summary/", {
                'date[eq]': self._extract_date(query)
            }
        
        return None
    
    def _extract_user_id(self, query: str) -> Optional[str]:
        """Extract user ID from query"""
        # Look for patterns like "user123", "user 123", "user id 123"
        patterns = [
            r'user\s*(\w+)',
            r'user\s*id\s*(\w+)',
            r'user\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1)
        return None
    
    def _extract_device_id(self, query: str) -> Optional[str]:
        """Extract device ID from query"""
        patterns = [
            r'device\s*(\w+)',
            r'device\s*id\s*(\w+)',
            r'device\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1)
        return None
    
    def _extract_alert_id(self, query: str) -> Optional[str]:
        """Extract alert ID from query"""
        patterns = [
            r'alert\s*id\s*(\w+)',
            r'alert\s*(\d+)',
            r'id\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1)
        return None
    
    def _extract_limit(self, query: str, default: int = 10) -> int:
        """Extract limit parameter from query"""
        # Look for patterns like "top 5", "first 10", "5 most", etc.
        patterns = [
            r'top\s*(\d+)',
            r'first\s*(\d+)',
            r'(\d+)\s*most',
            r'(\d+)\s*risky',
            r'(\d+)\s*anomalous',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                limit = int(match.group(1))
                return min(limit, 100)  # API maximum is 100
        
        return default
    
    def _extract_date(self, query: str) -> Optional[str]:
        """Extract date from query"""
        # Look for date patterns like "2024-09-03", "on 2024-09-03", etc.
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        match = re.search(date_pattern, query)
        
        if match:
            return match.group(1)
        
        # Look for relative dates like "yesterday", "last week", etc.
        if 'yesterday' in query:
            yesterday = date.today() - timedelta(days=1)
            return yesterday.strftime('%Y-%m-%d')
        
        return None
    
    def _build_api_request(self, endpoint_info: dict, params: dict) -> dict:
        """Build API request structure"""
        path = endpoint_info['path']
        logger.info(f"Building API request for endpoint: {path}")
        
        # Remove trailing slash if present
        if path.endswith('/'):
            path = path[:-1]
            logger.info(f"Removed trailing slash, new path: {path}")
        
        # Replace path parameters
        for param_name, param_value in params.items():
            if f'{{{param_name}}}' in path:
                path = path.replace(f'{{{param_name}}}', str(param_value))
                logger.info(f"Replaced path parameter {param_name} with {param_value}")
        
        # Separate query parameters
        query_params = {}
        path_params = {}
        
        for param_name, param_value in params.items():
            if f'{{{param_name}}}' in endpoint_info['path']:
                path_params[param_name] = param_value
            else:
                query_params[param_name] = param_value
        
        api_request = {
            'method': endpoint_info['method'],
            'url': path,
            'query_params': query_params,
            'path_params': path_params,
            'headers': Config.get_headers(),
            'base_url': Config.API_BASE_URL
        }
        
        logger.info(f"Final API request: {api_request}")
        return api_request
    
    def _get_suggestion_queries(self) -> List[str]:
        """Get example queries for user guidance"""
        return [
            "Show me the most risky users",
            "List the top 5 risky devices",
            "What were the user threats on 2024-09-03?",
            "Describe risky user user123",
            "Show me the organization's security summary",
            "List the most risky rare process executions"
        ]

class OpenAIParser:
    """OpenAI-powered natural language query parser"""
    
    def __init__(self, openapi_spec: dict):
        self.openapi_spec = openapi_spec
        self.endpoints = self._parse_endpoints()
        
    def _parse_endpoints(self) -> Dict[str, dict]:
        """Parse OpenAPI endpoints for AI context"""
        endpoints = {}
        for path, methods in self.openapi_spec.get('paths', {}).items():
            for method, details in methods.items():
                endpoint_key = f"{method.upper()} {path}"
                endpoints[endpoint_key] = {
                    'path': path,
                    'method': method.upper(),
                    'summary': details.get('summary', ''),
                    'description': details.get('description', ''),
                    'parameters': details.get('parameters', [])
                }
        return endpoints
    
    def parse_query(self, query: str, detected_language: str = 'en') -> Optional[Dict]:
        """Use OpenAI to parse natural language query"""
        if not Config.OPENAI_API_KEY:
            logger.warning("AI API key not configured")
            return None
            
        try:
            logger.info(f"AI parsing query: '{query}' (language: {detected_language})")
            logger.info(f"AI API Key configured: {bool(Config.OPENAI_API_KEY)}")
            logger.info(f"AI Model: {Config.OPENAI_MODEL}")
            logger.info(f"AI Base URL: {Config.OPENAI_BASE_URL}")
            
            # Create context for the AI
            endpoints_context = []
            for endpoint_key, info in self.endpoints.items():
                endpoints_context.append(f"- {endpoint_key}: {info['summary']}")
                if info['description']:
                    endpoints_context.append(f"  Description: {info['description']}")
                if info['parameters']:
                    params = [f"{p['name']} ({p.get('schema', {}).get('type', 'string')})" for p in info['parameters']]
                    endpoints_context.append(f"  Parameters: {', '.join(params)}")
                endpoints_context.append("")
            
            # Generate language-specific prompt
            if detected_language == 'zh-tw':
                prompt = f"""您是一個威脅偵測和回應系統的API查詢解析器。
將自然語言查詢轉換為結構化的API請求。

可用的API端點:
{chr(10).join(endpoints_context)}

查詢: "{query}"

規則:
1. 根據查詢識別最合適的端點
2. 從查詢中提取參數 (user_id, device_id, alert_id, limit, date, 等)
3. 返回具有以下結構的JSON物件:
{{
    "endpoint": "METHOD /path",
    "parameters": {{
        "param_name": "value"
    }},
    "confidence": 0.95
}}

參數提取規則:
- 對於有ID的使用者查詢: 從 "user123", "user 123" 等模式中提取 user_id
- 對於有ID的裝置查詢: 從 "device123", "device 123" 等模式中提取 device_id  
- 對於有ID的警報查詢: 從 "alert 123", "id 123" 等模式中提取 alert_id
- 對於限制: 從 "top 5", "first 10", "5 most" 等中提取數字
- 對於日期: 提取 YYYY-MM-DD 格式的日期
- 對於摘要查詢: 尋找 "describe", "summary", "details", "explain" 等詞彙

只返回有效的JSON，不要額外的文字。"""
            elif detected_language == 'zh':
                prompt = f"""你是一个威胁检测和响应系统的API查询解析器。
将自然语言查询转换为结构化的API请求。

可用的API端点:
{chr(10).join(endpoints_context)}

查询: "{query}"

规则:
1. 根据查询识别最合适的端点
2. 从查询中提取参数 (user_id, device_id, alert_id, limit, date, 等)
3. 返回具有以下结构的JSON对象:
{{
    "endpoint": "METHOD /path",
    "parameters": {{
        "param_name": "value"
    }},
    "confidence": 0.95
}}

参数提取规则:
- 对于有ID的用户查询: 从 "user123", "user 123" 等模式中提取 user_id
- 对于有ID的设备查询: 从 "device123", "device 123" 等模式中提取 device_id  
- 对于有ID的警报查询: 从 "alert 123", "id 123" 等模式中提取 alert_id
- 对于限制: 从 "top 5", "first 10", "5 most" 等中提取数字
- 对于日期: 提取 YYYY-MM-DD 格式的日期
- 对于摘要查询: 寻找 "describe", "summary", "details", "explain" 等词汇

只返回有效的JSON，不要额外的文字。"""
            else:
                prompt = f"""You are an API query parser for a Threat Detection and Response system. 
Convert the natural language query into a structured API request.

Available API endpoints:
{chr(10).join(endpoints_context)}

Query: "{query}"

Rules:
1. Identify the most appropriate endpoint based on the query
2. Extract parameters from the query (user_id, device_id, alert_id, limit, date, etc.)
3. Return a JSON object with the following structure:
{{
    "endpoint": "METHOD /path",
    "parameters": {{
        "param_name": "value"
    }},
    "confidence": 0.95
}}

Parameter extraction rules:
- For user queries with IDs: extract user_id from patterns like "user123", "user 123"
- For device queries with IDs: extract device_id from patterns like "device123", "device 123"  
- For alert queries with IDs: extract alert_id from patterns like "alert 123", "id 123"
- For limits: extract numbers from "top 5", "first 10", "5 most", etc.
- For dates: extract dates in YYYY-MM-DD format
- For summary queries: look for words like "describe", "summary", "details", "explain"

Return only valid JSON, no additional text."""

            # Generate language-specific system prompt
            if detected_language == 'zh-tw':
                system_prompt = "您是一個有用的API查詢解析器。總是返回有效的JSON。"
            elif detected_language == 'zh':
                system_prompt = "你是一个有用的API查询解析器。总是返回有效的JSON。"
            else:
                system_prompt = "You are a helpful API query parser. Always return valid JSON."
            
            # Prepare headers for OpenRouter (optional but recommended)
            extra_headers = {
                "HTTP-Referer": "https://github.com/yourusername/tdr-agent",  # Optional: Your app URL
                "X-Title": "TDR Agent"  # Optional: Your app name
            }
            
            # Create OpenAI client with OpenRouter base URL and headers
            client = openai.OpenAI(
                api_key=Config.OPENAI_API_KEY,
                base_url=Config.OPENAI_BASE_URL,
                default_headers=extra_headers
            )
            
            response = client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result_text = response.choices[0].message.content.strip()
            logger.info(f"AI response: {result_text}")
            
            # Parse JSON response
            result = json.loads(result_text)
            logger.info(f"Parsed AI result: {result}")
            
            # Validate the result
            if 'endpoint' not in result or 'parameters' not in result:
                logger.error("Invalid AI response structure")
                return None
                
            logger.info(f"AI parsing successful: {result['endpoint']} with params: {result['parameters']}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI JSON response: {e}")
            return None
        except Exception as e:
            logger.error(f"AI API error: {e}")
            return None

# Initialize the processors
nlp = NaturalLanguageProcessor(openapi_spec)
openai_parser = OpenAIParser(openapi_spec)

# Configuration file path
CONFIG_FILE = 'tdr_config.json'

def save_config_to_file(config_data):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
        logger.info(f"Configuration saved to {CONFIG_FILE}")
        return True
    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")
        return False

def load_config_from_file():
    """Load configuration from file"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            logger.info(f"Configuration loaded from {CONFIG_FILE}")
            return config_data
        else:
            logger.info(f"Configuration file {CONFIG_FILE} not found, using defaults")
            return None
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return None

# Load configuration on startup
saved_config = load_config_from_file()
if saved_config:
    # Support both old (openai_*) and new (openrouter_*) parameter names for backward compatibility
    openrouter_api_key = saved_config.get('openrouter_api_key') or saved_config.get('openai_api_key', Config.OPENAI_API_KEY)
    openrouter_model = saved_config.get('openrouter_model') or saved_config.get('openai_model', Config.OPENAI_MODEL)
    openrouter_base_url = saved_config.get('openrouter_base_url') or saved_config.get('openai_base_url', Config.OPENAI_BASE_URL)
    
    Config.update_config(
        saved_config.get('hostname', Config.HOSTNAME),
        saved_config.get('api_token', Config.API_TOKEN),
        openrouter_api_key,
        saved_config.get('ai_provider', Config.AI_PROVIDER),
        openrouter_model,
        openrouter_base_url
    )

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/debug')
def debug():
    """Serve the debug page"""
    return render_template('debug.html')

@app.route('/debug-ui')
def debug_ui():
    """Serve the debug UI page"""
    return render_template('index_debug.html')

@app.route('/simple')
def simple():
    """Serve the simple test page"""
    return render_template('simple.html')

@app.route('/connection-test')
def connection_test():
    """Serve the connection test page"""
    return render_template('connection_test.html')

@app.route('/proxy-test')
def proxy_test():
    """Serve the proxy test page"""
    return render_template('proxy_test.html')

@app.route('/api/query', methods=['POST'])
def process_natural_language_query():
    """Process natural language query and return API request details"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        logger.info(f"Processing query: {query}")
        
        result = nlp.process_query(query)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/endpoints', methods=['GET'])
def get_endpoints():
    """Get available API endpoints"""
    endpoints = []
    for endpoint_key, info in nlp.endpoints.items():
        endpoints.append({
            'key': endpoint_key,
            'path': info['path'],
            'method': info['method'],
            'summary': info['summary'],
            'description': info['description']
        })
    
    return jsonify(endpoints)

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Get example queries"""
    return jsonify({
        'suggestions': nlp._get_suggestion_queries()
    })

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify(Config.get_config_dict())

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        data = request.get_json()
        hostname = data.get('hostname', '').strip()
        api_token = data.get('api_token', '').strip()
        # Support both old (openai_*) and new (openrouter_*) parameter names for backward compatibility
        openrouter_api_key = data.get('openrouter_api_key', '').strip() or data.get('openai_api_key', '').strip()
        ai_provider = data.get('ai_provider', 'deepseek').strip()
        openrouter_model = data.get('openrouter_model', '').strip() or data.get('openai_model', 'deepseek/deepseek-chat').strip()
        openrouter_base_url = data.get('openrouter_base_url', '').strip() or data.get('openai_base_url', 'https://openrouter.ai/api/v1').strip()
        
        if not hostname:
            return jsonify({'error': 'Hostname is required'}), 400
        
        # Validate and fix model format based on provider
        if ai_provider == 'openai':
            # Ensure OpenAI models start with 'openai/'
            if not openrouter_model.startswith('openai/'):
                # Try to fix old format (e.g., 'gpt-4o-mini' -> 'openai/gpt-4o-mini')
                if openrouter_model.startswith('gpt-'):
                    openrouter_model = f'openai/{openrouter_model}'
                    logger.info(f"Fixed OpenAI model format: {openrouter_model}")
                else:
                    # Default to OpenAI model
                    openrouter_model = 'openai/gpt-4o-mini'
                    logger.warning(f"Invalid OpenAI model format, using default: {openrouter_model}")
        elif ai_provider == 'deepseek':
            # Ensure DeepSeek models start with 'deepseek/'
            if not openrouter_model.startswith('deepseek/'):
                # Default to DeepSeek model
                openrouter_model = 'deepseek/deepseek-chat'
                logger.warning(f"Invalid DeepSeek model format, using default: {openrouter_model}")
        
        Config.update_config(hostname, api_token, openrouter_api_key, ai_provider, openrouter_model, openrouter_base_url)
        
        # Save configuration to file
        config_data = Config.get_config_dict()
        save_success = save_config_to_file(config_data)
        
        logger.info(f"Configuration updated: hostname={hostname}, api_token={'***' if api_token else 'None'}, openrouter_key={'***' if openrouter_api_key else 'None'}")
        
        return jsonify({
            'message': 'Configuration updated successfully' + (' and saved to file' if save_success else ' (but failed to save to file)'),
            'config': config_data,
            'saved_to_file': save_success
        })
    
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/proxy/<path:api_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_api_request(api_path):
    """Proxy API requests to bypass CORS issues"""
    try:
        # Build the full API URL
        api_url = f"{Config.API_BASE_URL}/{api_path}"
        logger.info(f"Building API URL: {api_url}")
        
        # Get query parameters from the request
        query_params = request.args
        
        # Add query parameters to URL
        if query_params:
            param_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
            api_url += f"?{param_string}"
        
        logger.info(f"Proxying request to: {api_url}")
        
        # Prepare headers
        headers = {
            'X-API-KEY': Config.API_TOKEN,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Prepare request options
        request_options = {
            'headers': headers,
            'timeout': 30
        }
        
        # Add body for non-GET requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            request_options['data'] = request.get_data()
        
        # Make the request
        response = requests.request(
            method=request.method,
            url=api_url,
            **request_options
        )
        
        logger.info(f"API response status: {response.status_code}")
        
        # Return the response
        return response.content, response.status_code, dict(response.headers)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Proxy request failed: {str(e)}")
        return jsonify({'error': f'Proxy request failed: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Proxy error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/ai-explain', methods=['POST'])
def ai_explain_response():
    """Use AI to explain API response in natural language"""
    try:
        logger.info("=== AI EXPLAIN ENDPOINT CALLED ===")
        data = request.get_json()
        logger.info(f"Received data keys: {list(data.keys()) if data else 'None'}")
        
        prompt = data.get('prompt')
        response_data = data.get('responseData')
        api_request = data.get('apiRequest')
        detected_language = data.get('detected_language', 'en')
        
        logger.info(f"Prompt length: {len(prompt) if prompt else 0}")
        logger.info(f"Response data type: {type(response_data)}")
        logger.info(f"API request: {api_request}")
        
        if not prompt:
            logger.error("No prompt provided")
            return jsonify({'error': 'No prompt provided'}), 400
        
        logger.info(f"Processing AI explanation for {api_request.get('method', 'GET')} {api_request.get('url', 'unknown')}")
        logger.info(f"Detected language: {detected_language}")
        logger.info(f"AI API Key configured: {bool(Config.OPENAI_API_KEY)}")
        logger.info(f"AI Model: {Config.OPENAI_MODEL}")
        logger.info(f"AI Base URL: {Config.OPENAI_BASE_URL}")
        
        # Modify prompt based on detected language
        language_prompts = {
            'zh': "你是一名网络安全分析师，专门解释威胁检测和响应(TDR)数据。请提供清晰、专业的安全数据解释，帮助安全管理人员理解威胁并采取适当的行动。请用简体中文回答。",
            'zh-tw': "您是一名網路安全分析師，專門解釋威脅偵測和回應(TDR)資料。請提供清晰、專業的安全資料解釋，幫助安全管理人員理解威脅並採取適當的行動。請用繁體中文回答。",
            'ja': "あなたは脅威検出および対応（TDR）データを説明する専門のサイバーセキュリティアナリストです。セキュリティ管理者が脅威を理解し、適切な行動を取れるよう、明確で専門的なセキュリティデータの説明を提供してください。日本語で回答してください。",
            'ko': "당신은 위협 탐지 및 대응(TDR) 데이터를 설명하는 전문 사이버보안 분석가입니다. 보안 관리자가 위협을 이해하고 적절한 조치를 취할 수 있도록 명확하고 전문적인 보안 데이터 설명을 제공해 주세요. 한국어로 답변해 주세요.",
            'ar': "أنت محلل أمن سيبراني متخصص في شرح بيانات اكتشاف التهديدات والاستجابة (TDR). قدم شرحًا واضحًا ومهنيًا لبيانات الأمان لمساعدة مدراء الأمن على فهم التهديدات واتخاذ الإجراءات المناسبة. أجب باللغة العربية.",
            'ru': "Вы эксперт-аналитик по кибербезопасности, специализирующийся на объяснении данных обнаружения и реагирования на угрозы (TDR). Предоставляйте четкие, профессиональные объяснения данных безопасности, чтобы помочь менеджерам по безопасности понять угрозы и принять соответствующие меры. Отвечайте на русском языке.",
            'en': "You are a cybersecurity analyst expert in threat detection and response. Provide clear, professional explanations of security data that help security managers understand threats and take appropriate action."
        }
        
        system_prompt = language_prompts.get(detected_language, language_prompts['en'])
        
        # Use OpenAI/OpenRouter to generate explanation
        try:
            logger.info("Creating AI client...")
            logger.info(f"Using base URL: {Config.OPENAI_BASE_URL}")
            
            # Prepare headers for OpenRouter (optional but recommended)
            extra_headers = {
                "HTTP-Referer": "https://github.com/yourusername/tdr-agent",  # Optional: Your app URL
                "X-Title": "TDR Agent"  # Optional: Your app name
            }
            
            client = openai.OpenAI(
                api_key=Config.OPENAI_API_KEY,
                base_url=Config.OPENAI_BASE_URL,
                default_headers=extra_headers
            )
            
            logger.info("Sending request to AI service...")
            logger.info(f"Request prompt preview: {prompt[:200]}...")
            
            response = client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            explanation = response.choices[0].message.content
            logger.info("AI explanation generated successfully")
            logger.info(f"Explanation length: {len(explanation)} characters")
            logger.info(f"Explanation preview: {explanation[:200]}...")
            
            result = {
                'explanation': explanation,
                'success': True
            }
            logger.info(f"Returning result: {result}")
            return jsonify(result)
            
        except Exception as ai_error:
            logger.error(f"AI API error: {str(ai_error)}")
            logger.error(f"AI error type: {type(ai_error)}")
            return jsonify({
                'error': f'AI processing failed: {str(ai_error)}',
                'success': False
            }), 500
            
    except Exception as e:
        logger.error(f"AI explain endpoint error: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/test-ai')
def test_ai():
    """Test AI configuration and connectivity"""
    try:
        logger.info("=== AI TEST ENDPOINT CALLED ===")
        
        # Check configuration
        has_api_key = bool(Config.OPENAI_API_KEY)
        model = Config.OPENAI_MODEL
        base_url = Config.OPENAI_BASE_URL
        
        logger.info(f"AI API Key configured: {has_api_key}")
        logger.info(f"AI Model: {model}")
        logger.info(f"AI Base URL: {base_url}")
        
        if not has_api_key:
            return jsonify({
                'error': 'AI API key not configured',
                'has_api_key': False,
                'model': model,
                'base_url': base_url
            }), 400
        
        # Test AI connection (OpenRouter/OpenAI)
        try:
            logger.info(f"Using base URL: {Config.OPENAI_BASE_URL}")
            
            # Prepare headers for OpenRouter (optional but recommended)
            extra_headers = {
                "HTTP-Referer": "https://github.com/yourusername/tdr-agent",  # Optional: Your app URL
                "X-Title": "TDR Agent"  # Optional: Your app name
            }
            
            client = openai.OpenAI(
                api_key=Config.OPENAI_API_KEY,
                base_url=Config.OPENAI_BASE_URL,
                default_headers=extra_headers
            )
            
            response = client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant."
                    },
                    {
                        "role": "user",
                        "content": "Say 'AI test successful' and nothing else."
                    }
                ]
            )
            
            result = response.choices[0].message.content
            logger.info(f"AI test successful: {result}")
            
            return jsonify({
                'success': True,
                'has_api_key': True,
                'model': model,
                'base_url': base_url,
                'test_response': result,
                'message': 'AI configuration and connectivity test successful'
            })
            
        except Exception as ai_error:
            logger.error(f"AI test failed: {str(ai_error)}")
            return jsonify({
                'error': f'AI test failed: {str(ai_error)}',
                'has_api_key': True,
                'model': model,
                'base_url': base_url,
                'success': False
            }), 500
            
    except Exception as e:
        logger.error(f"AI test endpoint error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/test-proxy')
def test_proxy():
    """Test proxy functionality"""
    try:
        test_url = f"{Config.API_BASE_URL}/threats/users"
        logger.info(f"Testing proxy with URL: {test_url}")
        
        headers = {
            'X-API-KEY': Config.API_TOKEN,
            'Accept': 'application/json'
        }
        
        response = requests.get(test_url, headers=headers, timeout=10)
        logger.info(f"Test response status: {response.status_code}")
        
        return jsonify({
            'message': 'Proxy test successful',
            'status': response.status_code,
            'url': test_url,
            'response_preview': response.text[:200] if response.text else 'No response body'
        })
        
    except Exception as e:
        logger.error(f"Proxy test failed: {str(e)}")
        return jsonify({
            'error': f'Proxy test failed: {str(e)}',
            'url': f"{Config.API_BASE_URL}/threats/users"
        }), 500

if __name__ == '__main__':
    # Fix for Windows socket error
    import os
    if os.name == 'nt':  # Windows
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    else:  # Unix/Linux/Mac
        app.run(debug=True, host='0.0.0.0', port=5000)
