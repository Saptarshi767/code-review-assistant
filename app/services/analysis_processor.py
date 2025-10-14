"""
Service for processing and validating LLM analysis results.
"""

import json
import logging
import re
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from app.models.analysis_models import (
    AnalysisResultModel, IssueModel, RecommendationModel, 
    AggregatedReportModel, ValidationResultModel,
    IssueType, SeverityLevel, RecommendationArea, EffortLevel
)

logger = logging.getLogger(__name__)


class AnalysisProcessor:
    """Service for processing and validating analysis results."""
    
    def __init__(self):
        self.confidence_threshold = 0.3  # Minimum confidence to include results
        self.max_issues_per_chunk = 20   # Limit issues per chunk
        self.max_recommendations_per_chunk = 10  # Limit recommendations per chunk
    
    def parse_llm_response(self, response: str, processing_time: float = 0.0) -> AnalysisResultModel:
        """Parse LLM JSON response into structured AnalysisResult."""
        try:
            # Clean and extract JSON from response
            cleaned_response = self._clean_json_response(response)
            data = json.loads(cleaned_response)
            
            # Validate and parse issues
            issues = self._parse_issues(data.get('issues', []))
            
            # Validate and parse recommendations
            recommendations = self._parse_recommendations(data.get('recommendations', []))
            
            # Calculate overall confidence
            confidence = self._calculate_confidence(issues, recommendations, data)
            
            return AnalysisResultModel(
                summary=data.get('summary', 'Analysis completed'),
                issues=issues,
                recommendations=recommendations,
                confidence=confidence,
                processing_time=processing_time
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.debug(f"Raw response: {response}")
            
            # Return fallback result with parsing error
            return AnalysisResultModel(
                summary="Analysis completed with parsing errors",
                issues=[],
                recommendations=[],
                confidence=0.1,
                processing_time=processing_time
            )
    
    def _clean_json_response(self, response: str) -> str:
        """Clean LLM response to extract valid JSON."""
        response = response.strip()
        
        # Remove markdown code blocks
        if response.startswith('```json'):
            response = response[7:]
        elif response.startswith('```'):
            response = response[3:]
        
        if response.endswith('```'):
            response = response[:-3]
        
        # Remove any text before the first {
        json_start = response.find('{')
        if json_start > 0:
            response = response[json_start:]
        
        # Remove any text after the last }
        json_end = response.rfind('}')
        if json_end > 0:
            response = response[:json_end + 1]
        
        return response.strip()
    
    def _parse_issues(self, issues_data: List[Dict[str, Any]]) -> List[IssueModel]:
        """Parse and validate issues from LLM response."""
        issues = []
        
        for issue_data in issues_data[:self.max_issues_per_chunk]:
            try:
                # Validate and normalize issue type
                issue_type = self._normalize_issue_type(issue_data.get('type', 'unknown'))
                
                # Validate and normalize severity
                severity = self._normalize_severity(issue_data.get('severity', 'medium'))
                
                # Validate line number
                line = max(0, int(issue_data.get('line', 0)))
                
                # Validate confidence
                confidence = max(0.0, min(1.0, float(issue_data.get('confidence', 0.8))))
                
                # Skip issues with very low confidence
                if confidence < self.confidence_threshold:
                    continue
                
                issue = IssueModel(
                    id=str(uuid.uuid4()),
                    type=issue_type,
                    severity=severity,
                    line=line,
                    message=str(issue_data.get('message', '')).strip(),
                    suggestion=str(issue_data.get('suggestion', '')).strip(),
                    code_snippet=issue_data.get('code_snippet'),
                    confidence=confidence
                )
                
                # Only add if message and suggestion are not empty
                if issue.message and issue.suggestion:
                    issues.append(issue)
                    
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse issue: {e}")
                continue
        
        return issues
    
    def _parse_recommendations(self, recommendations_data: List[Dict[str, Any]]) -> List[RecommendationModel]:
        """Parse and validate recommendations from LLM response."""
        recommendations = []
        
        for rec_data in recommendations_data[:self.max_recommendations_per_chunk]:
            try:
                # Validate and normalize area
                area = self._normalize_recommendation_area(rec_data.get('area', 'general'))
                
                # Validate and normalize impact/effort
                impact = self._normalize_effort_level(rec_data.get('impact', 'medium'))
                effort = self._normalize_effort_level(rec_data.get('effort', 'medium'))
                
                # Parse examples
                examples = rec_data.get('examples', [])
                if isinstance(examples, list):
                    examples = [str(ex).strip() for ex in examples if str(ex).strip()]
                else:
                    examples = []
                
                recommendation = RecommendationModel(
                    id=str(uuid.uuid4()),
                    area=area,
                    message=str(rec_data.get('message', '')).strip(),
                    impact=impact,
                    effort=effort,
                    examples=examples[:5]  # Limit examples
                )
                
                # Only add if message is not empty
                if recommendation.message:
                    recommendations.append(recommendation)
                    
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse recommendation: {e}")
                continue
        
        return recommendations
    
    def _normalize_issue_type(self, type_str: str) -> IssueType:
        """Normalize issue type string to enum value."""
        type_str = str(type_str).lower().strip()
        
        type_mapping = {
            'security': IssueType.SECURITY,
            'bug': IssueType.BUG,
            'performance': IssueType.PERFORMANCE,
            'style': IssueType.STYLE,
            'maintainability': IssueType.MAINTAINABILITY,
            'maintenance': IssueType.MAINTAINABILITY,
            'readability': IssueType.STYLE,
            'formatting': IssueType.STYLE,
            'vulnerability': IssueType.SECURITY,
            'error': IssueType.BUG,
            'defect': IssueType.BUG,
            'optimization': IssueType.PERFORMANCE,
            'efficiency': IssueType.PERFORMANCE
        }
        
        return type_mapping.get(type_str, IssueType.UNKNOWN)
    
    def _normalize_severity(self, severity_str: str) -> SeverityLevel:
        """Normalize severity string to enum value."""
        severity_str = str(severity_str).lower().strip()
        
        severity_mapping = {
            'high': SeverityLevel.HIGH,
            'critical': SeverityLevel.HIGH,
            'major': SeverityLevel.HIGH,
            'medium': SeverityLevel.MEDIUM,
            'moderate': SeverityLevel.MEDIUM,
            'normal': SeverityLevel.MEDIUM,
            'low': SeverityLevel.LOW,
            'minor': SeverityLevel.LOW,
            'trivial': SeverityLevel.LOW
        }
        
        return severity_mapping.get(severity_str, SeverityLevel.MEDIUM)
    
    def _normalize_recommendation_area(self, area_str: str) -> RecommendationArea:
        """Normalize recommendation area string to enum value."""
        area_str = str(area_str).lower().strip()
        
        area_mapping = {
            'readability': RecommendationArea.READABILITY,
            'modularity': RecommendationArea.MODULARITY,
            'performance': RecommendationArea.PERFORMANCE,
            'security': RecommendationArea.SECURITY,
            'testing': RecommendationArea.TESTING,
            'test': RecommendationArea.TESTING,
            'tests': RecommendationArea.TESTING,
            'structure': RecommendationArea.MODULARITY,
            'organization': RecommendationArea.MODULARITY,
            'optimization': RecommendationArea.PERFORMANCE,
            'efficiency': RecommendationArea.PERFORMANCE,
            'style': RecommendationArea.READABILITY,
            'formatting': RecommendationArea.READABILITY,
            'documentation': RecommendationArea.READABILITY,
            'general': RecommendationArea.GENERAL
        }
        
        return area_mapping.get(area_str, RecommendationArea.GENERAL)
    
    def _normalize_effort_level(self, effort_str: str) -> EffortLevel:
        """Normalize effort level string to enum value."""
        effort_str = str(effort_str).lower().strip()
        
        effort_mapping = {
            'high': EffortLevel.HIGH,
            'large': EffortLevel.HIGH,
            'significant': EffortLevel.HIGH,
            'major': EffortLevel.HIGH,
            'medium': EffortLevel.MEDIUM,
            'moderate': EffortLevel.MEDIUM,
            'normal': EffortLevel.MEDIUM,
            'low': EffortLevel.LOW,
            'small': EffortLevel.LOW,
            'minor': EffortLevel.LOW,
            'trivial': EffortLevel.LOW
        }
        
        return effort_mapping.get(effort_str, EffortLevel.MEDIUM)
    
    def _calculate_confidence(self, issues: List[IssueModel], 
                            recommendations: List[RecommendationModel], 
                            raw_data: Dict[str, Any]) -> float:
        """Calculate overall confidence score for analysis result."""
        if not issues and not recommendations:
            return 0.5  # Neutral confidence for empty results
        
        # Calculate average confidence from issues
        issue_confidence = 0.0
        if issues:
            issue_confidence = sum(issue.confidence for issue in issues) / len(issues)
        
        # Recommendations don't have confidence, so use a default
        rec_confidence = 0.8 if recommendations else 0.0
        
        # Weight issues more heavily than recommendations
        if issues and recommendations:
            overall_confidence = (issue_confidence * 0.7) + (rec_confidence * 0.3)
        elif issues:
            overall_confidence = issue_confidence
        else:
            overall_confidence = rec_confidence
        
        return max(0.0, min(1.0, overall_confidence))
    
    def validate_analysis_result(self, result: AnalysisResultModel) -> ValidationResultModel:
        """Validate an analysis result for quality and completeness."""
        errors = []
        warnings = []
        
        # Check summary quality
        if not result.summary or len(result.summary.strip()) < 10:
            errors.append("Summary is too short or empty")
        
        # Validate issues
        for i, issue in enumerate(result.issues):
            if not issue.message:
                errors.append(f"Issue {i+1} has empty message")
            if not issue.suggestion:
                errors.append(f"Issue {i+1} has empty suggestion")
            if issue.line < 0:
                errors.append(f"Issue {i+1} has invalid line number")
            if issue.confidence < 0.3:
                warnings.append(f"Issue {i+1} has low confidence ({issue.confidence:.2f})")
        
        # Validate recommendations
        for i, rec in enumerate(result.recommendations):
            if not rec.message:
                errors.append(f"Recommendation {i+1} has empty message")
        
        # Check overall confidence
        if result.confidence < 0.3:
            warnings.append(f"Overall confidence is low ({result.confidence:.2f})")
        
        # Calculate validation confidence
        validation_confidence = 1.0
        if errors:
            validation_confidence -= len(errors) * 0.2
        if warnings:
            validation_confidence -= len(warnings) * 0.1
        
        validation_confidence = max(0.0, min(1.0, validation_confidence))
        
        return ValidationResultModel(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            confidence_score=validation_confidence
        )
    
    def aggregate_results(self, results: List[AnalysisResultModel], 
                         filename: str, language: str, file_size: int) -> AggregatedReportModel:
        """Aggregate multiple analysis results into a single report."""
        if not results:
            return AggregatedReportModel(
                report_id=str(uuid.uuid4()),
                filename=filename,
                language=language,
                file_size=file_size,
                chunks_analyzed=0,
                summary="No analysis results to aggregate",
                issues=[],
                recommendations=[],
                total_issues=0,
                high_severity_issues=0,
                medium_severity_issues=0,
                low_severity_issues=0,
                confidence=0.0,
                processing_time=0.0
            )
        
        # Combine all issues and recommendations
        all_issues = []
        all_recommendations = []
        total_processing_time = 0.0
        
        for result in results:
            all_issues.extend(result.issues)
            all_recommendations.extend(result.recommendations)
            total_processing_time += result.processing_time
        
        # Deduplicate similar issues and recommendations
        unique_issues = self._deduplicate_issues(all_issues)
        unique_recommendations = self._deduplicate_recommendations(all_recommendations)
        
        # Calculate severity counts
        high_count = len([i for i in unique_issues if i.severity == SeverityLevel.HIGH])
        medium_count = len([i for i in unique_issues if i.severity == SeverityLevel.MEDIUM])
        low_count = len([i for i in unique_issues if i.severity == SeverityLevel.LOW])
        
        # Create aggregated summary
        summary = self._create_aggregated_summary(
            len(results), len(unique_issues), high_count, medium_count, low_count, len(unique_recommendations)
        )
        
        # Calculate average confidence
        avg_confidence = sum(r.confidence for r in results) / len(results)
        
        return AggregatedReportModel(
            report_id=str(uuid.uuid4()),
            filename=filename,
            language=language,
            file_size=file_size,
            chunks_analyzed=len(results),
            summary=summary,
            issues=unique_issues,
            recommendations=unique_recommendations,
            total_issues=len(unique_issues),
            high_severity_issues=high_count,
            medium_severity_issues=medium_count,
            low_severity_issues=low_count,
            confidence=avg_confidence,
            processing_time=total_processing_time
        )
    
    def _deduplicate_issues(self, issues: List[IssueModel]) -> List[IssueModel]:
        """Remove duplicate or very similar issues."""
        unique_issues = []
        seen_signatures = set()
        
        for issue in issues:
            # Create signature for deduplication
            signature = self._create_issue_signature(issue)
            
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_issues.append(issue)
        
        return unique_issues
    
    def _deduplicate_recommendations(self, recommendations: List[RecommendationModel]) -> List[RecommendationModel]:
        """Remove duplicate or very similar recommendations."""
        unique_recommendations = []
        seen_signatures = set()
        
        for rec in recommendations:
            # Create signature for deduplication
            signature = self._create_recommendation_signature(rec)
            
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def _create_issue_signature(self, issue: IssueModel) -> str:
        """Create a signature for issue deduplication."""
        # Normalize message for comparison
        normalized_message = re.sub(r'\s+', ' ', issue.message.lower().strip())
        
        # Create signature from type, severity, and normalized message
        return f"{issue.type.value}:{issue.severity.value}:{normalized_message[:50]}"
    
    def _create_recommendation_signature(self, recommendation: RecommendationModel) -> str:
        """Create a signature for recommendation deduplication."""
        # Normalize message for comparison
        normalized_message = re.sub(r'\s+', ' ', recommendation.message.lower().strip())
        
        # Create signature from area and normalized message
        return f"{recommendation.area.value}:{normalized_message[:50]}"
    
    def _create_aggregated_summary(self, chunks_count: int, issues_count: int, 
                                 high_count: int, medium_count: int, low_count: int, 
                                 recommendations_count: int) -> str:
        """Create a summary for aggregated results."""
        summary_parts = [
            f"Analysis of {chunks_count} code chunk{'s' if chunks_count != 1 else ''} completed."
        ]
        
        if issues_count > 0:
            severity_details = []
            if high_count > 0:
                severity_details.append(f"{high_count} high")
            if medium_count > 0:
                severity_details.append(f"{medium_count} medium")
            if low_count > 0:
                severity_details.append(f"{low_count} low")
            
            severity_text = ", ".join(severity_details) + " severity"
            summary_parts.append(f"Found {issues_count} issue{'s' if issues_count != 1 else ''}: {severity_text}.")
        else:
            summary_parts.append("No issues found.")
        
        if recommendations_count > 0:
            summary_parts.append(f"{recommendations_count} improvement recommendation{'s' if recommendations_count != 1 else ''} provided.")
        
        return " ".join(summary_parts)


# Global analysis processor instance
analysis_processor = AnalysisProcessor()