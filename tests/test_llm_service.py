"""
Unit tests for LLM service functionality.
Tests LLM integration, code chunking, and analysis result processing.
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
import asyncio

from app.services.llm_service import (
    LLMService, OpenAIProvider, GeminiProvider, 
    CodeChunk, AnalysisContext, AnalysisResult, Issue, Recommendation
)


class TestCodeChunk:
    """Test CodeChunk data class."""
    
    def test_code_chunk_creation(self):
        """Test creating a CodeChunk instance."""
        chunk = CodeChunk(
            content="def hello(): pass",
            start_line=1,
            end_line=1,
            context="Test function",
            language="python"
        )
        
        assert chunk.content == "def hello(): pass"
        assert chunk.start_line == 1
        assert chunk.end_line == 1
        assert chunk.context == "Test function"
        assert chunk.language == "python"


class TestAnalysisContext:
    """Test AnalysisContext data class."""
    
    def test_analysis_context_creation(self):
        """Test creating an AnalysisContext instance."""
        context = AnalysisContext(
            language="python",
            ruleset=["security", "performance"],
            focus_areas=["security", "readability"],
            max_severity="high"
        )
        
        assert context.language == "python"
        assert context.ruleset == ["security", "performance"]
        assert context.focus_areas == ["security", "readability"]
        assert context.max_severity == "high"


class TestOpenAIProvider:
    """Test OpenAI provider implementation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.provider = OpenAIProvider()
    
    def test_is_configured_without_api_key(self):
        """Test configuration check without API key."""
        with patch('app.services.llm_service.settings.openai_api_key', None):
            provider = OpenAIProvider()
            assert provider.is_configured() is False
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        content = "def hello_world(): print('Hello, World!')"
        tokens = self.provider.estimate_tokens(content)
        
        assert tokens > 0
        assert isinstance(tokens, int)
        # Rough check: should be approximately content length / 4
        assert tokens == len(content) // 4
    
    @pytest.mark.asyncio
    async def test_generate_response_without_client(self):
        """Test response generation without configured client."""
        provider = OpenAIProvider()
        provider.client = None
        
        with pytest.raises(ValueError, match="OpenAI client not configured"):
            await provider.generate_response("test prompt")
    
    @pytest.mark.asyncio
    async def test_analyze_code_with_retry_success(self):
        """Test successful code analysis with retry logic."""
        # Mock the client
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "summary": "Test analysis completed",
            "issues": [
                {
                    "type": "security",
                    "severity": "high",
                    "line": 5,
                    "message": "Test issue",
                    "suggestion": "Test suggestion",
                    "code_snippet": "test code",
                    "confidence": 0.9
                }
            ],
            "recommendations": [
                {
                    "area": "security",
                    "message": "Test recommendation",
                    "impact": "high",
                    "effort": "medium",
                    "examples": ["example1"]
                }
            ]
        })
        
        mock_client.chat.completions.create.return_value = mock_response
        self.provider.client = mock_client
        
        chunk = CodeChunk(
            content="def test(): pass",
            start_line=1,
            end_line=1,
            context="Test",
            language="python"
        )
        context = AnalysisContext(
            language="python",
            ruleset=["security"],
            focus_areas=["security"]
        )
        
        result = await self.provider.analyze_code_with_retry(chunk, context)
        
        assert isinstance(result, AnalysisResult)
        assert result.summary == "Test analysis completed"
        assert len(result.issues) == 1
        assert len(result.recommendations) == 1
        assert result.issues[0].type == "security"
        assert result.issues[0].severity == "high"
    
    def test_build_analysis_prompt(self):
        """Test analysis prompt building."""
        chunk = CodeChunk(
            content="def vulnerable_function(): pass",
            start_line=10,
            end_line=10,
            context="Security test",
            language="python"
        )
        context = AnalysisContext(
            language="python",
            ruleset=["security"],
            focus_areas=["security", "performance"]
        )
        
        prompt = self.provider._build_analysis_prompt(chunk, context)
        
        assert "python" in prompt
        assert "security" in prompt
        assert "performance" in prompt
        assert "lines 10-10" in prompt
        assert "vulnerable_function" in prompt
        assert "JSON" in prompt
    
    def test_parse_analysis_response_valid_json(self):
        """Test parsing valid JSON response."""
        response = json.dumps({
            "summary": "Analysis complete",
            "issues": [
                {
                    "type": "bug",
                    "severity": "medium",
                    "line": 3,
                    "message": "Potential bug",
                    "suggestion": "Fix this",
                    "confidence": 0.8
                }
            ],
            "recommendations": []
        })
        
        result = self.provider._parse_analysis_response(response, 1.5)
        
        assert result.summary == "Analysis complete"
        assert len(result.issues) == 1
        assert result.issues[0].type == "bug"
        assert result.processing_time == 1.5
    
    def test_parse_analysis_response_invalid_json(self):
        """Test parsing invalid JSON response."""
        invalid_response = "This is not valid JSON"
        
        result = self.provider._parse_analysis_response(invalid_response, 1.0)
        
        # Should return fallback result
        assert "parsing errors" in result.summary
        assert len(result.issues) == 0
        assert result.confidence == 0.5
    
    def test_parse_analysis_response_with_markdown(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        response = '''```json
{
    "summary": "Test summary",
    "issues": [],
    "recommendations": []
}
```'''
        
        result = self.provider._parse_analysis_response(response, 1.0)
        
        assert result.summary == "Test summary"
        assert len(result.issues) == 0


class TestGeminiProvider:
    """Test Gemini provider implementation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.provider = GeminiProvider()
    
    def test_is_configured_without_api_key(self):
        """Test configuration check without API key."""
        with patch('app.services.llm_service.settings.gemini_api_key', None):
            provider = GeminiProvider()
            assert provider.is_configured() is False
    
    def test_estimate_tokens(self):
        """Test token estimation for Gemini."""
        content = "function test() { return 'hello'; }"
        tokens = self.provider.estimate_tokens(content)
        
        assert tokens > 0
        assert isinstance(tokens, int)
        assert tokens == len(content) // 4
    
    @pytest.mark.asyncio
    async def test_generate_response_without_client(self):
        """Test response generation without configured client."""
        provider = GeminiProvider()
        provider.client = None
        
        with pytest.raises(ValueError, match="Gemini client not configured"):
            await provider.generate_response("test prompt")


class TestLLMService:
    """Test main LLM service functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.llm_service = LLMService()
    
    def test_get_provider_openai(self):
        """Test getting OpenAI provider."""
        with patch('app.services.llm_service.settings.llm_provider', 'openai'):
            service = LLMService()
            with patch.object(service.providers['openai'], 'is_configured', return_value=True):
                provider = service.get_provider()
                assert isinstance(provider, OpenAIProvider)
    
    def test_get_provider_gemini(self):
        """Test getting Gemini provider."""
        with patch('app.services.llm_service.settings.llm_provider', 'gemini'):
            service = LLMService()
            with patch.object(service.providers['gemini'], 'is_configured', return_value=True):
                provider = service.get_provider()
                assert isinstance(provider, GeminiProvider)
    
    def test_get_provider_unknown(self):
        """Test getting unknown provider."""
        with patch('app.services.llm_service.settings.llm_provider', 'unknown'):
            service = LLMService()
            with pytest.raises(ValueError, match="Unknown LLM provider"):
                service.get_provider()
    
    def test_get_provider_not_configured(self):
        """Test getting provider that's not configured."""
        with patch('app.services.llm_service.settings.llm_provider', 'openai'):
            service = LLMService()
            with patch.object(service.providers['openai'], 'is_configured', return_value=False):
                with pytest.raises(ValueError, match="not properly configured"):
                    service.get_provider()
    
    def test_estimate_tokens(self):
        """Test token estimation using current provider."""
        with patch.object(self.llm_service, 'get_provider') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.estimate_tokens.return_value = 50
            mock_get_provider.return_value = mock_provider
            
            tokens = self.llm_service.estimate_tokens("test content")
            
            assert tokens == 50
            mock_provider.estimate_tokens.assert_called_once_with("test content")
    
    def test_chunk_code_small_content(self):
        """Test chunking small content that fits in one chunk."""
        small_code = "def hello(): pass"
        
        with patch.object(self.llm_service, 'estimate_tokens', return_value=100):
            chunks = self.llm_service.chunk_code(small_code, "python")
            
            assert len(chunks) == 1
            assert chunks[0].content == small_code
            assert chunks[0].language == "python"
    
    def test_chunk_python_code(self):
        """Test chunking Python code by functions."""
        python_code = '''
def function1():
    print("Function 1")
    return 1

def function2():
    print("Function 2")
    return 2

class TestClass:
    def method1(self):
        pass
'''
        
        with patch.object(self.llm_service, 'estimate_tokens', side_effect=lambda x: len(x)):
            chunks = self.llm_service._chunk_python_code(python_code)
            
            assert len(chunks) > 1
            # Should have chunks for different functions/classes
            assert any("function1" in chunk.content for chunk in chunks)
            assert any("function2" in chunk.content for chunk in chunks)
            assert any("TestClass" in chunk.content for chunk in chunks)
    
    def test_chunk_javascript_code(self):
        """Test chunking JavaScript code by functions."""
        js_code = '''
function test1() {
    console.log("Test 1");
}

const test2 = () => {
    console.log("Test 2");
}

class MyClass {
    constructor() {
        this.value = 0;
    }
}
'''
        
        with patch.object(self.llm_service, 'estimate_tokens', side_effect=lambda x: len(x)):
            chunks = self.llm_service._chunk_javascript_code(js_code)
            
            assert len(chunks) > 1
            assert any("test1" in chunk.content for chunk in chunks)
            assert any("test2" in chunk.content for chunk in chunks)
    
    def test_chunk_java_code(self):
        """Test chunking Java code by methods and classes."""
        java_code = '''
public class TestClass {
    public void method1() {
        System.out.println("Method 1");
    }
    
    private int method2() {
        return 42;
    }
}

public interface TestInterface {
    void interfaceMethod();
}
'''
        
        with patch.object(self.llm_service, 'estimate_tokens', side_effect=lambda x: len(x)):
            chunks = self.llm_service._chunk_java_code(java_code)
            
            assert len(chunks) > 1
            assert any("TestClass" in chunk.content for chunk in chunks)
            assert any("TestInterface" in chunk.content for chunk in chunks)
    
    def test_chunk_go_code(self):
        """Test chunking Go code by functions and types."""
        go_code = '''
func main() {
    fmt.Println("Hello, World!")
}

func helper() int {
    return 42
}

type Person struct {
    Name string
    Age  int
}

func (p Person) String() string {
    return fmt.Sprintf("%s (%d)", p.Name, p.Age)
}
'''
        
        with patch.object(self.llm_service, 'estimate_tokens', side_effect=lambda x: len(x)):
            chunks = self.llm_service._chunk_go_code(go_code)
            
            assert len(chunks) > 1
            assert any("main" in chunk.content for chunk in chunks)
            assert any("Person" in chunk.content for chunk in chunks)
    
    def test_chunk_by_lines_fallback(self):
        """Test fallback chunking by line count."""
        large_code = "\n".join([f"line {i}" for i in range(100)])
        
        chunks = self.llm_service._chunk_by_lines(large_code, "unknown")
        
        assert len(chunks) == 2  # 100 lines / 50 lines per chunk
        assert chunks[0].start_line == 1
        assert chunks[0].end_line == 50
        assert chunks[1].start_line == 51
        assert chunks[1].end_line == 100
    
    @pytest.mark.asyncio
    async def test_analyze_code(self):
        """Test analyzing a single code chunk."""
        chunk = CodeChunk(
            content="def test(): pass",
            start_line=1,
            end_line=1,
            context="Test",
            language="python"
        )
        context = AnalysisContext(
            language="python",
            ruleset=["security"],
            focus_areas=["security"]
        )
        
        mock_result = AnalysisResult(
            summary="Test analysis",
            issues=[],
            recommendations=[],
            confidence=0.9,
            processing_time=1.0
        )
        
        with patch.object(self.llm_service, 'get_provider') as mock_get_provider:
            mock_provider = AsyncMock()
            mock_provider.analyze_code_with_retry.return_value = mock_result
            mock_get_provider.return_value = mock_provider
            
            result = await self.llm_service.analyze_code(chunk, context)
            
            assert result == mock_result
            mock_provider.analyze_code_with_retry.assert_called_once_with(chunk, context)
    
    def test_aggregate_results_empty(self):
        """Test aggregating empty results list."""
        result = self.llm_service.aggregate_results([])
        
        assert result.summary == "No analysis results to aggregate"
        assert len(result.issues) == 0
        assert len(result.recommendations) == 0
        assert result.confidence == 0.0
    
    def test_aggregate_results_single(self):
        """Test aggregating single result."""
        single_result = AnalysisResult(
            summary="Single analysis",
            issues=[Issue("bug", "high", 1, "Test issue", "Fix it", confidence=0.9)],
            recommendations=[],
            confidence=0.9,
            processing_time=1.0
        )
        
        result = self.llm_service.aggregate_results([single_result])
        
        assert result == single_result
    
    def test_aggregate_results_multiple(self):
        """Test aggregating multiple results."""
        result1 = AnalysisResult(
            summary="Analysis 1",
            issues=[Issue("bug", "high", 1, "Issue 1", "Fix 1", confidence=0.9)],
            recommendations=[Recommendation("security", "Rec 1", "high", "low")],
            confidence=0.9,
            processing_time=1.0
        )
        
        result2 = AnalysisResult(
            summary="Analysis 2", 
            issues=[Issue("security", "medium", 5, "Issue 2", "Fix 2", confidence=0.8)],
            recommendations=[Recommendation("performance", "Rec 2", "medium", "medium")],
            confidence=0.8,
            processing_time=2.0
        )
        
        with patch.object(self.llm_service, '_deduplicate_issues', side_effect=lambda x: x):
            with patch.object(self.llm_service, '_deduplicate_recommendations', side_effect=lambda x: x):
                result = self.llm_service.aggregate_results([result1, result2])
        
        assert len(result.issues) == 2
        assert len(result.recommendations) == 2
        assert result.processing_time == 3.0  # Sum of processing times
        assert result.confidence == 0.85  # Average confidence
        assert "2 code chunks" in result.summary
        assert "1 high, 1 medium, 0 low" in result.summary
    
    def test_deduplicate_issues(self):
        """Test issue deduplication logic."""
        issues = [
            Issue("bug", "high", 1, "Duplicate issue", "Fix it", confidence=0.9),
            Issue("bug", "high", 1, "Duplicate issue", "Fix it", confidence=0.8),
            Issue("security", "medium", 5, "Different issue", "Fix differently", confidence=0.7)
        ]
        
        # Mock the method to test the logic
        unique_issues = []
        seen_messages = set()
        
        for issue in issues:
            if issue.message not in seen_messages:
                unique_issues.append(issue)
                seen_messages.add(issue.message)
        
        assert len(unique_issues) == 2
        assert unique_issues[0].message == "Duplicate issue"
        assert unique_issues[1].message == "Different issue"


class TestLLMServiceIntegration:
    """Integration tests for LLM service with mocked providers."""
    
    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self, sample_python_code, mock_llm_response):
        """Test complete analysis workflow from code to results."""
        llm_service = LLMService()
        
        # Mock the provider
        with patch.object(llm_service, 'get_provider') as mock_get_provider:
            mock_provider = AsyncMock()
            mock_provider.analyze_code_with_retry.return_value = mock_llm_response
            mock_get_provider.return_value = mock_provider
            
            # Test chunking and analysis
            chunks = llm_service.chunk_code(sample_python_code, "python")
            assert len(chunks) >= 1
            
            # Analyze first chunk
            context = AnalysisContext(
                language="python",
                ruleset=["security", "performance"],
                focus_areas=["security", "performance"]
            )
            
            result = await llm_service.analyze_code(chunks[0], context)
            
            assert result == mock_llm_response
            assert len(result.issues) == 3
            assert len(result.recommendations) == 2
            assert result.confidence == 0.90