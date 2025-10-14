/**
 * Enhanced Accessibility Features for AI Code Reviewer
 * Comprehensive error handling, loading states, and keyboard navigation
 */

/**
 * Enhanced Loading State Management
 */
class LoadingStateManager {
    constructor() {
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.loadingTitle = document.getElementById('loading-title');
        this.loadingDescription = document.getElementById('loading-description');
        this.progressBar = document.querySelector('.loading-progress-bar');
        this.progressElement = document.querySelector('.loading-progress');
        this.isLoading = false;
        this.currentProgress = 0;
        
        // Initialize loading states
        this.initializeLoadingStates();
    }
    
    initializeLoadingStates() {
        // Ensure loading overlay is properly hidden initially
        if (this.loadingOverlay) {
            this.loadingOverlay.setAttribute('aria-hidden', 'true');
            this.loadingOverlay.classList.remove('active');
        }
    }
    
    show(title = 'Processing...', description = 'Please wait', showProgress = false) {
        if (!this.loadingOverlay) return;
        
        this.isLoading = true;
        this.currentProgress = 0;
        
        // Update content
        if (this.loadingTitle) this.loadingTitle.textContent = title;
        if (this.loadingDescription) this.loadingDescription.textContent = description;
        
        // Show/hide progress bar
        if (this.progressElement) {
            this.progressElement.style.display = showProgress ? 'block' : 'none';
        }
        
        // Reset progress
        this.updateProgress(0);
        
        // Show overlay
        this.loadingOverlay.classList.add('active');
        this.loadingOverlay.setAttribute('aria-hidden', 'false');
        
        // Announce to screen readers
        if (window.announceStatus) {
            window.announceStatus(`${title}. ${description}`);
        }
        
        // Trap focus in loading overlay
        this.trapFocusInOverlay();
        
        console.log('Loading state shown:', { title, description, showProgress });
    }
    
    hide() {
        if (!this.loadingOverlay || !this.isLoading) return;
        
        this.isLoading = false;
        
        // Hide overlay
        this.loadingOverlay.classList.remove('active');
        this.loadingOverlay.setAttribute('aria-hidden', 'true');
        
        // Restore focus
        this.restoreFocus();
        
        console.log('Loading state hidden');
    }
    
    updateProgress(percentage, message = null) {
        if (!this.progressBar || !this.isLoading) return;
        
        this.currentProgress = Math.max(0, Math.min(100, percentage));
        
        // Update visual progress
        this.progressBar.style.width = `${this.currentProgress}%`;
        
        // Update ARIA attributes
        if (this.progressElement) {
            this.progressElement.setAttribute('aria-valuenow', this.currentProgress);
        }
        
        // Update description if message provided
        if (message && this.loadingDescription) {
            this.loadingDescription.textContent = message;
        }
        
        // Announce progress milestones
        if (this.currentProgress % 25 === 0 && this.currentProgress > 0) {
            if (window.announceProgress) {
                window.announceProgress(message || 'Processing', this.currentProgress);
            }
        }
        
        console.log('Progress updated:', { percentage: this.currentProgress, message });
    }
    
    trapFocusInOverlay() {
        // Store currently focused element
        this.previouslyFocused = document.activeElement;
        
        // Focus the loading overlay
        if (this.loadingOverlay) {
            this.loadingOverlay.focus();
        }
    }
    
    restoreFocus() {
        // Restore focus to previously focused element
        if (this.previouslyFocused && typeof this.previouslyFocused.focus === 'function') {
            try {
                this.previouslyFocused.focus();
            } catch (error) {
                console.warn('Could not restore focus:', error);
            }
        }
    }
}

/**
 * Enhanced Notification System
 */
class NotificationManager {
    constructor() {
        this.container = document.getElementById('notification-container');
        this.notifications = new Map();
        this.notificationId = 0;
        
        // Ensure container exists
        if (!this.container) {
            this.createContainer();
        }
        
        console.log('Notification manager initialized');
    }
    
    createContainer() {
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.className = 'notification-container';
        this.container.setAttribute('aria-live', 'polite');
        this.container.setAttribute('aria-atomic', 'false');
        document.body.appendChild(this.container);
    }
    
    show(message, type = 'info', options = {}) {
        const id = ++this.notificationId;
        const {
            title = null,
            duration = 5000,
            actions = [],
            persistent = false,
            icon = this.getDefaultIcon(type)
        } = options;
        
        // Create notification element
        const notification = this.createNotificationElement(id, message, type, {
            title, icon, actions, persistent
        });
        
        // Add to container
        this.container.appendChild(notification);
        this.notifications.set(id, notification);
        
        // Show with animation
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });
        
        // Announce to screen readers
        const announcement = title ? `${title}: ${message}` : message;
        if (type === 'error') {
            if (window.announceError) {
                window.announceError(announcement);
            }
        } else {
            if (window.announceStatus) {
                window.announceStatus(announcement);
            }
        }
        
        // Auto-hide if not persistent
        if (!persistent && duration > 0) {
            setTimeout(() => {
                this.hide(id);
            }, duration);
        }
        
        console.log('Notification shown:', { id, type, message, title });
        return id;
    }
    
    createNotificationElement(id, message, type, options) {
        const { title, icon, actions, persistent } = options;
        
        const notification = document.createElement('div');
        notification.className = `api-notification ${type}`;
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', type === 'error' ? 'assertive' : 'polite');
        notification.setAttribute('data-notification-id', id);
        
        let html = '';
        
        // Icon
        if (icon) {
            html += `<span class="notification-icon" aria-hidden="true">${icon}</span>`;
        }
        
        // Content
        html += '<div class="notification-content">';
        if (title) {
            html += `<div class="notification-title">${this.escapeHtml(title)}</div>`;
        }
        html += `<div class="notification-message">${this.escapeHtml(message)}</div>`;
        
        // Actions
        if (actions.length > 0) {
            html += '<div class="notification-actions">';
            actions.forEach(action => {
                html += `<button class="notification-btn" data-action="${action.id}">${this.escapeHtml(action.label)}</button>`;
            });
            html += '</div>';
        }
        
        html += '</div>';
        
        // Close button (always show for persistent notifications)
        if (persistent || actions.length > 0) {
            html += `<button class="notification-close" aria-label="Close notification">×</button>`;
        }
        
        notification.innerHTML = html;
        
        // Add event listeners
        this.addNotificationEventListeners(notification, id, actions);
        
        return notification;
    }
    
    addNotificationEventListeners(notification, id, actions) {
        // Close button
        const closeBtn = notification.querySelector('.notification-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hide(id));
        }
        
        // Action buttons
        actions.forEach(action => {
            const btn = notification.querySelector(`[data-action="${action.id}"]`);
            if (btn) {
                btn.addEventListener('click', () => {
                    if (typeof action.handler === 'function') {
                        action.handler();
                    }
                    if (action.closeOnClick !== false) {
                        this.hide(id);
                    }
                });
            }
        });
        
        // Keyboard navigation
        notification.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hide(id);
            }
        });
    }
    
    hide(id) {
        const notification = this.notifications.get(id);
        if (!notification) return;
        
        // Animate out
        notification.style.animation = 'slideOutRight 0.3s ease-out forwards';
        
        // Remove after animation
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
            this.notifications.delete(id);
        }, 300);
        
        console.log('Notification hidden:', id);
    }
    
    hideAll() {
        this.notifications.forEach((notification, id) => {
            this.hide(id);
        });
    }
    
    getDefaultIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Convenience methods
    success(message, options = {}) {
        return this.show(message, 'success', options);
    }
    
    error(message, options = {}) {
        return this.show(message, 'error', { ...options, persistent: true });
    }
    
    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }
    
    info(message, options = {}) {
        return this.show(message, 'info', options);
    }
}

/**
 * Enhanced Error Handling System
 */
class ErrorHandler {
    constructor() {
        this.errorCounts = new Map();
        this.maxRetries = 3;
        this.retryDelays = [1000, 2000, 5000]; // Progressive delays
        
        // Initialize error handling
        this.initializeErrorHandling();
    }
    
    initializeErrorHandling() {
        // Global error handler
        window.addEventListener('error', (event) => {
            this.handleGlobalError(event.error, 'JavaScript Error');
        });
        
        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            this.handleGlobalError(event.reason, 'Unhandled Promise Rejection');
        });
        
        // Network status monitoring
        window.addEventListener('online', () => {
            this.handleNetworkStatusChange(true);
        });
        
        window.addEventListener('offline', () => {
            this.handleNetworkStatusChange(false);
        });
        
        console.log('Error handling system initialized');
    }
    
    handleGlobalError(error, context) {
        console.error(`${context}:`, error);
        
        // Don't show notifications for every error, just log them
        // Only show user-facing errors for critical issues
        if (this.isCriticalError(error)) {
            if (window.notificationManager) {
                window.notificationManager.error(
                    'An unexpected error occurred. Please refresh the page if problems persist.',
                    {
                        title: 'Application Error',
                        actions: [{
                            id: 'refresh',
                            label: 'Refresh Page',
                            handler: () => window.location.reload()
                        }]
                    }
                );
            }
        }
    }
    
    isCriticalError(error) {
        // Define what constitutes a critical error
        const criticalPatterns = [
            /network/i,
            /fetch/i,
            /api/i,
            /authentication/i,
            /authorization/i
        ];
        
        const errorMessage = error?.message || error?.toString() || '';
        return criticalPatterns.some(pattern => pattern.test(errorMessage));
    }
    
    handleNetworkStatusChange(isOnline) {
        const offlineIndicator = document.getElementById('offline-indicator');
        
        if (isOnline) {
            // Hide offline indicator
            if (offlineIndicator) {
                offlineIndicator.classList.remove('show');
            }
            
            if (window.announceStatus) {
                window.announceStatus('Connection restored. You are back online.');
            }
            if (window.notificationManager) {
                window.notificationManager.success('Connection restored', {
                    title: 'Back Online'
                });
            }
        } else {
            // Show offline indicator
            if (offlineIndicator) {
                offlineIndicator.classList.add('show');
            }
            
            if (window.announceError) {
                window.announceError('Connection lost. You are now offline.');
            }
            if (window.notificationManager) {
                window.notificationManager.warning(
                    'Some features may not work while offline.',
                    {
                        title: 'Connection Lost',
                        persistent: true
                    }
                );
            }
        }
    }
    
    async handleApiError(error, operation, retryFunction = null) {
        const errorKey = `${operation}_${error.status || 'unknown'}`;
        const errorCount = this.errorCounts.get(errorKey) || 0;
        
        console.error(`API Error in ${operation}:`, error);
        
        // Increment error count
        this.errorCounts.set(errorKey, errorCount + 1);
        
        // Determine if we should retry
        const shouldRetry = retryFunction && errorCount < this.maxRetries && this.isRetryableError(error);
        
        if (shouldRetry) {
            const delay = this.retryDelays[errorCount] || 5000;
            
            if (window.notificationManager) {
                window.notificationManager.warning(
                    `${operation} failed. Retrying in ${delay / 1000} seconds...`,
                    {
                        title: 'Retrying Operation',
                        duration: delay
                    }
                );
            }
            
            // Wait and retry
            await this.delay(delay);
            
            try {
                return await retryFunction();
            } catch (retryError) {
                return this.handleApiError(retryError, operation, retryFunction);
            }
        } else {
            // Show final error to user
            const userMessage = this.getUserFriendlyErrorMessage(error, operation);
            
            if (window.notificationManager) {
                window.notificationManager.error(userMessage, {
                    title: 'Operation Failed',
                    actions: [{
                        id: 'retry',
                        label: 'Try Again',
                        handler: retryFunction || (() => window.location.reload())
                    }]
                });
            }
            
            // Reset error count after final failure
            this.errorCounts.delete(errorKey);
            
            throw error;
        }
    }
    
    isRetryableError(error) {
        // Network errors and server errors are retryable
        // Client errors (4xx) are generally not retryable
        const status = error.status;
        return !status || status >= 500 || status === 408 || status === 429;
    }
    
    getUserFriendlyErrorMessage(error, operation) {
        const status = error.status;
        const operation_lower = operation.toLowerCase();
        
        if (!navigator.onLine) {
            return 'No internet connection. Please check your network and try again.';
        }
        
        switch (status) {
            case 400:
                return `Invalid ${operation_lower} request. Please check your input and try again.`;
            case 401:
                return 'Authentication required. Please log in and try again.';
            case 403:
                return `You don't have permission to perform this ${operation_lower}.`;
            case 404:
                return `${operation} endpoint not found. Please contact support.`;
            case 413:
                return 'File too large. Please select a smaller file.';
            case 429:
                return 'Too many requests. Please wait a moment and try again.';
            case 500:
                return 'Server error. Please try again in a few moments.';
            case 503:
                return 'Service temporarily unavailable. Please try again later.';
            default:
                return `${operation} failed. Please try again or contact support if the problem persists.`;
        }
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

/**
 * Enhanced Keyboard Navigation Manager
 */
class KeyboardNavigationManager {
    constructor() {
        this.focusableSelectors = [
            'a[href]',
            'button:not([disabled])',
            'input:not([disabled])',
            'textarea:not([disabled])',
            'select:not([disabled])',
            '[tabindex]:not([tabindex="-1"])',
            '[contenteditable="true"]'
        ].join(', ');
        
        this.initializeKeyboardNavigation();
    }
    
    initializeKeyboardNavigation() {
        // Enhanced keyboard event handling
        document.addEventListener('keydown', (e) => {
            this.handleGlobalKeydown(e);
        });
        
        // Focus management for dynamic content
        this.setupFocusManagement();
        
        console.log('Enhanced keyboard navigation initialized');
    }
    
    handleGlobalKeydown(e) {
        // Skip navigation if user is typing in an input
        if (this.isTypingContext(e.target)) {
            return;
        }
        
        switch (e.key) {
            case 'Escape':
                this.handleEscapeKey(e);
                break;
            case 'Tab':
                this.handleTabKey(e);
                break;
            case 'Enter':
            case ' ':
                this.handleActivationKey(e);
                break;
            case 'ArrowUp':
            case 'ArrowDown':
            case 'ArrowLeft':
            case 'ArrowRight':
                this.handleArrowKeys(e);
                break;
        }
    }
    
    isTypingContext(element) {
        const typingElements = ['INPUT', 'TEXTAREA', 'SELECT'];
        return typingElements.includes(element.tagName) || 
               element.contentEditable === 'true';
    }
    
    handleEscapeKey(e) {
        // Close modals, notifications, etc.
        const activeModal = document.querySelector('.loading-overlay.active');
        if (activeModal) {
            // Don't allow closing loading overlays with escape
            return;
        }
        
        // Close notifications
        const notifications = document.querySelectorAll('.api-notification.show');
        if (notifications.length > 0) {
            notifications.forEach(notification => {
                const id = notification.getAttribute('data-notification-id');
                if (id && window.notificationManager) {
                    window.notificationManager.hide(parseInt(id));
                }
            });
            e.preventDefault();
        }
    }
    
    handleTabKey(e) {
        // Enhanced tab navigation with focus trapping
        const focusableElements = this.getFocusableElements();
        
        // Check if we're in a modal or overlay
        const activeOverlay = document.querySelector('.loading-overlay.active');
        if (activeOverlay) {
            // Trap focus in overlay
            const overlayFocusable = activeOverlay.querySelectorAll(this.focusableSelectors);
            if (overlayFocusable.length === 0) {
                e.preventDefault();
                return;
            }
            
            const firstOverlayElement = overlayFocusable[0];
            const lastOverlayElement = overlayFocusable[overlayFocusable.length - 1];
            
            if (e.shiftKey && document.activeElement === firstOverlayElement) {
                e.preventDefault();
                lastOverlayElement.focus();
            } else if (!e.shiftKey && document.activeElement === lastOverlayElement) {
                e.preventDefault();
                firstOverlayElement.focus();
            }
        }
    }
    
    handleActivationKey(e) {
        const target = e.target;
        
        // Handle space key for buttons and custom interactive elements
        if (e.key === ' ' && (target.tagName === 'BUTTON' || target.getAttribute('role') === 'button')) {
            e.preventDefault();
            target.click();
        }
        
        // Add visual feedback
        target.classList.add('keyboard-activated');
        setTimeout(() => {
            target.classList.remove('keyboard-activated');
        }, 150);
    }
    
    handleArrowKeys(e) {
        const target = e.target;
        
        // Handle grid navigation
        const gridContainer = target.closest('.feature-grid, .metrics-grid, .issues-container');
        if (gridContainer) {
            this.handleGridNavigation(e, target, gridContainer);
        }
    }
    
    handleGridNavigation(e, currentElement, gridContainer) {
        const focusableItems = Array.from(gridContainer.querySelectorAll('[tabindex="0"]'));
        const currentIndex = focusableItems.indexOf(currentElement);
        
        if (currentIndex === -1) return;
        
        let targetIndex = currentIndex;
        const isGrid = gridContainer.classList.contains('feature-grid') || 
                      gridContainer.classList.contains('metrics-grid');
        
        if (isGrid) {
            // Calculate grid dimensions
            const gridStyle = window.getComputedStyle(gridContainer);
            const columns = gridStyle.gridTemplateColumns.split(' ').length;
            
            switch (e.key) {
                case 'ArrowLeft':
                    targetIndex = currentIndex > 0 ? currentIndex - 1 : focusableItems.length - 1;
                    break;
                case 'ArrowRight':
                    targetIndex = currentIndex < focusableItems.length - 1 ? currentIndex + 1 : 0;
                    break;
                case 'ArrowUp':
                    targetIndex = currentIndex - columns;
                    if (targetIndex < 0) targetIndex = currentIndex;
                    break;
                case 'ArrowDown':
                    targetIndex = currentIndex + columns;
                    if (targetIndex >= focusableItems.length) targetIndex = currentIndex;
                    break;
            }
        } else {
            // Linear navigation for lists
            switch (e.key) {
                case 'ArrowUp':
                    targetIndex = currentIndex > 0 ? currentIndex - 1 : focusableItems.length - 1;
                    break;
                case 'ArrowDown':
                    targetIndex = currentIndex < focusableItems.length - 1 ? currentIndex + 1 : 0;
                    break;
            }
        }
        
        if (targetIndex !== currentIndex && focusableItems[targetIndex]) {
            e.preventDefault();
            focusableItems[targetIndex].focus();
        }
    }
    
    getFocusableElements() {
        return Array.from(document.querySelectorAll(this.focusableSelectors))
            .filter(element => this.isVisible(element));
    }
    
    isVisible(element) {
        const style = window.getComputedStyle(element);
        return style.display !== 'none' && 
               style.visibility !== 'hidden' && 
               element.offsetParent !== null;
    }
    
    setupFocusManagement() {
        // Focus management for dynamically added content
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            this.enhanceNewElements(node);
                        }
                    });
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    enhanceNewElements(element) {
        // Add keyboard navigation to new focusable elements
        const focusableElements = element.querySelectorAll(this.focusableSelectors);
        
        focusableElements.forEach(el => {
            if (!el.hasAttribute('data-keyboard-enhanced')) {
                el.setAttribute('data-keyboard-enhanced', 'true');
                
                // Add focus indicators
                el.addEventListener('focus', () => {
                    el.classList.add('focus-visible');
                });
                
                el.addEventListener('blur', () => {
                    el.classList.remove('focus-visible');
                });
            }
        });
    }
}

// Initialize enhanced accessibility systems
document.addEventListener('DOMContentLoaded', function() {
    // Initialize global accessibility managers
    window.loadingManager = new LoadingStateManager();
    window.notificationManager = new NotificationManager();
    window.errorHandler = new ErrorHandler();
    window.keyboardManager = new KeyboardNavigationManager();
    
    console.log('Enhanced accessibility systems initialized');
});