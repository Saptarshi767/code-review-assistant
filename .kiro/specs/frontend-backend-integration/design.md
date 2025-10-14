# Design Document

## Overview

This design document outlines the integration of the existing glassmorphism landing page frontend with the Python FastAPI backend. The integration will transform the static frontend into a fully functional code review application by connecting interactive elements to backend APIs for file upload, code analysis, authentication, and real-time results display.

## Architecture

### Frontend Architecture
- **Static Assets**: HTML, CSS, and JavaScript files served by FastAPI
- **Client-Side State Management**: Vanilla JavaScript with local state management
- **API Communication**: Fetch API for HTTP requests to backend endpoints
- **Real-time Updates**: Polling-based updates for analysis status
- **Error Handling**: Graceful degradation with user-friendly error messages

### Backend Integration Points
- **File Upload API**: `/api/review` endpoint for code file uploads
- **Analysis Results API**: `/api/review/{report_id}` for fetching analysis results
- **Authentication API**: `/api/auth` endpoints for user authentication
- **Dashboard API**: `/api/dashboard` for user metrics and history
- **System Limits API**: `/api/limits` for frontend validation

### Data Flow
1. User uploads file through frontend interface
2. Frontend validates file and sends to backend API
3. Backend processes file and returns report ID
4. Frontend polls for analysis completion
5. Results are displayed in real-time UI updates
6. User can view history and metrics through dashboard

## Components and Interfaces

### 1. File Upload Component
**Location**: Code editor panel in `index.html`
**Functionality**:
- File picker integration with drag-and-drop support
- Client-side validation (file type, size)
- Progress indication during upload
- Error handling and user feedback

**API Integration**:
```javascript
// Upload file to backend
const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/api/review', {
    method: 'POST',
    body: formData,
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`
    }
  });
  
  return await response.json();
};
```

### 2. Code Analysis Component
**Location**: Results panel in `index.html`
**Functionality**:
- Trigger analysis on uploaded or sample code
- Display loading states during processing
- Real-time results updates
- Issue highlighting in code editor

**API Integration**:
```javascript
// Poll for analysis results
const pollAnalysisResults = async (reportId) => {
  const response = await fetch(`/api/review/${reportId}`);
  const report = await response.json();
  
  if (report.status === 'completed') {
    updateAnalysisResults(report);
    return true; // Stop polling
  }
  return false; // Continue polling
};
```

### 3. Authentication Component
**Location**: Navigation header and protected features
**Functionality**:
- Login/logout functionality
- Token storage and management
- Protected route handling
- User profile display

**API Integration**:
```javascript
// Create API key for authentication
const createApiKey = async (email) => {
  const response = await fetch('/api/auth/api-key', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, rate_limit_tier: 'basic' })
  });
  
  return await response.json();
};
```

### 4. Dashboard Component
**Location**: Analysis showcase section
**Functionality**:
- Display user metrics and trends
- Analysis history
- Export functionality
- Performance charts

**API Integration**:
```javascript
// Fetch user dashboard data
const fetchDashboardData = async () => {
  const response = await fetch('/api/dashboard/metrics', {
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`
    }
  });
  
  return await response.json();
};
```

## Data Models

### Frontend State Models
```javascript
// Application state
const AppState = {
  user: null,
  currentReport: null,
  analysisHistory: [],
  isLoading: false,
  error: null
};

// File upload state
const FileUploadState = {
  selectedFile: null,
  uploadProgress: 0,
  isUploading: false,
  validationErrors: []
};

// Analysis state
const AnalysisState = {
  reportId: null,
  status: 'idle', // idle, processing, completed, failed
  results: null,
  pollingInterval: null
};
```

### API Response Models
```javascript
// Review response from backend
const ReviewResponse = {
  report_id: string,
  status: 'processing' | 'completed' | 'failed',
  filename: string,
  language: string,
  estimated_time?: number
};

// Analysis report from backend
const Report = {
  report_id: string,
  filename: string,
  language: string,
  status: string,
  created_at: string,
  summary: {
    total_issues: number,
    critical_issues: number,
    code_quality_score: number
  },
  issues: Array<{
    type: string,
    severity: 'high' | 'medium' | 'low',
    line: number,
    message: string,
    suggestion: string,
    code_snippet: string
  }>,
  recommendations: Array<{
    area: string,
    message: string,
    impact: string,
    effort: string
  }>
};
```

## Error Handling

### Client-Side Error Handling
1. **Network Errors**: Display offline message and retry options
2. **Validation Errors**: Show inline validation feedback
3. **API Errors**: Parse backend error responses and show user-friendly messages
4. **Authentication Errors**: Redirect to login or show auth prompts

### Error Display Strategy
- **Toast Notifications**: For temporary errors and success messages
- **Inline Validation**: For form and input errors
- **Error States**: For component-level errors with retry options
- **Fallback UI**: For critical failures with graceful degradation

### Error Recovery
```javascript
// Retry mechanism for failed requests
const retryRequest = async (requestFn, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
};
```

## Testing Strategy

### Unit Testing
- **API Integration Functions**: Test request/response handling
- **State Management**: Test state updates and transitions
- **Validation Logic**: Test client-side validation rules
- **Error Handling**: Test error scenarios and recovery

### Integration Testing
- **File Upload Flow**: End-to-end file upload and processing
- **Authentication Flow**: Login, token management, and protected routes
- **Analysis Flow**: Code analysis from upload to results display
- **Dashboard Integration**: User data fetching and display

### User Acceptance Testing
- **Cross-browser Compatibility**: Test on major browsers
- **Responsive Design**: Test on mobile and desktop devices
- **Accessibility**: Test with screen readers and keyboard navigation
- **Performance**: Test with large files and slow networks

### Testing Tools
- **Frontend Testing**: Jest for unit tests, Cypress for E2E tests
- **API Testing**: Postman/Newman for API endpoint testing
- **Performance Testing**: Lighthouse for web vitals
- **Accessibility Testing**: axe-core for automated accessibility checks

## Security Considerations

### Authentication Security
- **Token Storage**: Use secure storage (httpOnly cookies or secure localStorage)
- **Token Expiration**: Handle token refresh and expiration gracefully
- **CSRF Protection**: Include CSRF tokens for state-changing operations
- **Rate Limiting**: Respect backend rate limits and show appropriate feedback

### Data Security
- **Input Validation**: Validate all user inputs on both client and server
- **File Upload Security**: Validate file types, sizes, and content
- **XSS Prevention**: Sanitize all user-generated content
- **Content Security Policy**: Implement CSP headers for script execution

### API Security
- **HTTPS Only**: Ensure all API calls use HTTPS in production
- **API Key Protection**: Never expose API keys in client-side code
- **Request Signing**: Implement request signing for sensitive operations
- **Error Information**: Avoid exposing sensitive information in error messages

## Performance Optimizations

### Frontend Performance
- **Code Splitting**: Load components on demand
- **Asset Optimization**: Minify and compress CSS/JS files
- **Image Optimization**: Use WebP format with fallbacks
- **Caching Strategy**: Implement service worker for offline functionality

### API Performance
- **Request Batching**: Batch multiple API calls when possible
- **Response Caching**: Cache non-sensitive API responses
- **Polling Optimization**: Use exponential backoff for status polling
- **Lazy Loading**: Load dashboard data only when needed

### Real-time Updates
```javascript
// Optimized polling with exponential backoff
const pollWithBackoff = async (reportId, maxAttempts = 30) => {
  let attempt = 0;
  let delay = 1000; // Start with 1 second
  
  while (attempt < maxAttempts) {
    const completed = await pollAnalysisResults(reportId);
    if (completed) return;
    
    await new Promise(resolve => setTimeout(resolve, delay));
    delay = Math.min(delay * 1.5, 10000); // Max 10 seconds
    attempt++;
  }
  
  throw new Error('Analysis timeout');
};
```

## Accessibility Implementation

### ARIA Integration
- **Live Regions**: Announce analysis status changes
- **Progress Indicators**: Accessible progress bars and loading states
- **Error Announcements**: Screen reader announcements for errors
- **Focus Management**: Proper focus handling during state changes

### Keyboard Navigation
- **Tab Order**: Logical tab sequence through interactive elements
- **Keyboard Shortcuts**: Implement common shortcuts (Ctrl+U for upload)
- **Focus Indicators**: Clear visual focus indicators
- **Skip Links**: Allow users to skip to main content

### Screen Reader Support
- **Semantic HTML**: Use proper heading hierarchy and landmarks
- **Alt Text**: Descriptive alt text for all images and icons
- **Form Labels**: Proper labels and descriptions for all form elements
- **Status Updates**: Announce important state changes

## Mobile Responsiveness

### Responsive Design
- **Breakpoints**: Mobile-first responsive design
- **Touch Interactions**: Optimize for touch interfaces
- **Viewport Optimization**: Proper viewport meta tags
- **Performance**: Optimize for mobile network conditions

### Mobile-Specific Features
- **File Upload**: Support mobile file picker and camera
- **Gestures**: Implement swipe gestures for navigation
- **Offline Support**: Basic offline functionality with service worker
- **Progressive Web App**: PWA features for mobile app-like experience