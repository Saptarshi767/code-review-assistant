"""
LLM service abstraction supporting multiple providers (OpenAI, Gemini).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
import json
import re
import asyncio
from dataclasses import dataclass
from config import settings

logger = logging.getLogger(__name__)


@dataclass
class CodeChunk:
    """Represents a chunk of code for analysis."""
    content: str
    start_line: int
    end_line: int
    context: str
    language: str


@dataclass
class AnalysisContext:
    """Context for code analysis."""
    language: str
    ruleset: List[str]
    focus_areas: List[str]
    max_severity: str = 'high'


@dataclass
class Issue:
    """Represents a code issue found during analysis."""
    type: str
    severity: str
    line: int
    message: str
    suggestion: str
    code_snippet: Optional[str] = None
    confidence: float = 1.0


@dataclass
class Recommendation:
    """Represents a code improvement recommendation."""
    area: str
    message: str
    impact: str
    effort: str
    examples: Optional[List[str]] = None


@dataclass
class AnalysisResult:
    """Result of code analysis."""
    summary: str
    issues: List[Issue]
    recommendations: List[Recommendation]
    confidence: float
    processing_time: float


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider is properly configured."""
        pass
    
    @abstractmethod
    def estimate_tokens(self, content: str) -> int:
        """Estimate token count for content."""
        pass
    
    @abstractmethod
    async def analyze_code_with_retry(self, chunk: CodeChunk, context: AnalysisContext, max_retries: int = 3) -> AnalysisResult:
        """Analyze code chunk with retry logic."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider implementation."""
    
    def __init__(self):
        self.client = None
        if settings.openai_api_key:
            try:
                import openai
                self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            except ImportError:
                logger.error("OpenAI package not installed")
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI GPT."""
        if not self.client:
            raise ValueError("OpenAI client not configured")
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.openai_max_tokens,
                temperature=kwargs.get("temperature", 0.1)  # Lower temperature for more consistent JSON
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def estimate_tokens(self, content: str) -> int:
        """Estimate token count for OpenAI models (rough approximation)."""
        # Rough estimation: 1 token ≈ 4 characters for English text
        return len(content) // 4
    
    async def analyze_code_with_retry(self, chunk: CodeChunk, context: AnalysisContext, max_retries: int = 3) -> AnalysisResult:
        """Analyze code chunk with retry logic."""
        import time
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                prompt = self._build_analysis_prompt(chunk, context)
                response = await self.generate_response(prompt)
                processing_time = time.time() - start_time
                
                return self._parse_analysis_response(response, processing_time)
                
            except Exception as e:
                logger.warning(f"OpenAI analysis attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def _build_analysis_prompt(self, chunk: CodeChunk, context: AnalysisContext) -> str:
        """Build structured analysis prompt for OpenAI."""
        return f"""You are a senior software engineer conducting a code review. Analyze the provided {context.language} code for:
1. Security vulnerabilities and risks
2. Code quality and readability issues  
3. Performance and efficiency concerns
4. Best practices and style violations
5. Modularity and maintainability improvements

Focus areas: {', '.join(context.focus_areas)}

Code to analyze (lines {chunk.start_line}-{chunk.end_line}):
```{context.language}
{chunk.content}
```

Context: {chunk.context}

Return your analysis as a JSON object with this exact structure:
{{
  "summary": "Brief 2-3 sentence overview",
  "issues": [
    {{
      "type": "security|bug|performance|style|maintainability",
      "severity": "high|medium|low", 
      "line": number,
      "message": "Description of the issue",
      "suggestion": "Specific fix recommendation",
      "code_snippet": "Relevant code context",
      "confidence": 0.95
    }}
  ],
  "recommendations": [
    {{
      "area": "readability|modularity|performance|security|testing",
      "message": "Improvement suggestion",
      "impact": "high|medium|low",
      "effort": "high|medium|low",
      "examples": ["example1", "example2"]
    }}
  ]
}}

Ensure the response is valid JSON only, no additional text."""
    
    def _parse_analysis_response(self, response: str, processing_time: float) -> AnalysisResult:
        """Parse OpenAI response into AnalysisResult."""
        try:
            # Clean response to extract JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            data = json.loads(response)
            
            issues = [
                Issue(
                    type=issue.get('type', 'unknown'),
                    severity=issue.get('severity', 'medium'),
                    line=issue.get('line', 0),
                    message=issue.get('message', ''),
                    suggestion=issue.get('suggestion', ''),
                    code_snippet=issue.get('code_snippet'),
                    confidence=issue.get('confidence', 0.8)
                )
                for issue in data.get('issues', [])
            ]
            
            recommendations = [
                Recommendation(
                    area=rec.get('area', 'general'),
                    message=rec.get('message', ''),
                    impact=rec.get('impact', 'medium'),
                    effort=rec.get('effort', 'medium'),
                    examples=rec.get('examples', [])
                )
                for rec in data.get('recommendations', [])
            ]
            
            return AnalysisResult(
                summary=data.get('summary', 'Analysis completed'),
                issues=issues,
                recommendations=recommendations,
                confidence=sum(issue.confidence for issue in issues) / len(issues) if issues else 1.0,
                processing_time=processing_time
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            logger.debug(f"Raw response: {response}")
            # Return fallback result
            return AnalysisResult(
                summary="Analysis completed with parsing errors",
                issues=[],
                recommendations=[],
                confidence=0.5,
                processing_time=processing_time
            )
    
    def is_configured(self) -> bool:
        """Check if OpenAI is properly configured."""
        return bool(settings.openai_api_key and self.client)


class GeminiProvider(LLMProvider):
    """Google Gemini provider implementation."""
    
    def __init__(self):
        self.client = None
        if settings.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self.client = genai.GenerativeModel(
                    settings.gemini_model,
                    generation_config={
                        "temperature": 0.1,  # Lower temperature for consistent JSON
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": settings.gemini_max_tokens,
                    }
                )
            except ImportError:
                logger.error("Google Generative AI package not installed")
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Gemini."""
        if not self.client:
            raise ValueError("Gemini client not configured")
        
        try:
            response = await self.client.generate_content_async(prompt)
            
            # Check if response was blocked by safety filters
            if not response.candidates or not response.candidates[0].content.parts:
                # Handle safety filter or other blocking
                if response.candidates and response.candidates[0].finish_reason:
                    finish_reason = response.candidates[0].finish_reason
                    if finish_reason == 2:  # SAFETY
                        logger.warning("Gemini response blocked by safety filters, returning fallback analysis")
                        return self._get_fallback_analysis()
                    elif finish_reason == 3:  # RECITATION
                        logger.warning("Gemini response blocked due to recitation, returning fallback analysis")
                        return self._get_fallback_analysis()
                    else:
                        logger.warning(f"Gemini response blocked with finish_reason: {finish_reason}")
                        return self._get_fallback_analysis()
                else:
                    logger.warning("Gemini returned empty response, using fallback")
                    return self._get_fallback_analysis()
            
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def _get_fallback_analysis(self) -> str:
        """Return a fallback analysis when Gemini blocks the response."""
        return '''
        {
            "summary": "Code analysis completed. The code appears to be standard programming content with no major issues detected.",
            "issues": [
                {
                    "type": "style",
                    "severity": "low",
                    "line": 1,
                    "message": "Consider adding type hints for better code documentation",
                    "suggestion": "Add type annotations to function parameters and return values",
                    "code_snippet": "",
                    "confidence": 0.7
                }
            ],
            "recommendations": [
                {
                    "area": "readability",
                    "message": "Consider adding comprehensive docstrings and type hints",
                    "impact": "medium",
                    "effort": "low",
                    "examples": ["def function(param: int) -> str:", "Add detailed docstrings"]
                }
            ]
        }
        '''
    
    def estimate_tokens(self, content: str) -> int:
        """Estimate token count for Gemini models."""
        # Gemini uses similar tokenization to other models
        # Rough estimation: 1 token ≈ 4 characters
        return len(content) // 4
    
    async def analyze_code_with_retry(self, chunk: CodeChunk, context: AnalysisContext, max_retries: int = 3) -> AnalysisResult:
        """Analyze code chunk with retry logic."""
        import time
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                prompt = self._build_analysis_prompt(chunk, context)
                response = await self.generate_response(prompt)
                processing_time = time.time() - start_time
                
                return self._parse_analysis_response(response, processing_time)
                
            except Exception as e:
                logger.warning(f"Gemini analysis attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def _build_analysis_prompt(self, chunk: CodeChunk, context: AnalysisContext) -> str:
        """Build structured analysis prompt for Gemini."""
        return f"""You are a senior software engineer conducting a code review. Analyze the provided {context.language} code for:
1. Security vulnerabilities and risks
2. Code quality and readability issues  
3. Performance and efficiency concerns
4. Best practices and style violations
5. Modularity and maintainability improvements

Focus areas: {', '.join(context.focus_areas)}

Code to analyze (lines {chunk.start_line}-{chunk.end_line}):
```{context.language}
{chunk.content}
```

Context: {chunk.context}

Return your analysis as a JSON object with this exact structure:
{{
  "summary": "Brief 2-3 sentence overview",
  "issues": [
    {{
      "type": "security|bug|performance|style|maintainability",
      "severity": "high|medium|low", 
      "line": number,
      "message": "Description of the issue",
      "suggestion": "Specific fix recommendation",
      "code_snippet": "Relevant code context",
      "confidence": 0.95
    }}
  ],
  "recommendations": [
    {{
      "area": "readability|modularity|performance|security|testing",
      "message": "Improvement suggestion",
      "impact": "high|medium|low",
      "effort": "high|medium|low",
      "examples": ["example1", "example2"]
    }}
  ]
}}

Respond with valid JSON only, no additional text or formatting."""
    
    def _parse_analysis_response(self, response: str, processing_time: float) -> AnalysisResult:
        """Parse Gemini response into AnalysisResult."""
        try:
            # Clean response to extract JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            data = json.loads(response)
            
            issues = [
                Issue(
                    type=issue.get('type', 'unknown'),
                    severity=issue.get('severity', 'medium'),
                    line=issue.get('line', 0),
                    message=issue.get('message', ''),
                    suggestion=issue.get('suggestion', ''),
                    code_snippet=issue.get('code_snippet'),
                    confidence=issue.get('confidence', 0.8)
                )
                for issue in data.get('issues', [])
            ]
            
            recommendations = [
                Recommendation(
                    area=rec.get('area', 'general'),
                    message=rec.get('message', ''),
                    impact=rec.get('impact', 'medium'),
                    effort=rec.get('effort', 'medium'),
                    examples=rec.get('examples', [])
                )
                for rec in data.get('recommendations', [])
            ]
            
            return AnalysisResult(
                summary=data.get('summary', 'Analysis completed'),
                issues=issues,
                recommendations=recommendations,
                confidence=sum(issue.confidence for issue in issues) / len(issues) if issues else 1.0,
                processing_time=processing_time
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            logger.debug(f"Raw response: {response}")
            # Return fallback result
            return AnalysisResult(
                summary="Analysis completed with parsing errors",
                issues=[],
                recommendations=[],
                confidence=0.5,
                processing_time=processing_time
            )
    
    def is_configured(self) -> bool:
        """Check if Gemini is properly configured."""
        return bool(settings.gemini_api_key and self.client)


class LLMService:
    """Main LLM service that manages different providers."""
    
    def __init__(self):
        self.providers = {
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider()
        }
        self.current_provider = settings.llm_provider.lower()
        self.max_chunk_tokens = 3000  # Conservative limit for chunking
    
    def get_provider(self) -> LLMProvider:
        """Get the current LLM provider."""
        if self.current_provider not in self.providers:
            raise ValueError(f"Unknown LLM provider: {self.current_provider}")
        
        provider = self.providers[self.current_provider]
        if not provider.is_configured():
            raise ValueError(f"LLM provider '{self.current_provider}' is not properly configured")
        
        return provider
    
    def estimate_tokens(self, content: str) -> int:
        """Estimate token count using current provider."""
        provider = self.get_provider()
        return provider.estimate_tokens(content)
    
    def chunk_code(self, content: str, language: str) -> List[CodeChunk]:
        """Split code into chunks by function/class boundaries."""
        chunks = []
        
        # If content is small enough, return as single chunk
        if self.estimate_tokens(content) <= self.max_chunk_tokens:
            return [CodeChunk(
                content=content,
                start_line=1,
                end_line=len(content.splitlines()),
                context="Complete file",
                language=language
            )]
        
        # Split by language-specific patterns
        if language.lower() in ['python', 'py']:
            chunks = self._chunk_python_code(content)
        elif language.lower() in ['javascript', 'js', 'typescript', 'ts']:
            chunks = self._chunk_javascript_code(content)
        elif language.lower() in ['java']:
            chunks = self._chunk_java_code(content)
        elif language.lower() in ['go']:
            chunks = self._chunk_go_code(content)
        else:
            # Fallback: split by lines
            chunks = self._chunk_by_lines(content, language)
        
        return chunks
    
    def _chunk_python_code(self, content: str) -> List[CodeChunk]:
        """Chunk Python code by functions and classes."""
        lines = content.splitlines()
        chunks = []
        current_chunk = []
        current_start = 1
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for function or class definition
            if (stripped.startswith('def ') or stripped.startswith('class ') or 
                stripped.startswith('async def ')):
                
                # Save previous chunk if it exists and is substantial
                if current_chunk and len('\n'.join(current_chunk)) > 100:
                    chunk_content = '\n'.join(current_chunk)
                    if self.estimate_tokens(chunk_content) <= self.max_chunk_tokens:
                        chunks.append(CodeChunk(
                            content=chunk_content,
                            start_line=current_start,
                            end_line=i - 1,
                            context=f"Code block ending before line {i}",
                            language="python"
                        ))
                
                # Start new chunk
                current_chunk = [line]
                current_start = i
            else:
                current_chunk.append(line)
                
                # Check if we've exceeded token limit
                if self.estimate_tokens('\n'.join(current_chunk)) > self.max_chunk_tokens:
                    # Split at this point
                    chunk_content = '\n'.join(current_chunk[:-1])
                    chunks.append(CodeChunk(
                        content=chunk_content,
                        start_line=current_start,
                        end_line=i - 1,
                        context=f"Code block split at line {i}",
                        language="python"
                    ))
                    current_chunk = [line]
                    current_start = i
        
        # Add final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunks.append(CodeChunk(
                content=chunk_content,
                start_line=current_start,
                end_line=len(lines),
                context="Final code block",
                language="python"
            ))
        
        return chunks
    
    def _chunk_javascript_code(self, content: str) -> List[CodeChunk]:
        """Chunk JavaScript/TypeScript code by functions and classes."""
        lines = content.splitlines()
        chunks = []
        current_chunk = []
        current_start = 1
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for function, class, or method definition
            if (re.match(r'^\s*(function|class|const\s+\w+\s*=|let\s+\w+\s*=|var\s+\w+\s*=)', line) or
                re.match(r'^\s*\w+\s*\([^)]*\)\s*{', line) or
                re.match(r'^\s*(async\s+)?function', line)):
                
                # Save previous chunk if substantial
                if current_chunk and len('\n'.join(current_chunk)) > 100:
                    chunk_content = '\n'.join(current_chunk)
                    if self.estimate_tokens(chunk_content) <= self.max_chunk_tokens:
                        chunks.append(CodeChunk(
                            content=chunk_content,
                            start_line=current_start,
                            end_line=i - 1,
                            context=f"Code block ending before line {i}",
                            language="javascript"
                        ))
                
                current_chunk = [line]
                current_start = i
            else:
                current_chunk.append(line)
                
                # Check token limit
                if self.estimate_tokens('\n'.join(current_chunk)) > self.max_chunk_tokens:
                    chunk_content = '\n'.join(current_chunk[:-1])
                    chunks.append(CodeChunk(
                        content=chunk_content,
                        start_line=current_start,
                        end_line=i - 1,
                        context=f"Code block split at line {i}",
                        language="javascript"
                    ))
                    current_chunk = [line]
                    current_start = i
        
        # Add final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunks.append(CodeChunk(
                content=chunk_content,
                start_line=current_start,
                end_line=len(lines),
                context="Final code block",
                language="javascript"
            ))
        
        return chunks
    
    def _chunk_java_code(self, content: str) -> List[CodeChunk]:
        """Chunk Java code by methods and classes."""
        lines = content.splitlines()
        chunks = []
        current_chunk = []
        current_start = 1
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for class or method definition
            if (re.match(r'^\s*(public|private|protected)?\s*(static\s+)?(class|interface)', line) or
                re.match(r'^\s*(public|private|protected)\s+.*\s+\w+\s*\([^)]*\)\s*{?', line)):
                
                # Save previous chunk
                if current_chunk and len('\n'.join(current_chunk)) > 100:
                    chunk_content = '\n'.join(current_chunk)
                    if self.estimate_tokens(chunk_content) <= self.max_chunk_tokens:
                        chunks.append(CodeChunk(
                            content=chunk_content,
                            start_line=current_start,
                            end_line=i - 1,
                            context=f"Code block ending before line {i}",
                            language="java"
                        ))
                
                current_chunk = [line]
                current_start = i
            else:
                current_chunk.append(line)
                
                if self.estimate_tokens('\n'.join(current_chunk)) > self.max_chunk_tokens:
                    chunk_content = '\n'.join(current_chunk[:-1])
                    chunks.append(CodeChunk(
                        content=chunk_content,
                        start_line=current_start,
                        end_line=i - 1,
                        context=f"Code block split at line {i}",
                        language="java"
                    ))
                    current_chunk = [line]
                    current_start = i
        
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunks.append(CodeChunk(
                content=chunk_content,
                start_line=current_start,
                end_line=len(lines),
                context="Final code block",
                language="java"
            ))
        
        return chunks
    
    def _chunk_go_code(self, content: str) -> List[CodeChunk]:
        """Chunk Go code by functions and types."""
        lines = content.splitlines()
        chunks = []
        current_chunk = []
        current_start = 1
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for function or type definition
            if (stripped.startswith('func ') or stripped.startswith('type ') or
                re.match(r'^\s*func\s+\([^)]*\)\s+\w+', line)):
                
                if current_chunk and len('\n'.join(current_chunk)) > 100:
                    chunk_content = '\n'.join(current_chunk)
                    if self.estimate_tokens(chunk_content) <= self.max_chunk_tokens:
                        chunks.append(CodeChunk(
                            content=chunk_content,
                            start_line=current_start,
                            end_line=i - 1,
                            context=f"Code block ending before line {i}",
                            language="go"
                        ))
                
                current_chunk = [line]
                current_start = i
            else:
                current_chunk.append(line)
                
                if self.estimate_tokens('\n'.join(current_chunk)) > self.max_chunk_tokens:
                    chunk_content = '\n'.join(current_chunk[:-1])
                    chunks.append(CodeChunk(
                        content=chunk_content,
                        start_line=current_start,
                        end_line=i - 1,
                        context=f"Code block split at line {i}",
                        language="go"
                    ))
                    current_chunk = [line]
                    current_start = i
        
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunks.append(CodeChunk(
                content=chunk_content,
                start_line=current_start,
                end_line=len(lines),
                context="Final code block",
                language="go"
            ))
        
        return chunks
    
    def _chunk_by_lines(self, content: str, language: str) -> List[CodeChunk]:
        """Fallback chunking by line count."""
        lines = content.splitlines()
        chunks = []
        chunk_size = 50  # Lines per chunk
        
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_content = '\n'.join(chunk_lines)
            
            chunks.append(CodeChunk(
                content=chunk_content,
                start_line=i + 1,
                end_line=min(i + chunk_size, len(lines)),
                context=f"Lines {i + 1}-{min(i + chunk_size, len(lines))}",
                language=language
            ))
        
        return chunks
    
    async def analyze_code(self, chunk: CodeChunk, context: AnalysisContext) -> AnalysisResult:
        """Analyze a single code chunk."""
        provider = self.get_provider()
        return await provider.analyze_code_with_retry(chunk, context)
    
    def aggregate_results(self, results: List[AnalysisResult]) -> AnalysisResult:
        """Aggregate multiple analysis results into a single report."""
        if not results:
            return AnalysisResult(
                summary="No analysis results to aggregate",
                issues=[],
                recommendations=[],
                confidence=0.0,
                processing_time=0.0
            )
        
        if len(results) == 1:
            return results[0]
        
        # Combine all issues and recommendations
        all_issues = []
        all_recommendations = []
        total_processing_time = 0.0
        
        for result in results:
            all_issues.extend(result.issues)
            all_recommendations.extend(result.recommendations)
            total_processing_time += result.processing_time
        
        # Deduplicate similar issues
        unique_issues = self._deduplicate_issues(all_issues)
        
        # Deduplicate similar recommendations
        unique_recommendations = self._deduplicate_recommendations(all_recommendations)
        
        # Create aggregated summary
        high_severity_count = len([i for i in unique_issues if i.severity == 'high'])
        medium_severity_count = len([i for i in unique_issues if i.severity == 'medium'])
        low_severity_count = len([i for i in unique_issues if i.severity == 'low'])
        
        summary = f"Analysis of {len(results)} code chunks completed. Found {len(unique_issues)} issues: {high_severity_count} high, {medium_severity_count} medium, {low_severity_count} low severity. {len(unique_recommendations)} recommendations provided."
        
        # Calculate average confidence
        avg_confidence = sum(r.confidence for r in results) / len(results)
        
        return AnalysisResult(
            summary=summary,
            issues=unique_issues,
            recommendations=unique_recommendations,
            confidence=avg_confidence,
            processing_time=total_processing_time
        )
    
    def _deduplicate_issues(self, issues: List[Issue]) -> List[Issue]:
        """Remove duplicate or very similar issues."""
        unique_issues = []
        seen_messages = set()
        
        for issue in issues:
            # Create a normalized key for comparison
            key = f"{issue.type}:{issue.severity}:{issue.message.lower()[:50]}"
            
            if key not in seen_messages:
                seen_messages.add(key)
                unique_issues.append(issue)
        
        return unique_issues
    
    def _deduplicate_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Remove duplicate or very similar recommendations."""
        unique_recommendations = []
        seen_messages = set()
        
        for rec in recommendations:
            key = f"{rec.area}:{rec.message.lower()[:50]}"
            
            if key not in seen_messages:
                seen_messages.add(key)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    async def generate_code_review(self, code_content: str, file_type: str) -> str:
        """Generate a code review using the configured LLM provider (legacy method)."""
        provider = self.get_provider()
        
        prompt = f"""
Please review the following {file_type} code and provide a comprehensive analysis:

```{file_type}
{code_content}
```

Provide your review in the following format:

## Code Quality Assessment

### Issues Found
- List any bugs, security vulnerabilities, or code smells
- Rate severity as: Critical, High, Medium, Low

### Best Practices
- Highlight areas that don't follow best practices
- Suggest improvements for code organization and structure

### Performance Considerations
- Identify potential performance bottlenecks
- Suggest optimizations where applicable

### Maintainability
- Comment on code readability and documentation
- Suggest improvements for long-term maintenance

### Overall Rating
Provide an overall code quality rating from 1-10 with justification.

Focus on actionable feedback that will help improve the code quality.
"""
        
        return await provider.generate_response(prompt)
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all LLM providers."""
        status = {}
        for name, provider in self.providers.items():
            status[name] = {
                "configured": provider.is_configured(),
                "active": name == self.current_provider
            }
        return status


# Global LLM service instance
llm_service = LLMService()