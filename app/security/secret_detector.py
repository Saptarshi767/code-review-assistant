"""
Secret detection and redaction for uploaded code files.
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class DetectedSecret:
    """Information about a detected secret."""
    type: str
    line_number: int
    start_pos: int
    end_pos: int
    original_value: str
    redacted_value: str
    confidence: float


class SecretDetector:
    """
    Detects and redacts common secrets in source code.
    """
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, List[Tuple[re.Pattern, str, float]]]:
        """Initialize regex patterns for different types of secrets."""
        patterns = {
            "api_key": [
                (re.compile(r'(?i)api[_-]?key["\s]*[:=]["\s]*([a-zA-Z0-9_\-]{20,})', re.MULTILINE), "API_KEY_REDACTED", 0.9),
                (re.compile(r'(?i)apikey["\s]*[:=]["\s]*([a-zA-Z0-9_\-]{20,})', re.MULTILINE), "API_KEY_REDACTED", 0.9),
                (re.compile(r'(?i)key["\s]*[:=]["\s]*([a-zA-Z0-9_\-]{32,})', re.MULTILINE), "API_KEY_REDACTED", 0.7),
            ],
            "secret_key": [
                (re.compile(r'(?i)secret[_-]?key["\s]*[:=]["\s]*([a-zA-Z0-9_\-+/=]{20,})', re.MULTILINE), "SECRET_KEY_REDACTED", 0.9),
                (re.compile(r'(?i)secretkey["\s]*[:=]["\s]*([a-zA-Z0-9_\-+/=]{20,})', re.MULTILINE), "SECRET_KEY_REDACTED", 0.9),
            ],
            "password": [
                (re.compile(r'(?i)password["\s]*[:=]["\s]*([^\s"\']{8,})', re.MULTILINE), "PASSWORD_REDACTED", 0.8),
                (re.compile(r'(?i)passwd["\s]*[:=]["\s]*([^\s"\']{8,})', re.MULTILINE), "PASSWORD_REDACTED", 0.8),
                (re.compile(r'(?i)pwd["\s]*[:=]["\s]*([^\s"\']{8,})', re.MULTILINE), "PASSWORD_REDACTED", 0.7),
            ],
            "token": [
                (re.compile(r'(?i)token["\s]*[:=]["\s]*([a-zA-Z0-9_\-+/=]{20,})', re.MULTILINE), "TOKEN_REDACTED", 0.8),
                (re.compile(r'(?i)access[_-]?token["\s]*[:=]["\s]*([a-zA-Z0-9_\-+/=]{20,})', re.MULTILINE), "ACCESS_TOKEN_REDACTED", 0.9),
                (re.compile(r'(?i)bearer["\s]*[:=]["\s]*([a-zA-Z0-9_\-+/=]{20,})', re.MULTILINE), "BEARER_TOKEN_REDACTED", 0.9),
            ],
            "jwt": [
                (re.compile(r'eyJ[a-zA-Z0-9_\-+/=]+\.eyJ[a-zA-Z0-9_\-+/=]+\.[a-zA-Z0-9_\-+/=]+', re.MULTILINE), "JWT_TOKEN_REDACTED", 0.95),
            ],
            "aws_key": [
                (re.compile(r'AKIA[0-9A-Z]{16}', re.MULTILINE), "AWS_ACCESS_KEY_REDACTED", 0.95),
                (re.compile(r'(?i)aws[_-]?access[_-]?key[_-]?id["\s]*[:=]["\s]*([A-Z0-9]{20})', re.MULTILINE), "AWS_ACCESS_KEY_REDACTED", 0.9),
            ],
            "aws_secret": [
                (re.compile(r'(?i)aws[_-]?secret[_-]?access[_-]?key["\s]*[:=]["\s]*([a-zA-Z0-9+/]{40})', re.MULTILINE), "AWS_SECRET_KEY_REDACTED", 0.9),
            ],
            "github_token": [
                (re.compile(r'ghp_[a-zA-Z0-9]{36}', re.MULTILINE), "GITHUB_TOKEN_REDACTED", 0.95),
                (re.compile(r'gho_[a-zA-Z0-9]{36}', re.MULTILINE), "GITHUB_TOKEN_REDACTED", 0.95),
                (re.compile(r'ghu_[a-zA-Z0-9]{36}', re.MULTILINE), "GITHUB_TOKEN_REDACTED", 0.95),
            ],
            "private_key": [
                (re.compile(r'-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----', re.DOTALL | re.MULTILINE), "PRIVATE_KEY_REDACTED", 0.99),
                (re.compile(r'-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----', re.DOTALL | re.MULTILINE), "RSA_PRIVATE_KEY_REDACTED", 0.99),
                (re.compile(r'-----BEGIN EC PRIVATE KEY-----.*?-----END EC PRIVATE KEY-----', re.DOTALL | re.MULTILINE), "EC_PRIVATE_KEY_REDACTED", 0.99),
            ],
            "database_url": [
                (re.compile(r'(?i)database[_-]?url["\s]*[:=]["\s]*([a-zA-Z]+://[^\s"\']+)', re.MULTILINE), "DATABASE_URL_REDACTED", 0.8),
                (re.compile(r'(?i)db[_-]?url["\s]*[:=]["\s]*([a-zA-Z]+://[^\s"\']+)', re.MULTILINE), "DATABASE_URL_REDACTED", 0.8),
            ],
            "email": [
                (re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', re.MULTILINE), "EMAIL_REDACTED", 0.6),
            ],
            "ip_address": [
                (re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', re.MULTILINE), "IP_ADDRESS_REDACTED", 0.5),
            ]
        }
        
        return patterns
    
    def detect_secrets(self, content: str) -> List[DetectedSecret]:
        """
        Detect secrets in the given content.
        
        Args:
            content: Source code content to scan
            
        Returns:
            List of detected secrets
        """
        detected_secrets = []
        lines = content.split('\n')
        
        for secret_type, pattern_list in self.patterns.items():
            for pattern, redacted_value, confidence in pattern_list:
                for match in pattern.finditer(content):
                    # Find line number
                    line_number = content[:match.start()].count('\n') + 1
                    
                    # Skip if it looks like a comment or example
                    line_content = lines[line_number - 1] if line_number <= len(lines) else ""
                    if self._is_likely_example(line_content, match.group()):
                        continue
                    
                    detected_secret = DetectedSecret(
                        type=secret_type,
                        line_number=line_number,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        original_value=match.group(),
                        redacted_value=redacted_value,
                        confidence=confidence
                    )
                    
                    detected_secrets.append(detected_secret)
        
        # Remove duplicates and sort by position
        detected_secrets = self._remove_duplicates(detected_secrets)
        detected_secrets.sort(key=lambda x: x.start_pos)
        
        return detected_secrets
    
    def _is_likely_example(self, line_content: str, matched_value: str) -> bool:
        """Check if the detected secret is likely an example or placeholder."""
        line_lower = line_content.lower()
        value_lower = matched_value.lower()
        
        # Common example indicators
        example_indicators = [
            'example', 'sample', 'test', 'demo', 'placeholder', 'your_',
            'replace', 'change', 'todo', 'fixme', 'xxx', 'yyy', 'zzz'
        ]
        
        # Check if line contains example indicators
        for indicator in example_indicators:
            if indicator in line_lower or indicator in value_lower:
                return True
        
        # Check for repeated characters (like 'xxxxxxxxxx')
        if len(set(matched_value)) <= 3 and len(matched_value) > 10:
            return True
        
        # Check for obvious test patterns
        test_patterns = ['test123', 'password123', 'secret123', 'key123']
        for pattern in test_patterns:
            if pattern in value_lower:
                return True
        
        return False
    
    def _remove_duplicates(self, secrets: List[DetectedSecret]) -> List[DetectedSecret]:
        """Remove duplicate detections (same position, different patterns)."""
        seen_positions = set()
        unique_secrets = []
        
        for secret in secrets:
            position_key = (secret.start_pos, secret.end_pos)
            if position_key not in seen_positions:
                seen_positions.add(position_key)
                unique_secrets.append(secret)
            else:
                # Keep the one with higher confidence
                existing_idx = next(
                    i for i, s in enumerate(unique_secrets)
                    if s.start_pos == secret.start_pos and s.end_pos == secret.end_pos
                )
                if secret.confidence > unique_secrets[existing_idx].confidence:
                    unique_secrets[existing_idx] = secret
        
        return unique_secrets
    
    def redact_secrets(self, content: str, secrets: List[DetectedSecret]) -> str:
        """
        Redact detected secrets from content.
        
        Args:
            content: Original content
            secrets: List of detected secrets
            
        Returns:
            Content with secrets redacted
        """
        if not secrets:
            return content
        
        # Sort secrets by position (reverse order to maintain positions)
        secrets_sorted = sorted(secrets, key=lambda x: x.start_pos, reverse=True)
        
        redacted_content = content
        for secret in secrets_sorted:
            redacted_content = (
                redacted_content[:secret.start_pos] +
                secret.redacted_value +
                redacted_content[secret.end_pos:]
            )
        
        return redacted_content
    
    def scan_and_redact(self, content: str) -> Tuple[str, List[DetectedSecret]]:
        """
        Scan content for secrets and return redacted version.
        
        Args:
            content: Source code content to scan
            
        Returns:
            Tuple of (redacted_content, detected_secrets)
        """
        detected_secrets = self.detect_secrets(content)
        redacted_content = self.redact_secrets(content, detected_secrets)
        
        return redacted_content, detected_secrets


# Global secret detector instance
secret_detector = SecretDetector()