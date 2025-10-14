"""
Data models for code analysis results and LLM integration.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime, timezone


class IssueType(str, Enum):
    """Types of code issues that can be detected."""
    SECURITY = "security"
    BUG = "bug"
    PERFORMANCE = "performance"
    STYLE = "style"
    MAINTAINABILITY = "maintainability"
    UNKNOWN = "unknown"


class SeverityLevel(str, Enum):
    """Severity levels for code issues."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationArea(str, Enum):
    """Areas for code improvement recommendations."""
    READABILITY = "readability"
    MODULARITY = "modularity"
    PERFORMANCE = "performance"
    SECURITY = "security"
    TESTING = "testing"
    GENERAL = "general"


class EffortLevel(str, Enum):
    """Effort levels for implementing recommendations."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueModel(BaseModel):
    """Model for code issues found during analysis."""
    id: Optional[str] = Field(None, description="Unique identifier for the issue")
    type: IssueType = Field(..., description="Type of issue")
    severity: SeverityLevel = Field(..., description="Severity level")
    line: int = Field(..., ge=0, description="Line number where issue occurs")
    message: str = Field(..., min_length=1, description="Description of the issue")
    suggestion: str = Field(..., min_length=1, description="Suggested fix")
    code_snippet: Optional[str] = Field(None, description="Relevant code context")
    confidence: float = Field(0.8, ge=0.0, le=1.0, description="Confidence score for the issue")
    
    @validator('line')
    def validate_line_number(cls, v):
        if v < 0:
            raise ValueError('Line number must be non-negative')
        return v


class RecommendationModel(BaseModel):
    """Model for code improvement recommendations."""
    id: Optional[str] = Field(None, description="Unique identifier for the recommendation")
    area: RecommendationArea = Field(..., description="Area of improvement")
    message: str = Field(..., min_length=1, description="Recommendation message")
    impact: EffortLevel = Field(..., description="Expected impact of implementing this recommendation")
    effort: EffortLevel = Field(..., description="Effort required to implement")
    examples: List[str] = Field(default_factory=list, description="Code examples or references")
    
    @validator('examples')
    def validate_examples(cls, v):
        # Limit number of examples to prevent excessive data
        if len(v) > 5:
            return v[:5]
        return v


class AnalysisResultModel(BaseModel):
    """Model for complete analysis results."""
    summary: str = Field(..., min_length=1, description="Brief summary of analysis")
    issues: List[IssueModel] = Field(default_factory=list, description="List of issues found")
    recommendations: List[RecommendationModel] = Field(default_factory=list, description="List of recommendations")
    confidence: float = Field(0.8, ge=0.0, le=1.0, description="Overall confidence score")
    processing_time: float = Field(0.0, ge=0.0, description="Processing time in seconds")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of analysis")
    
    @validator('issues')
    def validate_issues_count(cls, v):
        # Reasonable limit on number of issues
        if len(v) > 100:
            return v[:100]
        return v
    
    @validator('recommendations')
    def validate_recommendations_count(cls, v):
        # Reasonable limit on number of recommendations
        if len(v) > 50:
            return v[:50]
        return v


class CodeChunkModel(BaseModel):
    """Model for code chunks used in analysis."""
    content: str = Field(..., min_length=1, description="Code content")
    start_line: int = Field(..., ge=1, description="Starting line number")
    end_line: int = Field(..., ge=1, description="Ending line number")
    context: str = Field(..., description="Context description for the chunk")
    language: str = Field(..., description="Programming language")
    
    @validator('end_line')
    def validate_line_range(cls, v, values):
        if 'start_line' in values and v < values['start_line']:
            raise ValueError('End line must be greater than or equal to start line')
        return v


class AnalysisContextModel(BaseModel):
    """Model for analysis context and configuration."""
    language: str = Field(..., description="Programming language")
    ruleset: List[str] = Field(default_factory=list, description="Analysis rules to apply")
    focus_areas: List[str] = Field(default_factory=list, description="Areas to focus analysis on")
    max_severity: SeverityLevel = Field(SeverityLevel.HIGH, description="Maximum severity to report")
    
    @validator('focus_areas')
    def validate_focus_areas(cls, v):
        valid_areas = {'security', 'performance', 'readability', 'maintainability', 'style'}
        return [area for area in v if area.lower() in valid_areas]


class AggregatedReportModel(BaseModel):
    """Model for aggregated analysis reports from multiple chunks."""
    report_id: str = Field(..., description="Unique report identifier")
    filename: str = Field(..., description="Original filename")
    language: str = Field(..., description="Programming language")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    chunks_analyzed: int = Field(..., ge=1, description="Number of code chunks analyzed")
    
    # Analysis results
    summary: str = Field(..., description="Overall analysis summary")
    issues: List[IssueModel] = Field(default_factory=list, description="All issues found")
    recommendations: List[RecommendationModel] = Field(default_factory=list, description="All recommendations")
    
    # Metrics
    total_issues: int = Field(0, ge=0, description="Total number of issues")
    high_severity_issues: int = Field(0, ge=0, description="Number of high severity issues")
    medium_severity_issues: int = Field(0, ge=0, description="Number of medium severity issues")
    low_severity_issues: int = Field(0, ge=0, description="Number of low severity issues")
    
    confidence: float = Field(0.8, ge=0.0, le=1.0, description="Overall confidence score")
    processing_time: float = Field(0.0, ge=0.0, description="Total processing time")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Report creation time")
    
    @validator('total_issues')
    def validate_total_issues(cls, v, values):
        # Ensure total matches sum of severity counts
        if all(key in values for key in ['high_severity_issues', 'medium_severity_issues', 'low_severity_issues']):
            expected_total = values['high_severity_issues'] + values['medium_severity_issues'] + values['low_severity_issues']
            if v != expected_total:
                return expected_total
        return v


class AnalysisRequestModel(BaseModel):
    """Model for analysis requests."""
    content: str = Field(..., min_length=1, description="Code content to analyze")
    language: str = Field(..., description="Programming language")
    filename: Optional[str] = Field(None, description="Original filename")
    context: Optional[AnalysisContextModel] = Field(None, description="Analysis context")
    async_processing: bool = Field(False, description="Whether to process asynchronously")


class AnalysisStatusModel(BaseModel):
    """Model for analysis status tracking."""
    report_id: str = Field(..., description="Report identifier")
    status: str = Field(..., description="Current status")
    progress: float = Field(0.0, ge=0.0, le=1.0, description="Progress percentage")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Status creation time")


class ValidationResultModel(BaseModel):
    """Model for validation results of analysis responses."""
    valid: bool = Field(..., description="Whether the analysis result is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Confidence in validation")
    
    @validator('errors')
    def validate_errors_count(cls, v):
        # Limit number of errors to prevent excessive data
        if len(v) > 20:
            return v[:20]
        return v


class LLMProviderStatusModel(BaseModel):
    """Model for LLM provider status."""
    provider_name: str = Field(..., description="Name of the LLM provider")
    configured: bool = Field(..., description="Whether provider is configured")
    active: bool = Field(..., description="Whether provider is currently active")
    last_used: Optional[datetime] = Field(None, description="Last time provider was used")
    error_count: int = Field(0, ge=0, description="Number of recent errors")
    success_rate: float = Field(1.0, ge=0.0, le=1.0, description="Success rate percentage")


class AnalysisMetricsModel(BaseModel):
    """Model for analysis performance metrics."""
    total_requests: int = Field(0, ge=0, description="Total analysis requests")
    successful_requests: int = Field(0, ge=0, description="Successful requests")
    failed_requests: int = Field(0, ge=0, description="Failed requests")
    average_processing_time: float = Field(0.0, ge=0.0, description="Average processing time")
    average_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Average confidence score")
    
    @validator('successful_requests')
    def validate_success_count(cls, v, values):
        if 'total_requests' in values and v > values['total_requests']:
            raise ValueError('Successful requests cannot exceed total requests')
        return v
    
    @validator('failed_requests')
    def validate_failure_count(cls, v, values):
        if 'total_requests' in values and 'successful_requests' in values:
            expected_failures = values['total_requests'] - values['successful_requests']
            if v != expected_failures:
                return expected_failures
        return v