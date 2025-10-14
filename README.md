# Code Review Assistant

An automated code analysis system that provides LLM-powered code reviews through a REST API. Upload source code files and receive structured feedback on code quality, security vulnerabilities, performance issues, and best practices.

## Features

- **Multi-language Support**: Analyze Python, JavaScript, TypeScript, Java, Go, C++, C, Ruby, and PHP files
- **LLM-Powered Analysis**: Uses Google Gemini or OpenAI GPT models for intelligent code review
- **Security Focus**: Detects vulnerabilities, secrets, and security anti-patterns
- **Structured Reports**: JSON responses with categorized issues and actionable recommendations
- **File Upload**: Single files or ZIP archives with multiple source files
- **REST API**: Full API for CI/CD integration and automation
- **Web Dashboard**: Interactive interface for file upload and report viewing
- **Rate Limiting**: Built-in protection with configurable limits
- **Authentication**: API key-based authentication system

## Quick Start

### Prerequisites

- Python 3.11+
- LLM API key (Google Gemini or OpenAI)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd code-review-assistant
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:

**Option A: Interactive setup (recommended)**
```bash
python setup_env.py
```

**Option B: Manual setup**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Docker Setup

1. Build the Docker image:
```bash
docker build -t code-review-assistant .
```

2. Run the container:
```bash
docker run -p 8000:8000 --env-file .env code-review-assistant
```

## API Documentation

### Interactive Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Endpoints

#### Authentication

All API endpoints require authentication via API key in the `X-API-Key` header.

**Create API Key**
```bash
curl -X POST "http://localhost:8000/api/auth/api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "rate_limit_tier": "standard"
  }'
```

Response:
```json
{
  "api_key": "cr_1234567890abcdef",
  "user_id": "uuid-here",
  "rate_limit_tier": "standard",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Code Review

**Upload File for Review**
```bash
curl -X POST "http://localhost:8000/api/review" \
  -H "X-API-Key: your_api_key_here" \
  -F "file=@example.py" \
  -F "language=python"
```

Response:
```json
{
  "report_id": "uuid-here",
  "status": "completed",
  "filename": "example.py",
  "language": "python",
  "estimated_time": null
}
```

**Get Report by ID**
```bash
curl -X GET "http://localhost:8000/api/review/{report_id}" \
  -H "X-API-Key: your_api_key_here"
```

Response:
```json
{
  "report_id": "uuid-here",
  "filename": "example.py",
  "language": "python",
  "file_size": 1024,
  "status": "completed",
  "summary": "Code analysis summary...",
  "issues": [
    {
      "id": "issue-uuid",
      "type": "security",
      "severity": "high",
      "line": 15,
      "message": "Potential SQL injection vulnerability",
      "suggestion": "Use parameterized queries",
      "code_snippet": "cursor.execute(f\"SELECT * FROM users WHERE id = {user_id}\")",
      "confidence": 0.95
    }
  ],
  "recommendations": [
    {
      "area": "security",
      "message": "Implement input validation",
      "impact": "high",
      "effort": "medium",
      "examples": ["Use SQLAlchemy ORM", "Validate user inputs"]
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:00:05Z",
  "processing_time_ms": 5000
}
```

**List Reports**
```bash
curl -X GET "http://localhost:8000/api/reviews?page=1&limit=10&language=python" \
  -H "X-API-Key: your_api_key_here"
```

Response:
```json
{
  "reports": [
    {
      "report_id": "uuid-here",
      "filename": "example.py",
      "language": "python",
      "status": "completed",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10,
  "total_pages": 1
}
```

**Delete Report**
```bash
curl -X DELETE "http://localhost:8000/api/review/{report_id}" \
  -H "X-API-Key: your_api_key_here"
```

#### System Information

**Get System Limits**
```bash
curl -X GET "http://localhost:8000/api/limits"
```

Response:
```json
{
  "max_file_size_mb": 10,
  "supported_languages": ["python", "javascript", "typescript", "java", "go", "cpp", "c", "ruby", "php"],
  "supported_extensions": [".py", ".js", ".ts", ".java", ".go", ".cpp", ".c", ".rb", ".php"],
  "rate_limits": {
    "review_per_minute": 10,
    "reports_per_minute": 60
  }
}
```

**Health Check**
```bash
curl -X GET "http://localhost:8000/api/health"
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "llm": "healthy",
    "storage": "healthy",
    "system": "healthy"
  },
  "version": "1.0.0"
}
```

#### User Management

**Get Current User Info**
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "X-API-Key: your_api_key_here"
```

**Get Rate Limit Status**
```bash
curl -X GET "http://localhost:8000/api/auth/rate-limit" \
  -H "X-API-Key: your_api_key_here"
```

Response:
```json
{
  "requests_per_minute": 10,
  "current_usage": 3,
  "reset_time": "2024-01-01T00:01:00Z",
  "tier": "standard"
}
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following:

#### Core Settings
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Enable debug mode (default: true)

#### LLM Provider
- `LLM_PROVIDER`: Choose "openai" or "gemini" (default: gemini)

#### OpenAI Configuration
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Model to use (default: gpt-4)
- `OPENAI_MAX_TOKENS`: Maximum tokens per request (default: 4000)

#### Gemini Configuration
- `GEMINI_API_KEY`: Your Google Gemini API key
- `GEMINI_MODEL`: Model to use (default: gemini-pro)
- `GEMINI_MAX_TOKENS`: Maximum tokens per request (default: 4000)

#### File Upload
- `MAX_FILE_SIZE_MB`: Maximum file size (default: 10MB)
- `UPLOAD_DIR`: Directory for uploaded files (default: ./uploads)
- `REPORTS_DIR`: Directory for report storage (default: ./reports)

#### Security
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `API_KEY_SALT`: Salt for API key generation
- `ALLOWED_ORIGINS`: CORS allowed origins (comma-separated)
- `CORS_ENABLED`: Enable CORS (default: true)

#### Rate Limiting
- `RATE_LIMIT_REQUESTS_PER_MINUTE`: API rate limit (default: 10)

#### TLS/HTTPS (Production)
- `TLS_CERT_FILE`: Path to TLS certificate file
- `TLS_KEY_FILE`: Path to TLS private key file
- `TLS_CA_FILE`: Path to CA bundle file

### Getting API Keys

#### Google Gemini
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

#### OpenAI
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to your `.env` file as `OPENAI_API_KEY`

## Sample Code Files

Create these sample files for testing:

**sample_python.py** (Good code):
```python
def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def main():
    number = 10
    result = calculate_fibonacci(number)
    print(f"Fibonacci({number}) = {result}")

if __name__ == "__main__":
    main()
```

**sample_issues.py** (Code with issues):
```python
import os
import sqlite3

# Security issue: hardcoded credentials
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "admin123"

def get_user_data(user_id):
    # Security issue: SQL injection vulnerability
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchall()

def process_file(filename):
    # Performance issue: file not closed properly
    file = open(filename, 'r')
    data = file.read()
    return data.upper()

# Style issue: unused import, poor naming
def calc(x, y):
    return x + y
```

**sample_javascript.js**:
```javascript
// Performance issue: inefficient DOM manipulation
function updateList(items) {
    const list = document.getElementById('list');
    list.innerHTML = '';
    
    for (let i = 0; i < items.length; i++) {
        const li = document.createElement('li');
        li.textContent = items[i];
        list.appendChild(li);
    }
}

// Security issue: potential XSS vulnerability
function displayMessage(message) {
    document.getElementById('output').innerHTML = message;
}

// Code quality issue: no error handling
async function fetchData(url) {
    const response = await fetch(url);
    const data = await response.json();
    return data;
}
```

## Web Dashboard

Access the web dashboard at `http://localhost:8000` for:

- **File Upload**: Drag-and-drop interface for code files
- **Report Viewing**: Interactive display of analysis results
- **Report History**: Browse and search previous reviews
- **Syntax Highlighting**: Code display with issue annotations

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest test_auth.py
```

### Code Style

```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy app/
```

### Project Structure

```
code-review-assistant/
├── app/
│   ├── api/           # API endpoints
│   ├── auth/          # Authentication system
│   ├── models/        # Data models
│   ├── services/      # Business logic
│   ├── utils/         # Utilities
│   ├── static/        # Web dashboard files
│   └── templates/     # HTML templates
├── docs/              # Documentation
├── logs/              # Application logs
├── reports/           # Stored reports
├── uploads/           # Uploaded files
├── .env.example       # Environment template
├── config.py          # Configuration
├── main.py           # Application entry point
└── requirements.txt   # Dependencies
```

## Troubleshooting

### Common Issues

**LLM API Errors**
- Verify your API key is correct and has sufficient credits
- Check rate limits for your LLM provider
- Ensure network connectivity to the LLM service

**File Upload Issues**
- Check file size is under the limit (default 10MB)
- Verify file extension is supported
- Ensure proper Content-Type headers

**Authentication Errors**
- Verify API key is included in X-API-Key header
- Check that the API key exists and is active
- Ensure rate limits haven't been exceeded

### Logs

Application logs are stored in the `logs/` directory:
- `app.log`: General application logs
- `error.log`: Error-specific logs
- `requests.log`: HTTP request logs

### Support

For issues and questions:
1. Check the logs for error details
2. Verify your configuration matches the examples
3. Test with the provided sample files
4. Review the API documentation at `/docs`

## License

MIT License