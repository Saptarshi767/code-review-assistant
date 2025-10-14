/**
 * API Client Module for Frontend-Backend Integration
 * Handles authentication, token storage, request interceptors, and global error handling
 */

class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.token = this.getStoredToken();
        this.requestInterceptors = [];
        this.responseInterceptors = [];
        this.errorHandlers = new Map();
        
        // Initialize default error handlers
        this.initializeDefaultErrorHandlers();
        
        console.log('API Client initialized');
    }

    /**
     * Get stored authentication token
     */
    getStoredToken() {
        try {
            // Try sessionStorage first (more secure for temporary sessions)
            let token = sessionStorage.getItem('auth_token');
            if (!token) {
                // Fallback to localStorage for persistent sessions
                token = localStorage.getItem('auth_token');
            }
            return token;
        } catch (error) {
            console.warn('Failed to retrieve stored token:', error);
            return null;
        }
    }

    /**
     * Store authentication token securely
     */
    setToken(token, persistent = false) {
        this.token = token;
        
        try {
            if (persistent) {
                localStorage.setItem('auth_token', token);
                // Also store in session for current session
                sessionStorage.setItem('auth_token', token);
            } else {
                // Only store in session storage
                sessionStorage.setItem('auth_token', token);
                // Remove from localStorage if it exists
                localStorage.removeItem('auth_token');
            }
            
            console.log('Token stored successfully');
        } catch (error) {
            console.error('Failed to store token:', error);
            throw new Error('Failed to store authentication token');
        }
    }

    /**
     * Clear stored authentication token
     */
    clearToken() {
        this.token = null;
        
        try {
            sessionStorage.removeItem('auth_token');
            localStorage.removeItem('auth_token');
            console.log('Token cleared successfully');
        } catch (error) {
            console.warn('Failed to clear stored token:', error);
        }
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.token;
    }

    /**
     * Add request interceptor
     */
    addRequestInterceptor(interceptor) {
        this.requestInterceptors.push(interceptor);
    }

    /**
     * Add response interceptor
     */
    addResponseInterceptor(interceptor) {
        this.responseInterceptors.push(interceptor);
    }

    /**
     * Add custom error handler for specific error types
     */
    addErrorHandler(errorType, handler) {
        this.errorHandlers.set(errorType, handler);
    }

    /**
     * Initialize default error handlers
     */
    initializeDefaultErrorHandlers() {
        // Network error handler
        this.addErrorHandler('network', (error) => {
            console.error('Network error:', error);
            this.showUserFriendlyError('Network connection failed. Please check your internet connection and try again.');
            return { retry: true, delay: 2000 };
        });

        // Authentication error handler
        this.addErrorHandler('auth', (error) => {
            console.error('Authentication error:', error);
            this.clearToken();
            this.showUserFriendlyError('Your session has expired. Please log in again.');
            // Optionally redirect to login
            return { retry: false };
        });

        // Server error handler
        this.addErrorHandler('server', (error) => {
            console.error('Server error:', error);
            this.showUserFriendlyError('Server is temporarily unavailable. Please try again in a few moments.');
            return { retry: true, delay: 5000 };
        });

        // Validation error handler
        this.addErrorHandler('validation', (error) => {
            console.error('Validation error:', error);
            this.showValidationErrors(error.details || []);
            return { retry: false };
        });

        // Rate limit error handler
        this.addErrorHandler('rateLimit', (error) => {
            console.error('Rate limit exceeded:', error);
            const retryAfter = error.retryAfter || 60;
            this.showUserFriendlyError(`Rate limit exceeded. Please try again in ${retryAfter} seconds.`);
            return { retry: true, delay: retryAfter * 1000 };
        });
    }

    /**
     * Process request through interceptors
     */
    async processRequest(url, options) {
        let processedOptions = { ...options };
        
        // Apply request interceptors
        for (const interceptor of this.requestInterceptors) {
            try {
                processedOptions = await interceptor(url, processedOptions);
            } catch (error) {
                console.error('Request interceptor error:', error);
            }
        }

        // Add authentication header if token exists
        if (this.token) {
            processedOptions.headers = {
                ...processedOptions.headers,
                'Authorization': `Bearer ${this.token}`
            };
        }

        // Add default headers
        processedOptions.headers = {
            'Content-Type': 'application/json',
            ...processedOptions.headers
        };

        return processedOptions;
    }

    /**
     * Process response through interceptors
     */
    async processResponse(response, originalUrl, originalOptions) {
        let processedResponse = response;
        
        // Apply response interceptors
        for (const interceptor of this.responseInterceptors) {
            try {
                processedResponse = await interceptor(processedResponse, originalUrl, originalOptions);
            } catch (error) {
                console.error('Response interceptor error:', error);
            }
        }

        return processedResponse;
    }

    /**
     * Handle API errors with retry logic
     */
    async handleError(error, url, options, attempt = 1, maxRetries = 3) {
        const errorType = this.categorizeError(error);
        const handler = this.errorHandlers.get(errorType);
        
        let shouldRetry = false;
        let retryDelay = 1000;
        
        if (handler) {
            const result = handler(error);
            shouldRetry = result.retry && attempt < maxRetries;
            retryDelay = result.delay || retryDelay;
        }

        if (shouldRetry) {
            console.log(`Retrying request (attempt ${attempt + 1}/${maxRetries}) after ${retryDelay}ms`);
            await this.delay(retryDelay);
            return this.makeRequest(url, options, attempt + 1, maxRetries);
        }

        throw error;
    }

    /**
     * Categorize error for appropriate handling
     */
    categorizeError(error) {
        if (!navigator.onLine || error.name === 'NetworkError') {
            return 'network';
        }
        
        if (error.status === 401 || error.status === 403) {
            return 'auth';
        }
        
        if (error.status === 429) {
            return 'rateLimit';
        }
        
        if (error.status >= 400 && error.status < 500) {
            return 'validation';
        }
        
        if (error.status >= 500) {
            return 'server';
        }
        
        return 'unknown';
    }

    /**
     * Make HTTP request with error handling and retries
     */
    async makeRequest(url, options = {}, attempt = 1, maxRetries = 3) {
        const fullUrl = this.baseURL + url;
        
        try {
            // Process request through interceptors
            const processedOptions = await this.processRequest(url, options);
            
            // Make the actual request
            const response = await fetch(fullUrl, processedOptions);
            
            // Process response through interceptors
            const processedResponse = await this.processResponse(response, url, options);
            
            // Handle non-ok responses
            if (!processedResponse.ok) {
                const errorData = await this.parseErrorResponse(processedResponse);
                const error = new Error(errorData.message || `HTTP ${processedResponse.status}`);
                error.status = processedResponse.status;
                error.details = errorData.details;
                error.retryAfter = processedResponse.headers.get('Retry-After');
                throw error;
            }
            
            return processedResponse;
            
        } catch (error) {
            return this.handleError(error, url, options, attempt, maxRetries);
        }
    }

    /**
     * Parse error response body
     */
    async parseErrorResponse(response) {
        try {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return { message: await response.text() };
            }
        } catch (error) {
            return { message: `HTTP ${response.status} ${response.statusText}` };
        }
    }

    /**
     * Utility method for delays
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Show user-friendly error message
     */
    showUserFriendlyError(message) {
        // Use enhanced notification system if available
        if (window.notificationManager) {
            window.notificationManager.error(message);
        } else {
            // Fallback to basic notification
            this.showNotification(message, 'error');
        }
        
        // Use existing live region for screen reader announcements
        if (window.announceError) {
            window.announceError(message);
        } else if (window.announceToScreenReader) {
            window.announceToScreenReader(message, 'assertive');
        }
    }

    /**
     * Show validation errors
     */
    showValidationErrors(errors) {
        if (Array.isArray(errors) && errors.length > 0) {
            const errorMessages = errors.map(error => error.message || error).join(', ');
            this.showUserFriendlyError(`Validation failed: ${errorMessages}`);
        }
    }

    /**
     * Show notification to user (enhanced version)
     */
    showNotification(message, type = 'info', options = {}) {
        // Use enhanced notification system if available
        if (window.notificationManager) {
            return window.notificationManager.show(message, type, options);
        }
        
        // Fallback to basic notification
        let notification = document.getElementById('api-notification');
        
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'api-notification';
            notification.className = 'api-notification';
            notification.setAttribute('role', 'alert');
            notification.setAttribute('aria-live', 'assertive');
            document.body.appendChild(notification);
        }
        
        notification.className = `api-notification ${type}`;
        notification.textContent = message;
        notification.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.style.display = 'none';
        }, 5000);
    }

    // HTTP Methods

    /**
     * GET request
     */
    async get(url, options = {}) {
        const response = await this.makeRequest(url, {
            method: 'GET',
            ...options
        });
        return response.json();
    }

    /**
     * POST request
     */
    async post(url, data = null, options = {}) {
        const requestOptions = {
            method: 'POST',
            ...options
        };
        
        if (data !== null) {
            if (data instanceof FormData) {
                // Don't set Content-Type for FormData, let browser set it
                delete requestOptions.headers?.['Content-Type'];
                requestOptions.body = data;
            } else {
                requestOptions.body = JSON.stringify(data);
            }
        }
        
        const response = await this.makeRequest(url, requestOptions);
        return response.json();
    }

    /**
     * PUT request
     */
    async put(url, data = null, options = {}) {
        const requestOptions = {
            method: 'PUT',
            ...options
        };
        
        if (data !== null) {
            requestOptions.body = JSON.stringify(data);
        }
        
        const response = await this.makeRequest(url, requestOptions);
        return response.json();
    }

    /**
     * DELETE request
     */
    async delete(url, options = {}) {
        const response = await this.makeRequest(url, {
            method: 'DELETE',
            ...options
        });
        return response.json();
    }

    // Authentication Methods

    /**
     * Create API key for authentication
     */
    async createApiKey(email, rateLimitTier = 'basic') {
        try {
            const response = await this.post('/api/auth/api-key', {
                email,
                rate_limit_tier: rateLimitTier
            });
            
            if (response.api_key) {
                this.setToken(response.api_key, true); // Store persistently
                this.showNotification('Authentication successful!', 'success');
                return response;
            }
            
            throw new Error('No API key received');
            
        } catch (error) {
            console.error('Failed to create API key:', error);
            throw error;
        }
    }

    /**
     * Logout user
     */
    logout() {
        this.clearToken();
        this.showNotification('Logged out successfully', 'success');
        
        // Optionally refresh the page or redirect
        // window.location.reload();
    }

    // File Upload Methods

    /**
     * Upload file for analysis
     */
    async uploadFile(file) {
        if (!file) {
            throw new Error('No file provided');
        }
        
        // Validate file type and size
        this.validateFile(file);
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await this.post('/api/review', formData);
            this.showNotification('File uploaded successfully!', 'success');
            return response;
        } catch (error) {
            console.error('File upload failed:', error);
            throw error;
        }
    }

    /**
     * Validate file before upload
     */
    validateFile(file) {
        const allowedTypes = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs', '.swift'];
        const maxSize = 10 * 1024 * 1024; // 10MB
        
        // Check file extension
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(extension)) {
            throw new Error(`File type ${extension} is not supported. Allowed types: ${allowedTypes.join(', ')}`);
        }
        
        // Check file size
        if (file.size > maxSize) {
            throw new Error(`File size (${(file.size / 1024 / 1024).toFixed(2)}MB) exceeds maximum allowed size (10MB)`);
        }
    }

    // Analysis Methods

    /**
     * Get analysis report by ID
     */
    async getAnalysisReport(reportId) {
        try {
            return await this.get(`/api/review/${reportId}`);
        } catch (error) {
            console.error('Failed to fetch analysis report:', error);
            throw error;
        }
    }

    /**
     * Poll for analysis completion
     */
    async pollAnalysisStatus(reportId, maxAttempts = 30, initialDelay = 1000) {
        let attempt = 0;
        let delay = initialDelay;
        
        while (attempt < maxAttempts) {
            try {
                const report = await this.getAnalysisReport(reportId);
                
                if (report.status === 'completed') {
                    this.showNotification('Analysis completed!', 'success');
                    return report;
                } else if (report.status === 'failed') {
                    throw new Error('Analysis failed');
                }
                
                // Continue polling
                await this.delay(delay);
                delay = Math.min(delay * 1.2, 10000); // Exponential backoff, max 10s
                attempt++;
                
            } catch (error) {
                console.error('Error polling analysis status:', error);
                throw error;
            }
        }
        
        throw new Error('Analysis timeout - please try again');
    }

    // Dashboard Methods

    /**
     * Get user dashboard metrics
     */
    async getDashboardMetrics() {
        try {
            return await this.get('/api/dashboard/metrics');
        } catch (error) {
            console.error('Failed to fetch dashboard metrics:', error);
            throw error;
        }
    }

    /**
     * Get analysis history
     */
    async getAnalysisHistory(limit = 10, offset = 0) {
        try {
            return await this.get(`/api/reviews?limit=${limit}&offset=${offset}`);
        } catch (error) {
            console.error('Failed to fetch analysis history:', error);
            throw error;
        }
    }

    /**
     * Get user dashboard metrics
     */
    async getDashboardMetrics() {
        try {
            return await this.get('/api/dashboard/metrics');
        } catch (error) {
            console.error('Failed to fetch dashboard metrics:', error);
            throw error;
        }
    }
}

// Create global API client instance
window.apiClient = new APIClient();

// Add default request interceptor for logging
window.apiClient.addRequestInterceptor(async (url, options) => {
    console.log(`API Request: ${options.method || 'GET'} ${url}`);
    return options;
});

// Add default response interceptor for logging
window.apiClient.addResponseInterceptor(async (response, url, options) => {
    console.log(`API Response: ${response.status} ${url}`);
    return response;
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIClient;
}