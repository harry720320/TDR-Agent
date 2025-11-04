# TDR Agent - Natural Language API Query Interface

A web application that converts natural language queries into API requests based on the OpenText Core Threat Detection and Response API specification.

## Features

- **Hybrid Natural Language Processing**: 
  - Rule-based parsing for common queries (fast and free)
  - OpenAI API integration for complex queries (powerful and flexible)
- **AI-Powered Response Analysis**: Intelligent explanation of API responses in natural language
- **Interactive Web Interface**: Modern, responsive UI built with React and Tailwind CSS
- **Real-time Query Processing**: Instant feedback and API request generation
- **Multiple Query Types**: Support for user threats, device threats, rare processes, and organization summaries
- **Parameter Extraction**: Automatically extracts dates, limits, IDs, and other parameters from queries
- **Example Queries**: Built-in suggestions to help users understand the system capabilities
- **Real-time API Testing**: Send generated API requests directly from the UI
- **Persistent Configuration**: Settings are saved to file and restored on restart
- **Processing Method Indicators**: Shows whether queries were processed by rules or AI
- **CORS Proxy**: Built-in proxy to bypass browser CORS restrictions

## Supported Query Types

### User Threats
- "Show me the most risky users"
- "List the top 5 risky users"
- "What were the user threats on 2024-09-03?"
- "Describe risky user user123"

### Device Threats
- "Which devices are risky?"
- "Show me the most anomalous devices"
- "Describe risky device device123"

### Rare Process Executions
- "List the most risky rare process executions"
- "Show me the rare processes from yesterday"
- "Describe rare process execution 98765432"

### Organization Summary
- "What is the organization's security risk?"
- "Show me the organization summary"
- "Describe the overall security situation"

## 🤖 AI-Powered Response Analysis

The application now includes intelligent response analysis that converts raw API responses into clear, natural language explanations:

### Features:
- **Security Analysis**: AI analyzes threat data and provides professional security insights
- **Risk Assessment**: Explains threat severity levels and risk scores
- **Actionable Recommendations**: Suggests specific security actions to take
- **Non-Technical Language**: Converts technical data into manager-friendly explanations

### Example AI Analysis:
Instead of showing raw JSON data, the AI provides explanations like:
- "**Summary**: Your organization has 3 high-risk users with suspicious login patterns..."
- "**Key Findings**: User 'john.doe@company.com' has a risk score of 85/100 due to..."
- "**Recommendations**: Immediately investigate the anomalous login attempts from..."

### Configuration:
The AI analysis uses your configured OpenAI API key and model. Make sure to set these in the configuration panel for the best experience. The default model is GPT-5 Mini, which provides fast and efficient analysis.

**Supported Models:**
- GPT-5 Mini (default) - Fast and efficient
- GPT-4o - Latest multimodal model
- GPT-4o Mini - Compact version of GPT-4o
- GPT-4 Turbo - High-performance model
- GPT-3.5 Turbo - Legacy model

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the API settings** (choose one method):

   **Method 1: Environment Variables**
   ```bash
   # Set environment variables
   export TDR_HOSTNAME="api.example.com:8080"
   export TDR_API_TOKEN="your_api_token_here"
   export OPENAI_API_KEY="sk-your_openai_key_here"  # Optional
   export OPENAI_MODEL="gpt-3.5-turbo"  # Optional
   ```
   
   **Note**: The application uses HTTPS by default. If you need HTTP, specify the full URL (e.g., `http://api.example.com:8080`)

   **Method 2: Web Interface**
   - Start the application first
   - Click the gear icon (⚙️) in the top-right corner
   - Enter your API hostname, token, and OpenAI settings

   **Method 3: Edit config.py directly**
   ```python
   DEFAULT_HOSTNAME = "your-api-server.com:8080"
   DEFAULT_API_TOKEN = "your_api_token_here"
   DEFAULT_OPENAI_API_KEY = "sk-your_openai_key_here"  # Optional
   DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"  # Optional
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

   **Windows Users**: If you encounter socket errors, use the Windows-specific launcher:
   ```bash
   start_windows.bat
   ```

5. **Open your browser** and navigate to `http://127.0.0.1:5000` (Windows) or `http://localhost:5000` (Unix/Linux/Mac)

## API Endpoints

The application provides the following API endpoints:

- `GET /` - Main web interface
- `POST /api/query` - Process natural language queries
- `GET /api/endpoints` - Get available API endpoints
- `GET /api/suggestions` - Get example queries
- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration

## Usage Examples

### Basic Queries
```
"Show me the most risky users"
"List the top 10 devices with security threats"
"What was the organization's security risk yesterday?"
```

### Queries with Parameters
```
"Show me the top 5 risky users from 2024-09-03"
"Describe user user123"
"What were the device threats on 2024-11-12?"
```

### Complex Queries
```
"Which are the 8 most anomalous devices?"
"List the rare process executions with highest risk scores"
"Provide a summary of risky device device456"
```

### AI-Powered Queries
```
"I'm concerned about potential insider threats, can you help me investigate?"
"What unusual activities happened around the time of the security incident?"
"Show me users who might be compromised based on their recent behavior patterns"
```

## API Testing

After generating an API request, you can:

1. **Send the Request**: Click the "Send Request" button to execute the API call
2. **View Response**: See the full response including status, headers, and data
3. **Copy Request**: Use the copy button to copy the request for external use

The API testing feature allows you to:
- Test your configuration settings
- Verify API connectivity
- Debug request/response issues
- See actual data from your TDR system

## Technical Details

### Backend (Flask)
- **Natural Language Processing**: Custom implementation that parses queries and extracts intent
- **Parameter Extraction**: Regex-based extraction of dates, limits, IDs, and other parameters
- **API Request Generation**: Converts extracted parameters into structured API requests
- **Error Handling**: Comprehensive error handling with helpful suggestions

### Frontend (React)
- **Modern UI**: Built with React 18 and Tailwind CSS
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Feedback**: Instant query processing and result display
- **Interactive Elements**: Clickable suggestions and copy-to-clipboard functionality

### Supported Parameters
- **limit**: Number of results to return (1-100)
- **date[eq]**: Specific date for historical queries (YYYY-MM-DD format)
- **user_id**: Unique identifier for users
- **device_id**: Unique identifier for devices
- **alert_id**: Unique identifier for rare process alerts

## Configuration

### API Settings

The application requires configuration of the target API hostname and authentication token:

- **Hostname**: The hostname or IP address of your TDR API server (include port if needed)
- **API Token**: Authentication token that will be sent in the `X-API-KEY` header
- **OpenAI API Key** (Optional): For processing complex queries that don't match predefined patterns
- **OpenAI Model** (Optional): Choose between GPT-3.5 Turbo, GPT-4, or GPT-4 Turbo

**Protocol**: The application uses HTTPS by default for security. If your API server only supports HTTP, specify the full URL including the protocol (e.g., `http://api.example.com:8080`).

### Configuration Methods

1. **Environment Variables** (Recommended for production):
   ```bash
   export TDR_HOSTNAME="api.example.com:8080"
   export TDR_API_TOKEN="your_api_token_here"
   ```

2. **Web Interface** (Easy setup):
   - Click the gear icon (⚙️) in the application header
   - Enter your hostname, token, and OpenAI settings
   - Click Save (settings are automatically saved to `tdr_config.json`)

3. **Direct Configuration** (For development):
   - Edit `config.py` and update the `DEFAULT_HOSTNAME`, `DEFAULT_API_TOKEN`, and OpenAI settings

### How the Hybrid System Works

The application uses a two-tier approach for processing natural language queries:

1. **Rule-based Processing** (First Priority):
   - Fast, free, and works offline
   - Handles common query patterns like "show me risky users", "describe user123"
   - Uses regex patterns and keyword matching
   - Shows green "Rule-based" indicator

2. **AI-powered Processing** (Fallback):
   - Used when rule-based processing fails
   - Powered by OpenAI's language models
   - Handles complex, ambiguous, or creative queries
   - Shows purple "AI-powered" indicator with confidence score
   - Requires OpenAI API key and internet connection

**Examples of queries that trigger AI processing:**
- "I'm concerned about potential insider threats, can you help me investigate?"
- "What unusual activities happened around the time of the security incident?"
- "Show me users who might be compromised based on their recent behavior patterns"

## File Structure

```
TDR Agent/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── openapi.json          # OpenAPI specification
├── requirements.txt      # Python dependencies
├── env.example          # Environment variables example
├── tdr_config.json     # Saved configuration (auto-generated)
├── README.md            # This file
└── templates/
    ├── index.html       # Main React frontend
    ├── debug.html       # Debug page
    ├── simple.html      # Simple test page
    └── index_debug.html # Debug UI page
```

## Development

To modify or extend the application:

1. **Add new query patterns** in the `_extract_intent` method of `NaturalLanguageProcessor`
2. **Modify parameter extraction** in the respective `_extract_*` methods
3. **Update the UI** by modifying the React components in `templates/index.html`
4. **Add new API endpoints** by updating the OpenAPI specification and corresponding processing logic

## Error Handling

The application provides helpful error messages and suggestions when:
- Queries cannot be understood
- Required parameters are missing
- Invalid parameter values are provided
- API requests fail

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### Windows Socket Errors

If you encounter `OSError: [WinError 10038] An operation was attempted on something that is not a socket`:

1. **Use the Windows launcher**:
   ```bash
   start_windows.bat
   ```

2. **Check port availability**:
   ```bash
   netstat -ano | findstr :5000
   ```

3. **Kill conflicting processes**:
   ```bash
   taskkill /PID <process_id> /F
   ```

4. **Change the port** in `app.py`:
   ```python
   app.run(debug=True, host='127.0.0.1', port=5001)  # Use different port
   ```

### Common Issues

- **Port already in use**: Change port or kill the conflicting process
- **OpenAI API errors**: Check your API key and internet connection
- **Module not found**: Run `pip install -r requirements.txt`
- **Permission denied**: Run as administrator (Windows) or use `sudo` (Unix)

## License

This project is provided as-is for educational and demonstration purposes.
