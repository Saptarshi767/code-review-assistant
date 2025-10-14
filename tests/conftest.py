"""
Pytest configuration and shared fixtures.
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import UploadFile
import io

from main import app
from app.services.file_service import FileService
from app.services.llm_service import LLMService, AnalysisResult, Issue, Recommendation
from app.auth.models import User


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def temp_upload_dir():
    """Create a temporary directory for file uploads during testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_user():
    """Create a mock user for authentication testing."""
    return User(
        user_id="test-user-123",
        api_key="test-api-key-456",
        email="test@example.com",
        rate_limit_tier="standard"
    )


@pytest.fixture
def sample_python_code():
    """Sample Python code for testing."""
    return '''
def calculate_password_hash(password):
    # Security issue: using weak hashing
    import hashlib
    return hashlib.md5(password.encode()).hexdigest()

def get_user_data(user_id):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

class UserManager:
    def __init__(self):
        self.api_key = "sk-1234567890abcdef"  # Hardcoded secret
        
    def process_data(self, data):
        # Performance issue: inefficient loop
        result = []
        for item in data:
            for other_item in data:
                if item != other_item:
                    result.append((item, other_item))
        return result
'''


@pytest.fixture
def sample_javascript_code():
    """Sample JavaScript code for testing."""
    return '''
function authenticateUser(username, password) {
    // Security issue: eval usage
    const query = eval(`"SELECT * FROM users WHERE username = '${username}'"`);
    
    // Hardcoded credentials
    const adminPassword = "admin123";
    
    if (password === adminPassword) {
        return true;
    }
    return false;
}

class DataProcessor {
    constructor() {
        this.apiKey = "abc123def456";  // Exposed secret
    }
    
    // Performance issue: synchronous file operations
    processFiles(files) {
        let results = [];
        for (let file of files) {
            const content = fs.readFileSync(file);  // Blocking operation
            results.push(content);
        }
        return results;
    }
}
'''


@pytest.fixture
def mock_llm_response():
    """Mock LLM analysis response."""
    return AnalysisResult(
        summary="Code analysis completed. Found 3 security issues and 2 performance concerns.",
        issues=[
            Issue(
                type="security",
                severity="high",
                line=3,
                message="Weak cryptographic hashing algorithm (MD5) detected",
                suggestion="Use bcrypt, scrypt, or Argon2 for password hashing",
                code_snippet="hashlib.md5(password.encode()).hexdigest()",
                confidence=0.95
            ),
            Issue(
                type="security", 
                severity="high",
                line=8,
                message="SQL injection vulnerability detected",
                suggestion="Use parameterized queries or ORM methods",
                code_snippet='query = f"SELECT * FROM users WHERE id = {user_id}"',
                confidence=0.90
            ),
            Issue(
                type="security",
                severity="medium",
                line=14,
                message="Hardcoded API key detected",
                suggestion="Store secrets in environment variables or secure vault",
                code_snippet='self.api_key = "sk-1234567890abcdef"',
                confidence=0.85
            )
        ],
        recommendations=[
            Recommendation(
                area="security",
                message="Implement proper secret management using environment variables",
                impact="high",
                effort="medium",
                examples=["Use os.getenv('API_KEY')", "Implement HashiCorp Vault integration"]
            ),
            Recommendation(
                area="performance",
                message="Optimize nested loops to reduce time complexity",
                impact="medium", 
                effort="low",
                examples=["Use set operations", "Implement caching for repeated calculations"]
            )
        ],
        confidence=0.90,
        processing_time=2.5
    )


@pytest.fixture
def create_upload_file():
    """Factory function to create UploadFile objects for testing."""
    def _create_upload_file(content: str, filename: str, content_type: str = "text/plain"):
        file_obj = io.BytesIO(content.encode('utf-8'))
        return UploadFile(
            file=file_obj,
            filename=filename,
            headers={"content-type": content_type}
        )
    return _create_upload_file


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service for testing."""
    mock_service = Mock(spec=LLMService)
    mock_service.estimate_tokens = Mock(return_value=100)
    mock_service.chunk_code = Mock(return_value=[])
    mock_service.analyze_code = AsyncMock()
    mock_service.aggregate_results = Mock()
    return mock_service


@pytest.fixture
def binary_file_content():
    """Binary file content for testing file validation."""
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'


@pytest.fixture
def large_file_content():
    """Large file content exceeding size limits."""
    # Create content larger than 10MB
    return "x" * (11 * 1024 * 1024)


@pytest.fixture
def zip_file_content():
    """Create a zip file with source code for testing."""
    import zipfile
    import io
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add Python file
        zip_file.writestr('main.py', '''
def hello_world():
    print("Hello, World!")
    
if __name__ == "__main__":
    hello_world()
''')
        # Add JavaScript file
        zip_file.writestr('script.js', '''
function greet(name) {
    console.log("Hello, " + name);
}

greet("World");
''')
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()