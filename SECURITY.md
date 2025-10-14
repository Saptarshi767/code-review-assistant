# Security Features

This document describes the security features implemented in the Code Review Assistant API.

## Authentication

### API Key Authentication

The API uses API key authentication for all protected endpoints. API keys can be provided in two ways:

1. **Authorization Header** (Bearer token):
   ```
   Authorization: Bearer your-api-key-here
   ```

2. **X-API-Key Header**:
   ```
   X-API-Key: your-api-key-here
   ```

### Getting an API Key

Create a new API key by calling the `/api/auth/api-key` endpoint:

```bash
curl -X POST http://localhost:8000/api/auth/api-key \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "rate_limit_tier": "standard"
  }'
```

### Rate Limiting

API keys are subject to rate limiting based on their tier:

- **Basic**: 5 requests per minute
- **Standard**: 10 requests per minute  
- **Premium**: 50 requests per minute

Rate limit information is included in response headers:
- `X-RateLimit-Limit`: Maximum requests per minute
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Timestamp when rate limit resets

### Default Test Keys

For development and testing, the following API keys are pre-configured:

- **Admin Key**: `test-admin-key-12345` (Premium tier)
- **Standard Key**: `test-standard-key-67890` (Standard tier)

## Secret Detection and Redaction

The system automatically detects and redacts sensitive information in uploaded code files:

### Detected Secret Types

- **API Keys**: Various API key patterns
- **Passwords**: Password fields and variables
- **Tokens**: Access tokens, JWT tokens, Bearer tokens
- **AWS Credentials**: AWS access keys and secret keys
- **GitHub Tokens**: GitHub personal access tokens
- **Private Keys**: RSA, EC, and other private keys
- **Database URLs**: Connection strings with credentials
- **Email Addresses**: Email addresses (low confidence)
- **IP Addresses**: IP addresses (low confidence)

### Redaction Process

1. **Detection**: Content is scanned using regex patterns
2. **Confidence Scoring**: Each detection has a confidence score (0.0-1.0)
3. **Example Filtering**: Obvious examples and placeholders are filtered out
4. **Redaction**: Detected secrets are replaced with placeholder values
5. **Reporting**: Redacted secrets are logged for review

### Example

Original code:
```python
API_KEY = "sk-1234567890abcdef1234567890abcdef"
password = "mySecretPassword123"
```

Redacted code:
```python
API_KEY = "API_KEY_REDACTED"
password = "PASSWORD_REDACTED"
```

## Security Headers

The API includes comprehensive security headers in all responses:

### Content Security Policy (CSP)
Prevents XSS attacks by controlling resource loading:
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; ...
```

### Frame Protection
Prevents clickjacking attacks:
```
X-Frame-Options: DENY
```

### Content Type Protection
Prevents MIME type sniffing:
```
X-Content-Type-Options: nosniff
```

### XSS Protection
Enables browser XSS filtering:
```
X-XSS-Protection: 1; mode=block
```

### Referrer Policy
Controls referrer information:
```
Referrer-Policy: strict-origin-when-cross-origin
```

### Permissions Policy
Restricts browser features:
```
Permissions-Policy: geolocation=(), microphone=(), camera=(), ...
```

## HTTPS/TLS Configuration

For production deployment, configure HTTPS using environment variables:

```bash
# Certificate files
TLS_CERT_FILE=/path/to/certificate.pem
TLS_KEY_FILE=/path/to/private_key.pem
TLS_CA_FILE=/path/to/ca_bundle.pem  # Optional
```

### Self-Signed Certificates

For development, you can generate self-signed certificates:

```python
from app.security.tls_config import tls_config
tls_config.generate_self_signed_cert("cert.pem", "key.pem")
```

## CORS Configuration

Cross-Origin Resource Sharing (CORS) is configured based on environment settings:

```bash
# Allowed origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Enable/disable CORS
CORS_ENABLED=true
```

## Testing Security Features

Use the provided test script to verify security features:

```bash
python test_auth.py
```

This will test:
- API key creation and validation
- Authentication endpoints
- Rate limiting
- Security headers
- Unauthorized access handling

## Security Best Practices

### For Development
1. Use the provided test API keys
2. Keep secrets out of code (use environment variables)
3. Test with the security test script
4. Review redacted content before analysis

### For Production
1. Generate strong, unique API keys
2. Configure HTTPS/TLS with valid certificates
3. Set appropriate CORS origins
4. Monitor rate limiting and usage
5. Regularly rotate API keys
6. Use environment variables for all secrets
7. Enable HSTS headers for HTTPS
8. Consider using a reverse proxy (nginx, Apache)
9. Implement proper logging and monitoring
10. Regular security audits and updates

## Security Considerations

### Data Privacy
- Code content is processed by external LLM services
- Secrets are redacted before LLM processing
- Consider using local LLM for sensitive code
- Reports are stored locally (not sent to external services)

### Rate Limiting
- Prevents abuse and DoS attacks
- Configurable per user tier
- Headers provide transparency
- Consider implementing IP-based limiting for additional protection

### Input Validation
- File size limits (10MB default)
- File type validation
- Content encoding validation
- Zip file extraction limits

### Error Handling
- Detailed error messages for debugging
- No sensitive information in error responses
- Proper HTTP status codes
- Request ID tracking for debugging