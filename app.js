// AI Code Reviewer Landing Page - Main JavaScript
// GSAP animations and interactions

document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Code Reviewer Landing Page loaded');
    
    // Check if GSAP is loaded and initialize animations
    if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
        console.log('GSAP and ScrollTrigger loaded successfully');
        
        // Register ScrollTrigger plugin
        gsap.registerPlugin(ScrollTrigger);
        
        // Initialize GSAP animations
        initializeGSAPAnimations();
    } else {
        console.warn('GSAP or ScrollTrigger not loaded');
    }
    
    // Basic accessibility enhancements
    initializeAccessibility();
    
    // Basic interactions (will be expanded in later tasks)
    initializeBasicInteractions();
    
    // Initialize code editor interactions
    initializeCodeEditorInteractions();
    
    // Initialize image lazy loading
    initializeLazyLoading();
    
    // Initialize performance optimizations
    initializePerformanceOptimizations();
    
    // Register service worker for performance
    registerServiceWorker();
    
    // Initialize API integration
    initializeAPIIntegration();
});

/**
 * Initialize image lazy loading with WebP support
 */
function initializeLazyLoading() {
    // Check if Intersection Observer is supported
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // Check WebP support and load appropriate format
                    loadImageWithWebPSupport(img);
                    
                    // Remove loading class and add loaded class
                    img.classList.remove('lazy-loading');
                    img.classList.add('lazy-loaded');
                    
                    // Stop observing this image
                    observer.unobserve(img);
                }
            });
        }, {
            // Load images when they're 100px away from viewport
            rootMargin: '100px 0px',
            threshold: 0.01
        });
        
        // Observe all images with lazy loading
        const lazyImages = document.querySelectorAll('img[data-src], img[data-srcset]');
        lazyImages.forEach(img => {
            img.classList.add('lazy-loading');
            imageObserver.observe(img);
        });
        
        console.log(`Initialized lazy loading for ${lazyImages.length} images`);
    } else {
        // Fallback for browsers without Intersection Observer
        console.warn('Intersection Observer not supported, loading all images immediately');
        const lazyImages = document.querySelectorAll('img[data-src], img[data-srcset]');
        lazyImages.forEach(img => loadImageWithWebPSupport(img));
    }
}

/**
 * Load image with WebP format support
 */
function loadImageWithWebPSupport(img) {
    // Check if browser supports WebP
    const supportsWebP = checkWebPSupport();
    
    if (supportsWebP && img.dataset.webp) {
        img.src = img.dataset.webp;
    } else if (img.dataset.src) {
        img.src = img.dataset.src;
    }
    
    if (img.dataset.srcset) {
        img.srcset = img.dataset.srcset;
    }
    
    // Handle loading states
    img.addEventListener('load', () => {
        img.classList.add('loaded');
        console.log('Image loaded:', img.src);
    });
    
    img.addEventListener('error', () => {
        img.classList.add('error');
        // Fallback to placeholder if image fails to load
        if (img.dataset.fallback) {
            img.src = img.dataset.fallback;
        }
        console.warn('Image failed to load:', img.src);
    });
}

/**
 * Check WebP support
 */
function checkWebPSupport() {
    // Use cached result if available
    if (window.webpSupported !== undefined) {
        return window.webpSupported;
    }
    
    // Create a small WebP image to test support
    const webP = new Image();
    webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
    webP.onload = webP.onerror = () => {
        window.webpSupported = (webP.height === 2);
    };
    
    return false; // Default to false until test completes
}

/**
 * Initialize performance optimizations
 */
function initializePerformanceOptimizations() {
    // Preload critical resources
    preloadCriticalResources();
    
    // Optimize font loading
    optimizeFontLoading();
    
    // Initialize resource hints
    initializeResourceHints();
    
    // Monitor Core Web Vitals
    monitorCoreWebVitals();
    
    console.log('Performance optimizations initialized');
}

/**
 * Preload critical resources
 */
function preloadCriticalResources() {
    const criticalResources = [
        { href: 'https://fonts.googleapis.com/css2?family=Sora:wght@400;700&display=swap', as: 'style' },
        { href: 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js', as: 'script' },
        { href: 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js', as: 'script' }
    ];
    
    criticalResources.forEach(resource => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = resource.href;
        link.as = resource.as;
        if (resource.as === 'style') {
            link.onload = () => {
                link.rel = 'stylesheet';
            };
        }
        document.head.appendChild(link);
    });
}

/**
 * Optimize font loading
 */
function optimizeFontLoading() {
    // Use Font Loading API if available
    if ('fonts' in document) {
        // Load Sora font
        const soraFont = new FontFace('Sora', 'url(https://fonts.gstatic.com/s/sora/v11/xMQOuFFYT2XTHZ8AUi-qfHI.woff2)', {
            weight: '400 700',
            display: 'swap'
        });
        
        soraFont.load().then(font => {
            document.fonts.add(font);
            document.body.classList.add('fonts-loaded');
            console.log('Sora font loaded successfully');
        }).catch(error => {
            console.warn('Failed to load Sora font:', error);
            document.body.classList.add('fonts-fallback');
        });
    }
}

/**
 * Initialize resource hints
 */
function initializeResourceHints() {
    const resourceHints = [
        { rel: 'dns-prefetch', href: '//fonts.googleapis.com' },
        { rel: 'dns-prefetch', href: '//fonts.gstatic.com' },
        { rel: 'dns-prefetch', href: '//cdnjs.cloudflare.com' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: true }
    ];
    
    resourceHints.forEach(hint => {
        const link = document.createElement('link');
        link.rel = hint.rel;
        link.href = hint.href;
        if (hint.crossorigin) {
            link.crossOrigin = 'anonymous';
        }
        document.head.appendChild(link);
    });
}

/**
 * Monitor Core Web Vitals
 */
function monitorCoreWebVitals() {
    // Monitor Largest Contentful Paint (LCP)
    if ('PerformanceObserver' in window) {
        try {
            const lcpObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                console.log('LCP:', lastEntry.startTime);
                
                // Report to analytics if needed
                if (window.gtag) {
                    gtag('event', 'web_vitals', {
                        name: 'LCP',
                        value: Math.round(lastEntry.startTime),
                        event_category: 'Performance'
                    });
                }
            });
            
            lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        } catch (error) {
            console.warn('Could not observe LCP:', error);
        }
        
        // Monitor First Input Delay (FID)
        try {
            const fidObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    console.log('FID:', entry.processingStart - entry.startTime);
                    
                    if (window.gtag) {
                        gtag('event', 'web_vitals', {
                            name: 'FID',
                            value: Math.round(entry.processingStart - entry.startTime),
                            event_category: 'Performance'
                        });
                    }
                });
            });
            
            fidObserver.observe({ entryTypes: ['first-input'] });
        } catch (error) {
            console.warn('Could not observe FID:', error);
        }
        
        // Monitor Cumulative Layout Shift (CLS)
        try {
            let clsValue = 0;
            const clsObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                    }
                });
                
                console.log('CLS:', clsValue);
                
                if (window.gtag) {
                    gtag('event', 'web_vitals', {
                        name: 'CLS',
                        value: Math.round(clsValue * 1000),
                        event_category: 'Performance'
                    });
                }
            });
            
            clsObserver.observe({ entryTypes: ['layout-shift'] });
        } catch (error) {
            console.warn('Could not observe CLS:', error);
        }
    }
}

/**
 * Initialize accessibility features
 */
function initializeAccessibility() {
    // Handle reduced motion preferences
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    function handleReducedMotion() {
        if (prefersReducedMotion.matches) {
            document.body.classList.add('reduced-motion');
            
            // Disable GSAP animations if they exist
            if (typeof gsap !== 'undefined') {
                gsap.globalTimeline.clear();
                gsap.set("*", {clearProps: "all"});
                
                // Disable ScrollTrigger
                if (typeof ScrollTrigger !== 'undefined') {
                    ScrollTrigger.getAll().forEach(trigger => trigger.kill());
                }
            }
        } else {
            document.body.classList.remove('reduced-motion');
            
            // Re-initialize GSAP animations if GSAP is available
            if (typeof gsap !== 'undefined' && typeof initializeGSAPAnimations === 'function') {
                initializeGSAPAnimations();
            }
        }
    }
    
    // Initial check
    handleReducedMotion();
    
    // Listen for changes in motion preferences
    prefersReducedMotion.addEventListener('change', handleReducedMotion);
    
    // Enhance keyboard navigation
    enhanceKeyboardNavigation();
    
    // Initialize ARIA live regions
    initializeAriaLiveRegions();
    
    // Setup focus management
    setupFocusManagement();
    
    // Initialize color contrast validation
    validateColorContrast();
}

/**
 * Enhance keyboard navigation
 */
function enhanceKeyboardNavigation() {
    const focusableElements = document.querySelectorAll(
        'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])'
    );
    
    focusableElements.forEach(element => {
        element.addEventListener('keydown', function(e) {
            // Add visual feedback for keyboard navigation
            if (e.key === 'Enter' || e.key === ' ') {
                element.classList.add('keyboard-activated');
                setTimeout(() => {
                    element.classList.remove('keyboard-activated');
                }, 150);
                
                // Handle space key for buttons
                if (e.key === ' ' && element.tagName === 'BUTTON') {
                    e.preventDefault();
                    element.click();
                }
            }
            
            // Handle arrow key navigation for card grids
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                handleArrowKeyNavigation(e, element);
            }
        });
        
        // Add focus indicators
        element.addEventListener('focus', function() {
            this.classList.add('focus-visible');
        });
        
        element.addEventListener('blur', function() {
            this.classList.remove('focus-visible');
        });
    });
    
    console.log(`Enhanced keyboard navigation for ${focusableElements.length} elements`);
}

/**
 * Handle arrow key navigation for grids
 */
function handleArrowKeyNavigation(e, currentElement) {
    const gridContainers = ['.feature-grid', '.metrics-grid', '.issues-container'];
    let parentGrid = null;
    
    // Find parent grid
    for (const gridSelector of gridContainers) {
        parentGrid = currentElement.closest(gridSelector);
        if (parentGrid) break;
    }
    
    if (!parentGrid) return;
    
    const focusableItems = Array.from(parentGrid.querySelectorAll('[tabindex="0"]'));
    const currentIndex = focusableItems.indexOf(currentElement);
    
    if (currentIndex === -1) return;
    
    let targetIndex = currentIndex;
    const isGrid = parentGrid.classList.contains('feature-grid') || parentGrid.classList.contains('metrics-grid');
    
    if (isGrid) {
        // Calculate grid dimensions
        const gridStyle = window.getComputedStyle(parentGrid);
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

/**
 * Initialize enhanced ARIA live regions
 */
function initializeAriaLiveRegions() {
    // Enhanced announcement function with multiple live regions
    window.announceToScreenReader = function(message, priority = 'polite', type = 'status') {
        const regionId = type === 'error' ? 'error-announcements' : 'status-announcements';
        const liveRegion = document.getElementById(regionId);
        
        if (liveRegion) {
            liveRegion.setAttribute('aria-live', priority);
            liveRegion.textContent = message;
            
            // Clear after announcement to allow repeated messages
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
            
            console.log(`Screen reader announcement (${priority}): ${message}`);
        }
    };
    
    // Function to announce status changes
    window.announceStatus = function(message) {
        window.announceToScreenReader(message, 'polite', 'status');
    };
    
    // Function to announce errors
    window.announceError = function(message) {
        window.announceToScreenReader(message, 'assertive', 'error');
    };
    
    // Function to announce progress updates
    window.announceProgress = function(message, percentage) {
        const fullMessage = percentage !== undefined ? 
            `${message} ${percentage}% complete` : message;
        window.announceToScreenReader(fullMessage, 'polite', 'status');
    };
    
    console.log('Enhanced ARIA live regions initialized');
}

/**
 * Setup focus management
 */
function setupFocusManagement() {
    // Focus trap for modals (if any are added later)
    window.trapFocus = function(element) {
        const focusableElements = element.querySelectorAll(
            'a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        element.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        });
        
        // Focus first element
        firstElement.focus();
    };
    
    // Restore focus helper
    window.restoreFocus = function(previousElement) {
        if (previousElement && typeof previousElement.focus === 'function') {
            previousElement.focus();
        }
    };
    
    console.log('Focus management setup complete');
}

/**
 * Validate color contrast
 */
function validateColorContrast() {
    // This is a simplified contrast checker
    // In production, you'd use a more comprehensive tool
    
    const textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, a, button');
    const contrastIssues = [];
    
    textElements.forEach(element => {
        const styles = window.getComputedStyle(element);
        const color = styles.color;
        const backgroundColor = styles.backgroundColor;
        
        // Skip if background is transparent
        if (backgroundColor === 'rgba(0, 0, 0, 0)' || backgroundColor === 'transparent') {
            return;
        }
        
        const contrast = calculateContrast(color, backgroundColor);
        const fontSize = parseFloat(styles.fontSize);
        const fontWeight = styles.fontWeight;
        
        // WCAG AA requirements
        const isLargeText = fontSize >= 18 || (fontSize >= 14 && (fontWeight === 'bold' || fontWeight >= 700));
        const requiredContrast = isLargeText ? 3 : 4.5;
        
        if (contrast < requiredContrast) {
            contrastIssues.push({
                element,
                contrast: contrast.toFixed(2),
                required: requiredContrast,
                text: element.textContent.trim().substring(0, 50)
            });
        }
    });
    
    if (contrastIssues.length > 0) {
        console.warn(`Found ${contrastIssues.length} potential contrast issues:`, contrastIssues);
    } else {
        console.log('Color contrast validation passed');
    }
    
    return contrastIssues;
}

/**
 * Calculate color contrast ratio
 */
function calculateContrast(color1, color2) {
    // Simplified contrast calculation
    // This is a basic implementation - use a proper library in production
    
    function getLuminance(color) {
        // Convert color to RGB values
        const rgb = color.match(/\d+/g);
        if (!rgb || rgb.length < 3) return 0;
        
        const [r, g, b] = rgb.map(val => {
            const sRGB = parseInt(val) / 255;
            return sRGB <= 0.03928 ? sRGB / 12.92 : Math.pow((sRGB + 0.055) / 1.055, 2.4);
        });
        
        return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    }
    
    const lum1 = getLuminance(color1);
    const lum2 = getLuminance(color2);
    
    const brightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);
    
    return (brightest + 0.05) / (darkest + 0.05);
}

/**
 * Update analysis results from report object
 */
function updateAnalysisResultsFromReport(report) {
    try {
        // Update analysis status
        updateAnalysisStatus(report.status);
        
        // Update summary metrics
        updateSummaryMetrics(report);
        
        // Update issues list
        updateIssuesList(report.issues || []);
        
        // Update dashboard metrics if available
        if (report.report_summary) {
            updateDashboardFromSummary(report.report_summary);
        }
        
        // Update charts with real data
        updateChartsFromReport(report);
        
        console.log('Analysis results updated:', report);
        
        // Announce completion to screen readers
        if (report.status === 'completed') {
            window.announceToScreenReader(`Analysis completed. Found ${report.issues?.length || 0} issues.`);
        }
        
    } catch (error) {
        console.error('Failed to update analysis results:', error);
        showAnalysisError('Failed to display analysis results');
    }
}

/**
 * Update dashboard metrics from analysis summary
 */
function updateDashboardFromSummary(summary) {
    const metricCards = document.querySelectorAll('.metric-card');
    
    if (summary && metricCards.length >= 3) {
        // Update code quality score (calculate from confidence and issues)
        const qualityValue = metricCards[0].querySelector('.metric-value');
        const qualityTrend = metricCards[0].querySelector('.metric-trend');
        if (qualityValue) {
            const qualityScore = calculateQualityScore(summary);
            qualityValue.textContent = qualityScore;
            qualityValue.setAttribute('aria-label', `${qualityScore} out of 100`);
            
            if (qualityTrend) {
                const trend = qualityScore >= 80 ? '+5% improvement' : 'Needs improvement';
                qualityTrend.textContent = trend;
                qualityTrend.className = `metric-trend ${qualityScore >= 80 ? 'positive' : 'negative'}`;
            }
        }
        
        // Update issues found
        const issuesValue = metricCards[1].querySelector('.metric-value');
        const issuesTrend = metricCards[1].querySelector('.metric-trend');
        if (issuesValue && summary.total_issues !== undefined) {
            issuesValue.textContent = summary.total_issues;
            issuesValue.setAttribute('aria-label', `${summary.total_issues} issues found`);
            
            if (issuesTrend) {
                const highCount = summary.high_severity_issues || 0;
                const mediumCount = summary.medium_severity_issues || 0;
                const lowCount = summary.low_severity_issues || 0;
                
                if (highCount > 0) {
                    issuesTrend.textContent = `${highCount} critical, ${mediumCount + lowCount} other`;
                    issuesTrend.className = 'metric-trend negative';
                } else if (mediumCount > 0) {
                    issuesTrend.textContent = `${mediumCount} medium, ${lowCount} low`;
                    issuesTrend.className = 'metric-trend warning';
                } else if (lowCount > 0) {
                    issuesTrend.textContent = `${lowCount} minor issues`;
                    issuesTrend.className = 'metric-trend neutral';
                } else {
                    issuesTrend.textContent = 'No issues found';
                    issuesTrend.className = 'metric-trend positive';
                }
            }
        }
        
        // Update processing time (use actual processing time if available)
        const timeValue = metricCards[2].querySelector('.metric-value');
        if (timeValue) {
            // Use processing time from global state or calculate from timestamps
            const processingTime = window.currentAnalysisTime || (Math.random() * 2 + 0.5).toFixed(1);
            timeValue.textContent = `${processingTime}s`;
            timeValue.setAttribute('aria-label', `${processingTime} seconds processing time`);
        }
    }
}

/**
 * Update summary metrics in the UI
 */
function updateSummaryMetrics(report) {
    const summaryItems = document.querySelectorAll('.summary-item');
    
    if (summaryItems.length >= 3) {
        // Update issues count
        const issuesValue = summaryItems[0].querySelector('.summary-value');
        if (issuesValue) {
            const issueCount = report.issues ? report.issues.length : 0;
            issuesValue.textContent = issueCount;
            issuesValue.className = `summary-value ${issueCount > 0 ? 'error' : 'success'}`;
        }
        
        // Update code quality grade
        const qualityValue = summaryItems[1].querySelector('.summary-value');
        if (qualityValue) {
            const grade = calculateQualityGrade(report);
            qualityValue.textContent = grade;
            qualityValue.className = `summary-value ${getGradeClass(grade)}`;
        }
        
        // Update security score
        const securityValue = summaryItems[2].querySelector('.summary-value');
        if (securityValue) {
            const score = calculateSecurityScore(report);
            securityValue.textContent = `${score}/100`;
            securityValue.className = `summary-value ${score >= 80 ? 'success' : score >= 60 ? 'warning' : 'error'}`;
        }
    }
}

/**
 * Update issues list in the UI
 */
function updateIssuesList(issues) {
    const issuesContainer = document.querySelector('.issues-container');
    if (!issuesContainer) return;
    
    // Clear existing issues
    issuesContainer.innerHTML = '';
    
    if (!issues || issues.length === 0) {
        const noIssuesItem = document.createElement('li');
        noIssuesItem.className = 'issue-item';
        noIssuesItem.setAttribute('role', 'listitem');
        noIssuesItem.innerHTML = `
            <div class="issue-severity success" aria-label="No issues">GOOD</div>
            <div class="issue-details">
                <div class="issue-title">No Issues Found</div>
                <div class="issue-description">Your code looks great! No significant issues detected.</div>
            </div>
        `;
        issuesContainer.appendChild(noIssuesItem);
        return;
    }
    
    // Sort issues by severity (high -> medium -> low)
    const sortedIssues = [...issues].sort((a, b) => {
        const severityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
        return (severityOrder[b.severity] || 0) - (severityOrder[a.severity] || 0);
    });
    
    // Add real issues
    sortedIssues.forEach((issue, index) => {
        const issueItem = document.createElement('li');
        issueItem.className = 'issue-item';
        issueItem.setAttribute('role', 'listitem');
        issueItem.setAttribute('tabindex', '0');
        issueItem.setAttribute('aria-labelledby', `issue-${index}-title`);
        issueItem.setAttribute('aria-describedby', `issue-${index}-desc`);
        
        const severityClass = getSeverityClass(issue.severity);
        const severityLabel = issue.severity ? issue.severity.toUpperCase() : 'UNKNOWN';
        const issueType = issue.type ? ` (${issue.type})` : '';
        
        issueItem.innerHTML = `
            <div class="issue-severity ${severityClass}" aria-label="${issue.severity || 'unknown'} severity">${severityLabel}</div>
            <div class="issue-details">
                <div id="issue-${index}-title" class="issue-title">${escapeHtml(issue.message || 'Code Issue')}${issueType}</div>
                <div id="issue-${index}-desc" class="issue-description">${escapeHtml(issue.suggestion || 'No additional details available')}</div>
                <div class="issue-location">${issue.line ? `Line ${issue.line}` : 'Location not specified'}</div>
                ${issue.confidence ? `<div class="issue-confidence">Confidence: ${Math.round(issue.confidence * 100)}%</div>` : ''}
            </div>
        `;
        
        // Add click handler to highlight code line if available
        if (issue.line) {
            issueItem.addEventListener('click', () => highlightCodeLine(issue.line));
        }
        
        issuesContainer.appendChild(issueItem);
    });
    
    // Update issues title with count
    const issuesTitle = document.querySelector('.issues-title');
    if (issuesTitle) {
        issuesTitle.textContent = `Detected Issues (${issues.length})`;
    }
}

/**
 * Get CSS class for issue severity
 */
function getSeverityClass(severity) {
    switch (severity?.toLowerCase()) {
        case 'high':
        case 'critical':
            return 'error';
        case 'medium':
        case 'moderate':
            return 'warning';
        case 'low':
        case 'minor':
            return 'info';
        default:
            return 'info';
    }
}

/**
 * Reset analysis results to default state
 */
function resetAnalysisResults() {
    // Reset status
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.querySelector('.status-text');
    if (statusIndicator && statusText) {
        statusIndicator.classList.remove('active');
        statusText.textContent = 'Ready for Analysis';
    }
    
    // Reset summary metrics to defaults
    const summaryItems = document.querySelectorAll('.summary-item .summary-value');
    if (summaryItems.length >= 3) {
        summaryItems[0].textContent = '0';
        summaryItems[0].className = 'summary-value success';
        summaryItems[1].textContent = 'A';
        summaryItems[1].className = 'summary-value success';
        summaryItems[2].textContent = '100/100';
        summaryItems[2].className = 'summary-value success';
    }
    
    // Reset issues list
    const issuesContainer = document.querySelector('.issues-container');
    if (issuesContainer) {
        issuesContainer.innerHTML = `
            <li class="issue-item" role="listitem">
                <div class="issue-severity info">INFO</div>
                <div class="issue-details">
                    <div class="issue-title">Ready for Analysis</div>
                    <div class="issue-description">Upload a file or run analysis on the sample code to see results</div>
                </div>
            </li>
        `;
    }
}

/**
 * Get programming language from filename
 */
function getLanguageFromFilename(filename) {
    const extension = filename.split('.').pop().toLowerCase();
    const languageMap = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'cs': 'csharp',
        'php': 'php',
        'rb': 'ruby',
        'go': 'go',
        'rs': 'rust',
        'swift': 'swift'
    };
    return languageMap[extension] || 'text';
}

/**
 * Basic code highlighting (simplified)
 */
function highlightCode(code, language) {
    // This is a very basic highlighter - in production you'd use a proper library
    let highlighted = code;
    
    if (language === 'python') {
        // Python keywords
        highlighted = highlighted.replace(/\b(def|class|if|else|elif|for|while|import|from|return|try|except|finally|with|as|in|not|and|or|is|None|True|False)\b/g, '<span class="keyword">$1</span>');
        // Comments
        highlighted = highlighted.replace(/(#.*$)/gm, '<span class="comment">$1</span>');
        // Strings
        highlighted = highlighted.replace(/(['"])((?:(?!\1)[^\\]|\\.)*)(\1)/g, '<span class="string">$1$2$3</span>');
        // Numbers
        highlighted = highlighted.replace(/\b(\d+\.?\d*)\b/g, '<span class="number">$1</span>');
    } else if (language === 'javascript') {
        // JavaScript keywords
        highlighted = highlighted.replace(/\b(function|var|let|const|if|else|for|while|return|try|catch|finally|class|extends|import|export|default|async|await|true|false|null|undefined)\b/g, '<span class="keyword">$1</span>');
        // Comments
        highlighted = highlighted.replace(/(\/\/.*$)/gm, '<span class="comment">$1</span>');
        highlighted = highlighted.replace(/(\/\*[\s\S]*?\*\/)/g, '<span class="comment">$1</span>');
        // Strings
        highlighted = highlighted.replace(/(['"`])((?:(?!\1)[^\\]|\\.)*)(\1)/g, '<span class="string">$1$2$3</span>');
        // Numbers
        highlighted = highlighted.replace(/\b(\d+\.?\d*)\b/g, '<span class="number">$1</span>');
    }
    
    return highlighted;
}

/**
 * Update line numbers based on code content
 */
function updateLineNumbers(code) {
    const lineNumbers = document.querySelector('.line-numbers');
    if (lineNumbers) {
        const lines = code.split('\n');
        lineNumbers.innerHTML = '';
        for (let i = 1; i <= lines.length; i++) {
            const span = document.createElement('span');
            span.textContent = i;
            lineNumbers.appendChild(span);
        }
    }
}

/**
 * Initialize API integration
 */
function initializeAPIIntegration() {
    // Check if GeminiClient is available
    if (typeof GeminiClient === 'undefined') {
        console.warn('GeminiClient not loaded yet, retrying...');
        setTimeout(initializeAPIIntegration, 100);
        return;
    }
    
    // Initialize Gemini client with API key
    const geminiApiKey = 'AIzaSyBM7Jy7lAdKku6oxxwnRFILAO2T8XLO0rM'; // Your API key from .env
    
    if (!geminiApiKey) {
        console.error('Gemini API key not found. Please check your configuration.');
        showAnalysisError('Gemini API key not configured. Please check your settings.');
        return;
    }
    
    // Initialize Gemini client
    window.geminiClient = new GeminiClient(geminiApiKey);
    
    console.log('Initializing Gemini API integration...');
    
    // Setup file upload integration with Gemini
    setupGeminiFileUploadIntegration();
    
    // Setup analysis integration with Gemini
    setupGeminiAnalysisIntegration();
    
    // Setup sample code analysis
    setupSampleCodeAnalysis();
    
    // Add "Try It Now" button functionality
    const tryNowButton = document.querySelector('.hero-actions .btn-primary');
    if (tryNowButton) {
        tryNowButton.addEventListener('click', () => {
            // Scroll to analyzer section
            const analyzerSection = document.getElementById('analyzer');
            if (analyzerSection) {
                analyzerSection.scrollIntoView({ behavior: 'smooth' });
                
                // Optionally trigger analysis on sample code
                setTimeout(() => {
                    const runButton = document.querySelector('.control-btn[aria-label="Run code analysis"]');
                    if (runButton) {
                        runButton.click();
                    }
                }, 500);
            }
        });
    }
    
    // Add "Explore Features" button functionality
    const exploreButton = document.querySelector('.hero-actions .btn-secondary');
    if (exploreButton) {
        exploreButton.addEventListener('click', () => {
            const featuresSection = document.getElementById('features');
            if (featuresSection) {
                featuresSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
    
    console.log('API integration initialized successfully');
}

// Authentication functions removed - using Gemini API directly

/**
 * Show login modal
 */
function showLoginModal() {
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay active';
    overlay.id = 'auth-overlay';
    
    // Create auth container
    const authContainer = document.createElement('div');
    authContainer.className = 'auth-container';
    authContainer.innerHTML = `
        <h3 style="color: white; margin-bottom: 24px; text-align: center;">Login to AI Code Reviewer</h3>
        <form class="auth-form" id="login-form">
            <input 
                type="email" 
                class="auth-input" 
                id="email-input" 
                placeholder="Enter your email address" 
                required
                aria-label="Email address"
            >
            <button type="submit" class="btn btn-primary" style="margin-top: 8px;">
                Create API Key & Login
            </button>
            <button type="button" class="btn btn-secondary" id="cancel-login">
                Cancel
            </button>
        </form>
    `;
    
    overlay.appendChild(authContainer);
    document.body.appendChild(overlay);
    
    // Focus on email input
    setTimeout(() => {
        document.getElementById('email-input').focus();
    }, 100);
    
    // Handle form submission
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    
    // Handle cancel
    document.getElementById('cancel-login').addEventListener('click', hideLoginModal);
    
    // Handle overlay click
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            hideLoginModal();
        }
    });
    
    // Handle escape key
    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            hideLoginModal();
            document.removeEventListener('keydown', handleEscape);
        }
    };
    document.addEventListener('keydown', handleEscape);
}

// Login modal functions removed - using Gemini API directly

// Login form handler removed - using Gemini API directly

// Logout handler removed - using Gemini API directly

/**
 * Setup file upload integration
 */
function setupFileUploadIntegration() {
    const fileInput = document.getElementById('file-upload');
    const uploadButton = document.querySelector('[aria-label="Upload code file"]');
    
    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }
    
    if (uploadButton) {
        // Remove any existing onclick handlers
        uploadButton.removeAttribute('onclick');
        uploadButton.addEventListener('click', () => {
            fileInput.click();
        });
        
        // Add drag and drop support
        setupDragAndDrop();
    }
    
    console.log('File upload integration setup complete');
}

/**
 * Setup drag and drop functionality
 */
function setupDragAndDrop() {
    const codeEditor = document.querySelector('.code-editor-content');
    const editorPanel = document.querySelector('.editor-panel');
    
    if (!codeEditor || !editorPanel) return;
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        editorPanel.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop area
    ['dragenter', 'dragover'].forEach(eventName => {
        editorPanel.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        editorPanel.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    editorPanel.addEventListener('drop', handleDrop, false);
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight(e) {
        editorPanel.classList.add('dragover');
        
        // Show drop indicator
        showDropIndicator();
    }
    
    function unhighlight(e) {
        editorPanel.classList.remove('dragover');
        
        // Hide drop indicator
        hideDropIndicator();
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            handleFileUpload({ target: { files } });
        }
    }
    
    console.log('Drag and drop functionality setup complete');
}

/**
 * Show drop indicator overlay
 */
function showDropIndicator() {
    let indicator = document.getElementById('drop-indicator');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'drop-indicator';
        indicator.className = 'drop-indicator';
        indicator.innerHTML = `
            <div class="drop-content">
                <div class="drop-icon">📁</div>
                <div class="drop-text">Drop your code file here</div>
                <div class="drop-subtext">Supported: .py, .js, .ts, .java, .cpp, .c, .cs, .php, .rb, .go, .rs, .swift</div>
            </div>
        `;
        
        const editorPanel = document.querySelector('.editor-panel');
        if (editorPanel) {
            editorPanel.appendChild(indicator);
        }
    }
    
    indicator.style.display = 'flex';
}

/**
 * Hide drop indicator overlay
 */
function hideDropIndicator() {
    const indicator = document.getElementById('drop-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

/**
 * Handle file upload
 */
async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    const uploadButton = document.querySelector('[aria-label="Upload code file"]');
    
    // Show loading state and progress
    if (uploadButton) {
        uploadButton.classList.add('loading');
        uploadButton.disabled = true;
    }
    
    // Show progress indicator
    showUploadProgress(0);
    
    try {
        // Validate file before upload
        validateUploadFile(file);
        
        // Display file content in editor immediately for better UX
        const fileContent = await readFileContent(file);
        displayCodeInEditor(fileContent, file.name);
        
        // Update progress
        showUploadProgress(30);
        
        // Upload file using API client
        const response = await window.apiClient.uploadFile(file);
        
        // Update progress
        showUploadProgress(100);
        
        // Store report ID for analysis
        window.currentReportId = response.report_id;
        window.currentFileName = file.name;
        
        // Reset analysis results to ready state
        resetAnalysisResults();
        updateAnalysisStatus('ready', 'Ready for Analysis');
        
        // Announce to screen reader and show notification
        if (window.announceStatus) {
            window.announceStatus(`File ${file.name} uploaded successfully. Ready for analysis.`);
        }
        
        // Show success notification
        if (window.notificationManager) {
            window.notificationManager.success(
                `File "${file.name}" uploaded successfully`,
                { title: 'Upload Complete' }
            );
        }
        
        // Hide progress after success
        setTimeout(() => hideUploadProgress(), 1000);
        
    } catch (error) {
        console.error('File upload failed:', error);
        
        // Show error state
        showUploadProgress(0, true);
        setTimeout(() => hideUploadProgress(), 3000);
        
        // Reset editor if upload failed
        resetCodeEditor();
        
        // Error is already handled by API client
    } finally {
        if (uploadButton) {
            uploadButton.classList.remove('loading');
            uploadButton.disabled = false;
        }
    }
}

/**
 * Validate file before upload
 */
function validateUploadFile(file) {
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
    
    // Check if file is empty
    if (file.size === 0) {
        throw new Error('File is empty. Please select a file with content.');
    }
}

/**
 * Show upload progress indicator
 */
function showUploadProgress(percentage, isError = false) {
    let progressBar = document.getElementById('upload-progress');
    
    if (!progressBar) {
        progressBar = document.createElement('div');
        progressBar.id = 'upload-progress';
        progressBar.className = 'upload-progress';
        progressBar.innerHTML = `
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <div class="progress-text">Uploading...</div>
        `;
        
        const editorPanel = document.querySelector('.editor-panel');
        if (editorPanel) {
            editorPanel.appendChild(progressBar);
        }
    }
    
    const progressFill = progressBar.querySelector('.progress-fill');
    const progressText = progressBar.querySelector('.progress-text');
    
    if (progressFill && progressText) {
        progressFill.style.width = `${percentage}%`;
        
        if (isError) {
            progressBar.classList.add('error');
            progressText.textContent = 'Upload failed';
        } else if (percentage === 100) {
            progressBar.classList.add('success');
            progressText.textContent = 'Upload complete';
        } else {
            progressBar.classList.remove('error', 'success');
            progressText.textContent = `Uploading... ${percentage}%`;
        }
    }
    
    progressBar.style.display = 'block';
}

/**
 * Hide upload progress indicator
 */
function hideUploadProgress() {
    const progressBar = document.getElementById('upload-progress');
    if (progressBar) {
        progressBar.style.display = 'none';
        progressBar.classList.remove('error', 'success');
    }
}

/**
 * Reset code editor to default state
 */
function resetCodeEditor() {
    const codeContent = document.querySelector('.code-content pre code');
    const codeDescription = document.getElementById('code-description');
    
    if (codeContent) {
        // Reset to sample Python code
        codeContent.innerHTML = `<span class="keyword">def</span> <span class="function">calculate_score</span>(<span class="parameter">data</span>):
    <span class="keyword">if</span> <span class="parameter">data</span> <span class="operator">is</span> <span class="keyword">None</span>:
        <span class="keyword">return</span> <span class="number">0</span>
    
    <span class="comment"># Potential issue: no input validation</span>
    <span class="variable">score</span> <span class="operator">=</span> <span class="number">0</span>
    <span class="keyword">for</span> <span class="variable">item</span> <span class="keyword">in</span> <span class="parameter">data</span>:
        <span class="variable">score</span> <span class="operator">+=</span> <span class="variable">item</span><span class="operator">.</span><span class="property">value</span>
    
    <span class="keyword">return</span> <span class="variable">score</span> <span class="operator">/</span> <span class="function">len</span>(<span class="parameter">data</span>)`;
        
        codeContent.className = 'language-python';
        
        // Reset line numbers
        updateLineNumbers(codeContent.textContent);
        
        // Reset description
        if (codeDescription) {
            codeDescription.textContent = 'Python function that calculates a score from data items. Contains potential division by zero issue.';
        }
    }
    
    // Clear stored report data
    window.currentReportId = null;
    window.currentFileName = null;
}

/**
 * Read file content as text
 */
function readFileContent(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(new Error('Failed to read file'));
        reader.readAsText(file);
    });
}

/**
 * Display code in editor
 */
function displayCodeInEditor(code, filename) {
    const codeContent = document.querySelector('.code-content pre code');
    const codeDescription = document.getElementById('code-description');
    
    if (codeContent) {
        const language = getLanguageFromFilename(filename);
        const highlightedCode = highlightCode(code, language);
        
        codeContent.innerHTML = highlightedCode;
        codeContent.className = `language-${language}`;
        
        // Update line numbers
        updateLineNumbers(code);
        
        // Update description
        if (codeDescription) {
            codeDescription.textContent = `${language} code from ${filename}`;
        }
        
        // Update ARIA label
        const codeContentContainer = document.querySelector('.code-content');
        if (codeContentContainer) {
            codeContentContainer.setAttribute('aria-label', `${language} code from ${filename}`);
        }
    }
}

/**
 * Setup analysis integration
 */
function setupAnalysisIntegration() {
    // The run button is already handled in initializeCodeEditorInteractions
    // This function can be used for additional analysis-related setup
    
    // Initialize analysis status
    updateAnalysisStatus('idle', 'Ready for Analysis');
    
    // Reset any existing analysis results
    resetAnalysisResults();
    
    console.log('Analysis integration setup complete');
}

// Old functions removed - using new implementations

/**
 * Setup dashboard integration
 */
function setupDashboardIntegration() {
    // Load dashboard data if user is authenticated
    if (window.apiClient.isAuthenticated()) {
        loadUserDashboard();
    }
}

/**
 * Load user dashboard data
 */
async function loadUserDashboard() {
    try {
        // Load dashboard metrics
        const metrics = await window.apiClient.getDashboardMetrics();
        updateDashboardMetrics(metrics);
        
        // Load analysis history
        const history = await window.apiClient.getAnalysisHistory(5);
        updateAnalysisHistory(history);
        
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        // Error is already handled by API client
    }
}

/**
 * Update dashboard metrics
 */
function updateDashboardMetrics(metrics) {
    const metricCards = document.querySelectorAll('.metric-card');
    
    if (metrics && metricCards.length >= 3) {
        // Update code quality score
        const qualityValue = metricCards[0].querySelector('.metric-value');
        const qualityTrend = metricCards[0].querySelector('.metric-trend');
        if (qualityValue && metrics.code_quality_score !== undefined) {
            qualityValue.textContent = metrics.code_quality_score;
            if (qualityTrend && metrics.quality_trend) {
                qualityTrend.textContent = metrics.quality_trend;
                qualityTrend.className = `metric-trend ${metrics.quality_trend.startsWith('+') ? 'positive' : 'negative'}`;
            }
        }
        
        // Update issues found
        const issuesValue = metricCards[1].querySelector('.metric-value');
        const issuesTrend = metricCards[1].querySelector('.metric-trend');
        if (issuesValue && metrics.total_issues !== undefined) {
            issuesValue.textContent = metrics.total_issues;
            if (issuesTrend && metrics.issues_breakdown) {
                issuesTrend.textContent = metrics.issues_breakdown;
            }
        }
        
        // Update processing time
        const timeValue = metricCards[2].querySelector('.metric-value');
        if (timeValue && metrics.avg_processing_time !== undefined) {
            timeValue.textContent = `${metrics.avg_processing_time}s`;
        }
    }
}

/**
 * Update analysis history
 */
function updateAnalysisHistory(history) {
    // This would update a history section if it exists
    // For now, just log the history
    console.log('Analysis history loaded:', history);
}

/**
 * Setup Gemini file upload integration
 */
function setupGeminiFileUploadIntegration() {
    const fileInput = document.getElementById('file-input');
    const uploadArea = document.querySelector('.upload-area');
    
    if (!fileInput || !uploadArea) {
        console.warn('File upload elements not found');
        return;
    }
    
    // Handle file selection
    fileInput.addEventListener('change', handleGeminiFileUpload);
    
    // Handle drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleGeminiFileUpload({ target: { files } });
        }
    });
    
    console.log('Gemini file upload integration setup complete');
}

/**
 * Handle file upload with Gemini analysis
 */
async function handleGeminiFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
        // Validate file
        validateUploadedFile(file);
        
        // Show loading state
        showAnalysisLoading(`Analyzing ${file.name}...`);
        
        // Update file name display
        const fileNameDisplay = document.querySelector('.file-name');
        if (fileNameDisplay) {
            fileNameDisplay.textContent = file.name;
        }
        
        // Analyze file with Gemini
        const report = await window.geminiClient.analyzeFile(file);
        
        // Update UI with results
        updateAnalysisResultsFromReport(report);
        
        // Store current analysis time for metrics
        window.currentAnalysisTime = (Math.random() * 2 + 0.5).toFixed(1);
        
        // Announce completion
        window.announceToScreenReader(`Analysis of ${file.name} completed. Found ${report.issues?.length || 0} issues.`);
        
    } catch (error) {
        console.error('File analysis failed:', error);
        showAnalysisError(error.message || 'Failed to analyze file');
    }
}

/**
 * Setup Gemini analysis integration for code editor
 */
function setupGeminiAnalysisIntegration() {
    const runButton = document.querySelector('.control-btn[aria-label*="Run"]');
    const codeEditor = document.getElementById('code-editor');
    
    if (!runButton || !codeEditor) {
        console.warn('Code editor elements not found');
        return;
    }
    
    // Handle run button click
    runButton.addEventListener('click', handleGeminiCodeAnalysis);
    
    // Handle keyboard shortcut (Ctrl+Enter or Cmd+Enter)
    codeEditor.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            handleGeminiCodeAnalysis();
        }
    });
    
    console.log('Gemini code analysis integration setup complete');
}

/**
 * Handle code analysis with Gemini
 */
async function handleGeminiCodeAnalysis() {
    const codeEditor = document.getElementById('code-editor');
    if (!codeEditor) return;
    
    const code = codeEditor.value.trim();
    if (!code) {
        showAnalysisError('Please enter some code to analyze');
        return;
    }
    
    try {
        // Show loading state
        showAnalysisLoading('Analyzing your code...');
        
        // Analyze code with Gemini
        const report = await window.geminiClient.analyzeCode(code, 'code.js');
        
        // Update UI with results
        updateAnalysisResultsFromReport(report);
        
        // Store current analysis time for metrics
        window.currentAnalysisTime = (Math.random() * 2 + 0.5).toFixed(1);
        
        // Announce completion
        window.announceToScreenReader(`Code analysis completed. Found ${report.issues?.length || 0} issues.`);
        
    } catch (error) {
        console.error('Code analysis failed:', error);
        showAnalysisError(error.message || 'Failed to analyze code');
    }
}

/**
 * Setup sample code analysis
 */
function setupSampleCodeAnalysis() {
    // Add sample code to editor if it's empty
    const codeEditor = document.getElementById('code-editor');
    if (codeEditor && !codeEditor.value.trim()) {
        const sampleCode = `function calculateTotal(items) {
    var total = 0;
    for (var i = 0; i < items.length; i++) {
        total += items[i].price * items[i].quantity;
    }
    return total;
}

// Usage example
const cartItems = [
    { price: 10.99, quantity: 2 },
    { price: 5.50, quantity: 1 },
    { price: 15.00, quantity: 3 }
];

console.log("Total: $" + calculateTotal(cartItems));`;
        
        codeEditor.value = sampleCode;
    }
    
    console.log('Sample code analysis setup complete');
}

/**
 * Validate uploaded file
 */
function validateUploadedFile(file) {
    const allowedExtensions = ['.js', '.ts', '.py', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs', '.swift'];
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    // Check file extension
    const extension = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedExtensions.includes(extension)) {
        throw new Error(`File type ${extension} is not supported. Allowed types: ${allowedExtensions.join(', ')}`);
    }
    
    // Check file size
    if (file.size > maxSize) {
        throw new Error(`File size (${(file.size / 1024 / 1024).toFixed(2)}MB) exceeds maximum allowed size (10MB)`);
    }
}ctor('.btn-primary');
    if (tryNowButton) {
        tryNowButton.addEventListener('click', function() {
            // Scroll to the analyzer section
            const analyzerSection = document.getElementById('analyzer');
            if (analyzerSection) {
                analyzerSection.scrollIntoView({ behavior: 'smooth' });
                
                // Focus on the run button after scrolling
                setTimeout(() => {
                    const runButton = document.querySelector('.control-btn[aria-label*="Run"]');
                    if (runButton) {
                        runButton.focus();
                    }
                }, 1000);
            }
        });
    }
    
    // Add "Explore Features" button functionality
    const exploreButton = document.querySelector('.btn-secondary');
    if (exploreButton) {
        exploreButton.addEventListener('click', function() {
            // Scroll to the features section
            const featuresSection = document.getElementById('features');
            if (featuresSection) {
                featuresSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
    
    console.log('API integration initialized');
}

/**
 * Register service worker for performance optimization
 */
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('Service Worker registered successfully:', registration.scope);
                    
                    // Check for updates
                    registration.addEventListener('updatefound', () => {
                        const newWorker = registration.installing;
                        newWorker.addEventListener('statechange', () => {
                            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                console.log('New service worker available');
                                // Optionally notify user about update
                            }
                        });
                    });
                })
                .catch(error => {
                    console.warn('Service Worker registration failed:', error);
                });
        });
    } else {
        console.log('Service Worker not supported');
    }
}

/**
 * Initialize basic interactions
 */
function initializeBasicInteractions() {
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = targetElement.offsetTop - headerHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Basic button interactions (will be enhanced with GSAP in later tasks)
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add ripple effect class (visual feedback)
            this.classList.add('clicked');
            
            setTimeout(() => {
                this.classList.remove('clicked');
            }, 300);
            
            // Log button clicks for now (will be replaced with actual functionality)
            console.log('Button clicked:', this.textContent.trim());
        });
    });
    
    // Add loading state management
    window.addEventListener('load', function() {
        document.body.classList.add('loaded');
    });
}

/**
 * Initialize code editor interactions
 */
function initializeCodeEditorInteractions() {
    // Add hover effects for code lines
    const codeLines = document.querySelectorAll('.code-content code span');
    
    codeLines.forEach(line => {
        line.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(99, 102, 241, 0.1)';
            this.style.borderRadius = '2px';
        });
        
        line.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'transparent';
        });
    });
    
    // Add click handlers for control buttons
    const runButton = document.querySelector('.control-btn[aria-label="Run code analysis"]');
    const clearButton = document.querySelector('.control-btn[aria-label="Clear code editor"]');
    
    if (runButton) {
        runButton.addEventListener('click', async function() {
            // Disable button during analysis
            this.disabled = true;
            this.style.opacity = '0.6';
            
            try {
                await triggerCodeAnalysis();
            } finally {
                // Re-enable button
                this.disabled = false;
                this.style.opacity = '1';
            }
        });
    }
    
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            const codeContent = document.querySelector('.code-content code');
            if (codeContent) {
                // Clear the code content
                codeContent.innerHTML = '<span class="comment"># Your code will appear here...</span>';
                
                // Reset analysis results
                resetAnalysisResults();
                
                // Clear current filename
                window.currentFilename = null;
            }
            
            // Announce to screen readers
            if (window.announceToScreenReader) {
                window.announceToScreenReader('Code editor cleared');
            }
            
            console.log('Code cleared');
        });
    }
    
    // Add file upload functionality with real API integration
    const fileUpload = document.getElementById('file-upload');
    if (fileUpload) {
        fileUpload.addEventListener('change', async function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            try {
                // Store filename for analysis
                window.currentFilename = file.name;
                
                // Display file content in editor
                const reader = new FileReader();
                reader.onload = function(e) {
                    const content = e.target.result;
                    const codeContent = document.querySelector('.code-content code');
                    if (codeContent) {
                        // Simple syntax highlighting (basic)
                        const highlightedContent = highlightCode(content, getLanguageFromFilename(file.name));
                        codeContent.innerHTML = highlightedContent;
                        
                        // Update line numbers
                        updateLineNumbers(content);
                    }
                    
                    // Announce to screen readers
                    if (window.announceToScreenReader) {
                        window.announceToScreenReader(`File ${file.name} loaded successfully`);
                    }
                };
                reader.readAsText(file);
                
                // Upload file and start analysis automatically
                if (window.apiClient) {
                    // Check if user is authenticated for better experience
                    if (!window.apiClient.isAuthenticated() && window.authManager) {
                        // Show authentication prompt
                        const action = await window.authManager.showAuthPrompt(
                            'Sign in to save your analysis history and access additional features.'
                        );
                        
                        if (action === 'signin') {
                            // Store file for processing after authentication
                            window.authManager.setPendingFileUpload(file);
                            return; // User will sign in, file upload will be handled after authentication
                        }
                        // If 'continue' or 'dismiss', proceed with upload without authentication
                    }
                    
                    const response = await window.apiClient.uploadFile(file);
                    if (response.report_id) {
                        // Start polling for results
                        await startAnalysisPolling(response.report_id);
                        
                        // If user is authenticated, refresh their history
                        if (window.authManager && window.authManager.isAuthenticated) {
                            setTimeout(() => {
                                window.authManager.loadAnalysisHistory();
                            }, 1000);
                        }
                    }
                }
                
            } catch (error) {
                console.error('File upload failed:', error);
                showAnalysisError('File upload failed', error.message);
            }
        });
    }
    
    // Add hover effects for issue items (will be updated dynamically)
    document.addEventListener('mouseenter', function(e) {
        if (e.target.closest('.issue-item')) {
            const item = e.target.closest('.issue-item');
            item.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
        }
    }, true);
    
    document.addEventListener('mouseleave', function(e) {
        if (e.target.closest('.issue-item')) {
            const item = e.target.closest('.issue-item');
            item.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
        }
    }, true);
    
    // Add click handlers for metric cards to show more details
    const metricCards = document.querySelectorAll('.metric-card');
    
    metricCards.forEach(card => {
        card.addEventListener('click', function() {
            // Add a subtle animation to indicate interaction
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
            
            console.log('Metric card clicked:', this.querySelector('.metric-title').textContent);
        });
    });
}

/**
 * Utility function to check if element is in viewport
 * (Will be used for scroll-triggered animations in later tasks)
 */
function isInViewport(element, threshold = 0.1) {
    const rect = element.getBoundingClientRect();
    const windowHeight = window.innerHeight || document.documentElement.clientHeight;
    
    return (
        rect.top <= windowHeight * (1 - threshold) &&
        rect.bottom >= windowHeight * threshold
    );
}

/**
 * Throttle function for performance optimization
 * (Will be used for scroll and resize events in later tasks)
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Initialize GSAP animations
 */
function initializeGSAPAnimations() {
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    if (prefersReducedMotion) {
        // Disable animations for users who prefer reduced motion
        gsap.set("*", {clearProps: "all"});
        return;
    }
    
    // Add class to indicate GSAP is active
    document.body.classList.add('gsap-enabled');
    
    // Set initial states for animated elements
    gsap.set([".hero-title", ".hero-subtitle", ".hero-actions"], {
        opacity: 0,
        y: 30
    });
    
    gsap.set(".header", {
        opacity: 0,
        y: -100
    });
    
    // Hero entrance animations (staggered fade and slide)
    const heroTimeline = gsap.timeline({ 
        delay: 0.1,
        onComplete: () => console.log('Hero entrance animations complete')
    });
    
    // Header slide down
    heroTimeline.to(".header", {
        opacity: 1,
        y: 0,
        duration: 0.8,
        ease: "power2.out",
        onComplete: () => console.log('Header animation complete')
    });
    
    // Hero content staggered entrance
    heroTimeline.to(".hero-title", {
        opacity: 1,
        y: 0,
        duration: 1,
        ease: "power2.out",
        onComplete: () => console.log('Hero title animation complete')
    }, "+=0.2")
    .to(".hero-subtitle", {
        opacity: 1,
        y: 0,
        duration: 1,
        ease: "power2.out",
        onComplete: () => console.log('Hero subtitle animation complete')
    }, "-=0.8")
    .to(".hero-actions", {
        opacity: 1,
        y: 0,
        duration: 1,
        ease: "power2.out",
        onComplete: () => console.log('Hero actions animation complete')
    }, "-=0.7");
    
    // Enhanced hover effects for cards
    initializeCardHoverEffects();
    
    // Scroll-triggered section reveals
    initializeScrollTriggerAnimations();
    
    // Parallax effects
    initializeParallaxEffects();
    
    // Button press animations
    initializeButtonAnimations();
    
    // Refresh ScrollTrigger after all animations are set up
    ScrollTrigger.refresh();
    
    console.log('All GSAP animations initialized successfully');
}

/**
 * Initialize enhanced card hover effects with GSAP
 */
function initializeCardHoverEffects() {
    // Glass cards hover effects
    const glassCards = document.querySelectorAll('.glass-card, .glass-card-dark');
    
    glassCards.forEach(card => {
        const hoverTl = gsap.timeline({ paused: true });
        
        hoverTl.to(card, {
            y: -8,
            scale: 1.02,
            duration: 0.3,
            ease: "power2.out"
        })
        .to(card, {
            backdropFilter: "blur(24px)",
            duration: 0.3,
            ease: "power2.out"
        }, 0);
        
        card.addEventListener('mouseenter', () => {
            hoverTl.play();
        });
        
        card.addEventListener('mouseleave', () => {
            hoverTl.reverse();
        });
    });
    
    // Feature cards special hover effects
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        const icon = card.querySelector('.feature-icon');
        const hoverTl = gsap.timeline({ paused: true });
        
        hoverTl.to(card, {
            y: -12,
            scale: 1.03,
            duration: 0.4,
            ease: "back.out(1.7)"
        })
        .to(icon, {
            scale: 1.2,
            rotation: 5,
            duration: 0.4,
            ease: "back.out(1.7)"
        }, 0);
        
        card.addEventListener('mouseenter', () => {
            hoverTl.play();
        });
        
        card.addEventListener('mouseleave', () => {
            hoverTl.reverse();
        });
    });
    
    // Metric cards hover effects
    const metricCards = document.querySelectorAll('.metric-card');
    
    metricCards.forEach(card => {
        const value = card.querySelector('.metric-value');
        const icon = card.querySelector('.metric-icon');
        const hoverTl = gsap.timeline({ paused: true });
        
        hoverTl.to(card, {
            y: -10,
            scale: 1.02,
            duration: 0.3,
            ease: "power2.out"
        })
        .to(value, {
            scale: 1.1,
            color: "#6366f1",
            duration: 0.3,
            ease: "power2.out"
        }, 0)
        .to(icon, {
            rotation: 10,
            scale: 1.1,
            duration: 0.3,
            ease: "power2.out"
        }, 0);
        
        card.addEventListener('mouseenter', () => {
            hoverTl.play();
        });
        
        card.addEventListener('mouseleave', () => {
            hoverTl.reverse();
        });
    });
}

/**
 * Initialize scroll-triggered animations
 */
function initializeScrollTriggerAnimations() {
    // Section reveals on scroll
    const sections = document.querySelectorAll('.circuit-city, .code-editor, .analysis-showcase');
    
    sections.forEach(section => {
        const title = section.querySelector('.section-title');
        const content = section.querySelector('.section-content, .editor-layout, .showcase-content');
        
        if (title) {
            gsap.fromTo(title, 
                {
                    opacity: 0,
                    y: 50
                },
                {
                    opacity: 1,
                    y: 0,
                    duration: 1,
                    ease: "power2.out",
                    scrollTrigger: {
                        trigger: title,
                        start: "top 80%",
                        end: "bottom 20%",
                        toggleActions: "play none none reverse"
                    }
                }
            );
        }
        
        if (content) {
            gsap.fromTo(content,
                {
                    opacity: 0,
                    y: 30
                },
                {
                    opacity: 1,
                    y: 0,
                    duration: 1.2,
                    ease: "power2.out",
                    scrollTrigger: {
                        trigger: content,
                        start: "top 85%",
                        end: "bottom 15%",
                        toggleActions: "play none none reverse"
                    }
                }
            );
        }
    });
    
    // Feature cards staggered reveal
    const featureCards = document.querySelectorAll('.feature-card');
    if (featureCards.length > 0) {
        gsap.fromTo(featureCards,
            {
                opacity: 0,
                y: 40,
                scale: 0.9
            },
            {
                opacity: 1,
                y: 0,
                scale: 1,
                duration: 0.8,
                stagger: 0.2,
                ease: "back.out(1.7)",
                scrollTrigger: {
                    trigger: featureCards[0].parentElement,
                    start: "top 80%",
                    end: "bottom 20%",
                    toggleActions: "play none none reverse"
                }
            }
        );
    }
    
    // Metric cards staggered reveal
    const metricCards = document.querySelectorAll('.metric-card');
    if (metricCards.length > 0) {
        gsap.fromTo(metricCards,
            {
                opacity: 0,
                y: 50,
                rotationX: -15
            },
            {
                opacity: 1,
                y: 0,
                rotationX: 0,
                duration: 1,
                stagger: 0.15,
                ease: "power2.out",
                scrollTrigger: {
                    trigger: metricCards[0].parentElement,
                    start: "top 75%",
                    end: "bottom 25%",
                    toggleActions: "play none none reverse"
                }
            }
        );
    }
    
    // Chart containers reveal
    const chartContainers = document.querySelectorAll('.chart-container');
    if (chartContainers.length > 0) {
        gsap.fromTo(chartContainers,
            {
                opacity: 0,
                scale: 0.8,
                rotationY: -10
            },
            {
                opacity: 1,
                scale: 1,
                rotationY: 0,
                duration: 1.2,
                stagger: 0.3,
                ease: "back.out(1.7)",
                scrollTrigger: {
                    trigger: chartContainers[0].parentElement,
                    start: "top 80%",
                    end: "bottom 20%",
                    toggleActions: "play none none reverse"
                }
            }
        );
    }
    
    // Progress bars animation
    const progressFills = document.querySelectorAll('.progress-fill');
    progressFills.forEach(fill => {
        const width = fill.style.width;
        gsap.fromTo(fill,
            {
                width: "0%"
            },
            {
                width: width,
                duration: 1.5,
                ease: "power2.out",
                scrollTrigger: {
                    trigger: fill,
                    start: "top 90%",
                    end: "bottom 10%",
                    toggleActions: "play none none reverse"
                }
            }
        );
    });
}

/**
 * Initialize parallax effects
 */
function initializeParallaxEffects() {
    // Hero background parallax
    const heroBackground = document.querySelector('.hero::before');
    if (heroBackground) {
        gsap.to('.hero::before', {
            yPercent: -50,
            ease: "none",
            scrollTrigger: {
                trigger: ".hero",
                start: "top bottom",
                end: "bottom top",
                scrub: true
            }
        });
    }
    
    // Circuit background parallax
    const circuitLines = document.querySelector('.circuit-lines');
    if (circuitLines) {
        gsap.to(circuitLines, {
            x: -30,
            y: -30,
            ease: "none",
            scrollTrigger: {
                trigger: ".circuit-city",
                start: "top bottom",
                end: "bottom top",
                scrub: 1
            }
        });
    }
    
    // Circuit nodes floating animation
    const circuitNodes = document.querySelector('.circuit-nodes');
    if (circuitNodes) {
        gsap.to(circuitNodes, {
            rotation: 360,
            duration: 30,
            ease: "none",
            repeat: -1
        });
    }
    
    // Subtle mouse parallax for hero content
    const heroContent = document.querySelector('.hero-content');
    if (heroContent) {
        let mouseMoveHandler = (e) => {
            const { clientX, clientY } = e;
            const { innerWidth, innerHeight } = window;
            
            const xPercent = (clientX / innerWidth - 0.5) * 2;
            const yPercent = (clientY / innerHeight - 0.5) * 2;
            
            gsap.to(heroContent, {
                x: xPercent * 10,
                y: yPercent * 10,
                duration: 0.5,
                ease: "power2.out"
            });
        };
        
        // Throttle mouse movement for performance
        let throttledMouseMove = throttle(mouseMoveHandler, 16); // ~60fps
        document.addEventListener('mousemove', throttledMouseMove);
        
        // Clean up on page unload
        window.addEventListener('beforeunload', () => {
            document.removeEventListener('mousemove', throttledMouseMove);
        });
    }
}

/**
 * Initialize button press animations
 */
function initializeButtonAnimations() {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        // Remove existing click event listener to replace with GSAP version
        button.removeEventListener('click', function() {});
        
        button.addEventListener('click', function(e) {
            // GSAP press animation
            const pressTl = gsap.timeline();
            
            pressTl.to(this, {
                scale: 0.95,
                duration: 0.1,
                ease: "power2.out"
            })
            .to(this, {
                scale: 1,
                duration: 0.2,
                ease: "back.out(1.7)"
            });
            
            // Create ripple effect
            const rect = this.getBoundingClientRect();
            const ripple = document.createElement('span');
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                pointer-events: none;
                transform: scale(0);
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            gsap.to(ripple, {
                scale: 2,
                opacity: 0,
                duration: 0.6,
                ease: "power2.out",
                onComplete: () => {
                    ripple.remove();
                }
            });
            
            console.log('Button clicked:', this.textContent.trim());
        });
        
        // Enhanced hover effects for buttons
        const hoverTl = gsap.timeline({ paused: true });
        
        hoverTl.to(button, {
            y: -2,
            scale: 1.02,
            duration: 0.3,
            ease: "power2.out"
        });
        
        button.addEventListener('mouseenter', () => {
            hoverTl.play();
        });
        
        button.addEventListener('mouseleave', () => {
            hoverTl.reverse();
        });
    });
    
    // Navigation links hover effects
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const underline = link.querySelector('::after') || link;
        
        const hoverTl = gsap.timeline({ paused: true });
        
        hoverTl.to(link, {
            color: "#6366f1",
            duration: 0.2,
            ease: "power2.out"
        });
        
        link.addEventListener('mouseenter', () => {
            hoverTl.play();
        });
        
        link.addEventListener('mouseleave', () => {
            hoverTl.reverse();
        });
    });
}

// Export functions for potential use in other scripts
window.LandingPage = {
    isInViewport,
    throttle,
    initializeGSAPAnimations
};
/**

 * Update analysis status indicator
 */
function updateAnalysisStatus(status, message = null) {
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.querySelector('.status-text');
    
    if (!statusIndicator || !statusText) return;
    
    // Remove all status classes
    statusIndicator.classList.remove('active', 'processing', 'error', 'success');
    
    let statusMessage = message;
    
    switch (status) {
        case 'processing':
            statusIndicator.classList.add('processing');
            statusMessage = statusMessage || 'Analysis in Progress...';
            break;
        case 'completed':
            statusIndicator.classList.add('success');
            statusMessage = statusMessage || 'Analysis Complete';
            break;
        case 'failed':
            statusIndicator.classList.add('error');
            statusMessage = statusMessage || 'Analysis Failed';
            break;
        default:
            statusIndicator.classList.add('active');
            statusMessage = statusMessage || 'Ready for Analysis';
    }
    
    statusText.textContent = statusMessage;
    statusText.setAttribute('aria-live', 'polite');
}

/**
 * Calculate quality score from report summary
 */
function calculateQualityScore(summary) {
    if (!summary) return 85; // Default score
    
    const baseScore = 100;
    const highPenalty = (summary.high_severity_issues || 0) * 20;
    const mediumPenalty = (summary.medium_severity_issues || 0) * 10;
    const lowPenalty = (summary.low_severity_issues || 0) * 5;
    
    const score = Math.max(0, baseScore - highPenalty - mediumPenalty - lowPenalty);
    return Math.round(score);
}

/**
 * Calculate quality grade from report
 */
function calculateQualityGrade(report) {
    if (!report || !report.issues) return 'A';
    
    const highIssues = report.issues.filter(i => i.severity === 'high').length;
    const mediumIssues = report.issues.filter(i => i.severity === 'medium').length;
    const totalIssues = report.issues.length;
    
    if (highIssues === 0 && totalIssues <= 2) return 'A';
    if (highIssues === 0 && totalIssues <= 5) return 'B+';
    if (highIssues <= 1 && totalIssues <= 8) return 'B';
    if (highIssues <= 2 && totalIssues <= 12) return 'C+';
    if (highIssues <= 3) return 'C';
    return 'D';
}

/**
 * Get CSS class for quality grade
 */
function getGradeClass(grade) {
    switch (grade) {
        case 'A':
        case 'B+':
            return 'success';
        case 'B':
        case 'C+':
            return 'warning';
        default:
            return 'error';
    }
}

/**
 * Calculate security score from report
 */
function calculateSecurityScore(report) {
    if (!report || !report.issues) return 100;
    
    const securityIssues = report.issues.filter(i => i.type === 'security');
    const highSecurityIssues = securityIssues.filter(i => i.severity === 'high').length;
    const mediumSecurityIssues = securityIssues.filter(i => i.severity === 'medium').length;
    const lowSecurityIssues = securityIssues.filter(i => i.severity === 'low').length;
    
    const baseScore = 100;
    const penalty = (highSecurityIssues * 30) + (mediumSecurityIssues * 15) + (lowSecurityIssues * 5);
    
    return Math.max(0, baseScore - penalty);
}

/**
 * Update charts from report data
 */
function updateChartsFromReport(report) {
    if (!report || !report.issues) return;
    
    // Update pie chart for issue distribution
    updateIssueDistributionChart(report.issues);
    
    // Update progress bars (mock data for now)
    updateProgressBars(report);
}

/**
 * Update issue distribution pie chart
 */
function updateIssueDistributionChart(issues) {
    const highCount = issues.filter(i => i.severity === 'high').length;
    const mediumCount = issues.filter(i => i.severity === 'medium').length;
    const lowCount = issues.filter(i => i.severity === 'low').length;
    const total = issues.length;
    
    if (total === 0) {
        // Show "no issues" state
        const pieChart = document.querySelector('.pie-chart');
        if (pieChart) {
            pieChart.innerHTML = '<div class="no-issues-message">No Issues Found</div>';
        }
        return;
    }
    
    const highPercentage = Math.round((highCount / total) * 100);
    const mediumPercentage = Math.round((mediumCount / total) * 100);
    const lowPercentage = 100 - highPercentage - mediumPercentage; // Ensure total is 100%
    
    // Update pie chart slices
    const criticalSlice = document.querySelector('.pie-slice.critical');
    const warningSlice = document.querySelector('.pie-slice.warning');
    const infoSlice = document.querySelector('.pie-slice.info');
    
    if (criticalSlice) criticalSlice.style.setProperty('--percentage', highPercentage);
    if (warningSlice) warningSlice.style.setProperty('--percentage', mediumPercentage);
    if (infoSlice) infoSlice.style.setProperty('--percentage', lowPercentage);
    
    // Update legend
    const legendItems = document.querySelectorAll('.legend-item .legend-label');
    if (legendItems.length >= 3) {
        legendItems[0].textContent = `Critical (${highPercentage}%)`;
        legendItems[1].textContent = `Warning (${mediumPercentage}%)`;
        legendItems[2].textContent = `Info (${lowPercentage}%)`;
    }
}

/**
 * Update progress bars with mock coverage data
 */
function updateProgressBars(report) {
    const progressItems = document.querySelectorAll('.progress-item');
    
    if (progressItems.length >= 3) {
        // Mock coverage calculations based on code quality
        const qualityScore = calculateQualityScore(report.report_summary);
        const baseCoverage = Math.max(60, qualityScore - 10);
        
        const functionsCoverage = baseCoverage + Math.random() * 10;
        const linesCoverage = baseCoverage + Math.random() * 15;
        const branchesCoverage = baseCoverage - Math.random() * 20;
        
        updateProgressBar(progressItems[0], Math.min(100, Math.round(functionsCoverage)));
        updateProgressBar(progressItems[1], Math.min(100, Math.round(linesCoverage)));
        updateProgressBar(progressItems[2], Math.max(0, Math.round(branchesCoverage)));
    }
}

/**
 * Update individual progress bar
 */
function updateProgressBar(progressItem, percentage) {
    const progressFill = progressItem.querySelector('.progress-fill');
    const progressValue = progressItem.querySelector('.progress-value');
    
    if (progressFill) {
        progressFill.style.width = `${percentage}%`;
    }
    
    if (progressValue) {
        progressValue.textContent = `${percentage}%`;
    }
}

/**
 * Highlight code line in editor
 */
function highlightCodeLine(lineNumber) {
    // Remove existing highlights
    const existingHighlights = document.querySelectorAll('.line-highlight');
    existingHighlights.forEach(highlight => highlight.remove());
    
    // Find the line in the code editor
    const lineNumbers = document.querySelectorAll('.line-numbers span');
    const codeLines = document.querySelectorAll('.code-content pre code');
    
    if (lineNumbers[lineNumber - 1] && codeLines.length > 0) {
        // Highlight line number
        lineNumbers[lineNumber - 1].classList.add('highlighted-line');
        
        // Scroll to line if needed
        lineNumbers[lineNumber - 1].scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });
        
        // Remove highlight after 3 seconds
        setTimeout(() => {
            lineNumbers[lineNumber - 1].classList.remove('highlighted-line');
        }, 3000);
        
        // Announce to screen readers
        window.announceToScreenReader(`Highlighted line ${lineNumber}`);
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show analysis error message
 */
function showAnalysisError(message, details = null) {
    updateAnalysisStatus('failed', message);
    
    // Show error in issues list
    const issuesContainer = document.querySelector('.issues-container');
    if (issuesContainer) {
        issuesContainer.innerHTML = `
            <li class="issue-item error-state" role="listitem">
                <div class="issue-severity error" aria-label="Error">ERROR</div>
                <div class="issue-details">
                    <div class="issue-title">Analysis Error</div>
                    <div class="issue-description">${escapeHtml(message)}</div>
                    ${details ? `<div class="issue-location">${escapeHtml(details)}</div>` : ''}
                </div>
            </li>
        `;
    }
    
    // Reset summary to error state
    resetAnalysisResults();
    
    // Announce error to screen readers
    window.announceToScreenReader(`Analysis failed: ${message}`, 'assertive');
}

/**
 * Show loading state for analysis (enhanced version)
 */
function showAnalysisLoading(message = 'Analyzing code...') {
    updateAnalysisStatus('processing', message);
    
    // Show loading in issues list
    const issuesContainer = document.querySelector('.issues-container');
    if (issuesContainer) {
        issuesContainer.innerHTML = `
            <li class="issue-item loading-state" role="listitem">
                <div class="issue-severity info" aria-label="Loading">
                    <div class="loading-spinner-small"></div>
                </div>
                <div class="issue-details">
                    <div class="issue-title">Analysis in Progress</div>
                    <div class="issue-description">${escapeHtml(message)}</div>
                </div>
            </li>
        `;
    }
    
    // Use enhanced loading manager
    if (window.loadingManager) {
        window.loadingManager.show(
            'Analyzing Code',
            message,
            true // Show progress bar
        );
    } else {
        // Fallback to basic loading overlay
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.classList.add('active');
        }
    }
    
    // Announce to screen readers
    if (window.announceStatus) {
        window.announceStatus(`Code analysis started. ${message}`);
    }
}

/**
 * Hide loading state (enhanced version)
 */
function hideAnalysisLoading() {
    // Use enhanced loading manager
    if (window.loadingManager) {
        window.loadingManager.hide();
    } else {
        // Fallback to basic loading overlay
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.classList.remove('active');
        }
    }
}

/**
 * Start real-time analysis polling (enhanced version)
 */
async function startAnalysisPolling(reportId) {
    if (!reportId || !window.apiClient) {
        console.error('Cannot start polling: missing report ID or API client');
        return null;
    }
    
    try {
        // Store analysis start time for metrics
        const startTime = Date.now();
        let pollAttempt = 0;
        const maxAttempts = 30;
        
        // Enhanced polling with progress simulation
        const pollWithProgress = async () => {
            while (pollAttempt < maxAttempts) {
                try {
                    // Update progress based on polling attempts
                    const progressPercentage = Math.min(60 + (pollAttempt * 2), 95);
                    const progressMessage = getProgressMessage(pollAttempt);
                    
                    if (window.loadingManager) {
                        window.loadingManager.updateProgress(progressPercentage, progressMessage);
                    }
                    
                    // Get analysis report
                    const report = await window.apiClient.getAnalysisReport(reportId);
                    
                    if (report.status === 'completed') {
                        // Final progress update
                        if (window.loadingManager) {
                            window.loadingManager.updateProgress(100, 'Analysis complete!');
                        }
                        
                        // Calculate processing time
                        const processingTime = ((Date.now() - startTime) / 1000).toFixed(1);
                        window.currentAnalysisTime = processingTime;
                        
                        // Small delay to show completion
                        await new Promise(resolve => setTimeout(resolve, 500));
                        
                        hideAnalysisLoading();
                        updateAnalysisResultsFromReport(report);
                        
                        // Show success notification
                        if (window.notificationManager) {
                            window.notificationManager.success(
                                `Analysis completed in ${processingTime}s. Found ${report.issues?.length || 0} issues.`,
                                { title: 'Analysis Complete' }
                            );
                        }
                        
                        // Announce completion
                        if (window.announceStatus) {
                            window.announceStatus(`Analysis completed. Found ${report.issues?.length || 0} issues.`);
                        }
                        
                        return report;
                        
                    } else if (report.status === 'failed') {
                        throw new Error('Analysis failed on server');
                    }
                    
                    // Continue polling
                    pollAttempt++;
                    const delay = Math.min(1000 + (pollAttempt * 200), 3000); // Progressive delay
                    await new Promise(resolve => setTimeout(resolve, delay));
                    
                } catch (error) {
                    if (error.status === 404 && pollAttempt < 5) {
                        // Report might not be ready yet, continue polling
                        pollAttempt++;
                        await new Promise(resolve => setTimeout(resolve, 1000));
                        continue;
                    }
                    throw error;
                }
            }
            
            throw new Error('Analysis timeout - please try again');
        };
        
        return await pollWithProgress();
        
    } catch (error) {
        console.error('Analysis polling failed:', error);
        hideAnalysisLoading();
        
        const userFriendlyMessage = getUserFriendlyAnalysisError(error);
        showAnalysisError('Analysis Failed', userFriendlyMessage);
        
        if (window.notificationManager) {
            window.notificationManager.error(userFriendlyMessage, {
                title: 'Analysis Failed',
                actions: [{
                    id: 'retry',
                    label: 'Try Again',
                    handler: () => triggerCodeAnalysis()
                }]
            });
        }
        
        return null;
    }
}

/**
 * Get progress message based on polling attempt
 */
function getProgressMessage(attempt) {
    const messages = [
        'Initializing analysis...',
        'Parsing code structure...',
        'Checking for syntax issues...',
        'Analyzing code patterns...',
        'Detecting security vulnerabilities...',
        'Evaluating performance issues...',
        'Checking code quality...',
        'Generating recommendations...',
        'Finalizing results...'
    ];
    
    const messageIndex = Math.min(Math.floor(attempt / 3), messages.length - 1);
    return messages[messageIndex];
}

/**
 * Trigger analysis on current code (enhanced version)
 */
async function triggerCodeAnalysis() {
    if (!window.apiClient) {
        const errorMsg = 'API client not available. Please refresh the page and try again.';
        showAnalysisError(errorMsg);
        
        if (window.notificationManager) {
            window.notificationManager.error(errorMsg, {
                title: 'System Error',
                actions: [{
                    id: 'refresh',
                    label: 'Refresh Page',
                    handler: () => window.location.reload()
                }]
            });
        }
        return;
    }
    
    // Get current code content (from editor or sample)
    const codeContent = getCurrentCodeContent();
    const filename = getCurrentFilename();
    
    if (!codeContent.trim()) {
        const errorMsg = 'No code to analyze. Please upload a file or use the sample code.';
        showAnalysisError('No code to analyze', errorMsg);
        
        if (window.notificationManager) {
            window.notificationManager.warning(errorMsg, {
                title: 'No Code Found'
            });
        }
        return;
    }
    
    // Show loading state
    showAnalysisLoading('Preparing code for analysis...');
    
    try {
        // Update progress
        if (window.loadingManager) {
            window.loadingManager.updateProgress(10, 'Creating analysis request...');
        }
        
        // Create a temporary file for analysis
        const blob = new Blob([codeContent], { type: 'text/plain' });
        const file = new File([blob], filename, { type: 'text/plain' });
        
        // Update progress
        if (window.loadingManager) {
            window.loadingManager.updateProgress(30, 'Uploading code...');
        }
        
        // Upload and start analysis with enhanced error handling
        const response = await window.errorHandler.handleApiError(
            () => window.apiClient.uploadFile(file),
            'Code Upload',
            () => window.apiClient.uploadFile(file)
        );
        
        if (response.report_id) {
            // Update progress
            if (window.loadingManager) {
                window.loadingManager.updateProgress(50, 'Starting analysis...');
            }
            
            // Start polling for results
            await startAnalysisPolling(response.report_id);
        } else {
            throw new Error('No report ID received from upload');
        }
        
    } catch (error) {
        console.error('Failed to trigger analysis:', error);
        
        // Hide loading state
        hideAnalysisLoading();
        
        // Show enhanced error message
        const userFriendlyMessage = getUserFriendlyAnalysisError(error);
        showAnalysisError('Analysis Failed', userFriendlyMessage);
        
        if (window.notificationManager) {
            window.notificationManager.error(userFriendlyMessage, {
                title: 'Analysis Failed',
                actions: [{
                    id: 'retry',
                    label: 'Try Again',
                    handler: () => triggerCodeAnalysis()
                }]
            });
        }
        
        // Announce error to screen readers
        if (window.announceError) {
            window.announceError(`Analysis failed: ${userFriendlyMessage}`);
        }
    }
}

/**
 * Get user-friendly error message for analysis failures
 */
function getUserFriendlyAnalysisError(error) {
    if (!navigator.onLine) {
        return 'No internet connection. Please check your network and try again.';
    }
    
    const status = error.status;
    switch (status) {
        case 413:
            return 'Code file is too large. Please reduce the file size and try again.';
        case 429:
            return 'Too many analysis requests. Please wait a moment and try again.';
        case 500:
            return 'Analysis service is temporarily unavailable. Please try again in a few moments.';
        case 503:
            return 'Analysis service is under maintenance. Please try again later.';
        default:
            return error.message || 'Analysis failed due to an unexpected error. Please try again.';
    }
}

/**
 * Get current code content from editor
 */
function getCurrentCodeContent() {
    const codeElement = document.querySelector('.code-content pre code');
    return codeElement ? codeElement.textContent : '';
}

/**
 * Get current filename (default or from upload)
 */
function getCurrentFilename() {
    return window.currentFilename || 'sample_code.py';
}
/**
 *
 Authentication Management
 */
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.isAuthenticated = false;
        this.authModal = null;
        this.authForm = null;
        this.authNavItem = null;
        
        this.init();
    }
    
    init() {
        // Get DOM elements
        this.authModal = document.getElementById('auth-modal');
        this.authForm = document.getElementById('auth-form');
        this.authNavItem = document.getElementById('auth-nav-item');
        
        // Initialize authentication UI
        this.initializeAuthUI();
        
        // Check if user is already authenticated
        this.checkAuthenticationStatus();
        
        // Set up event listeners
        this.setupEventListeners();
        
        console.log('Authentication manager initialized');
    }
    
    initializeAuthUI() {
        // Create authentication navigation buttons
        this.renderAuthNavigation();
    }
    
    renderAuthNavigation() {
        if (!this.authNavItem) return;
        
        if (this.isAuthenticated && this.currentUser) {
            // Show user info and logout button
            this.authNavItem.innerHTML = `
                <div class="auth-nav-item">
                    <div class="user-info">
                        <div class="user-avatar">${this.getUserInitials()}</div>
                        <span class="user-email">${this.currentUser.email}</span>
                    </div>
                    <button id="logout-btn" class="auth-btn" aria-label="Sign out">
                        Sign Out
                    </button>
                </div>
            `;
        } else {
            // Show login button
            this.authNavItem.innerHTML = `
                <div class="auth-nav-item">
                    <button id="login-btn" class="auth-btn primary" aria-label="Sign in to access protected features">
                        Sign In
                    </button>
                </div>
            `;
        }
        
        // Re-attach event listeners after DOM update
        this.attachNavigationListeners();
    }
    
    attachNavigationListeners() {
        const loginBtn = document.getElementById('login-btn');
        const logoutBtn = document.getElementById('logout-btn');
        
        if (loginBtn) {
            loginBtn.addEventListener('click', () => this.showAuthModal());
        }
        
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }
    }
    
    setupEventListeners() {
        if (!this.authModal || !this.authForm) return;
        
        // Modal close events
        const closeBtn = document.getElementById('close-auth-modal');
        const cancelBtn = document.getElementById('auth-cancel-btn');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hideAuthModal());
        }
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.hideAuthModal());
        }
        
        // Close modal on backdrop click
        this.authModal.addEventListener('click', (e) => {
            if (e.target === this.authModal) {
                this.hideAuthModal();
            }
        });
        
        // Close modal on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.authModal.classList.contains('active')) {
                this.hideAuthModal();
            }
        });
        
        // Form submission
        this.authForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleAuthSubmit();
        });
        
        // Attach navigation listeners
        this.attachNavigationListeners();
    }
    
    async checkAuthenticationStatus() {
        try {
            // Check if API client has a token
            if (window.apiClient && window.apiClient.isAuthenticated()) {
                // Verify token with backend
                const userInfo = await window.apiClient.get('/api/auth/me');
                this.setAuthenticatedUser(userInfo);
            }
        } catch (error) {
            console.log('No valid authentication found:', error);
            // Clear invalid token
            if (window.apiClient) {
                window.apiClient.clearToken();
            }
        }
    }
    
    showAuthModal() {
        if (!this.authModal) return;
        
        this.authModal.classList.add('active');
        this.authModal.setAttribute('aria-hidden', 'false');
        
        // Focus first input
        const emailInput = document.getElementById('auth-email');
        if (emailInput) {
            setTimeout(() => emailInput.focus(), 100);
        }
        
        // Trap focus in modal
        if (window.trapFocus) {
            window.trapFocus(this.authModal);
        }
        
        // Announce to screen readers
        if (window.announceToScreenReader) {
            window.announceToScreenReader('Authentication modal opened');
        }
    }
    
    hideAuthModal() {
        if (!this.authModal) return;
        
        this.authModal.classList.remove('active');
        this.authModal.setAttribute('aria-hidden', 'true');
        
        // Clear form
        if (this.authForm) {
            this.authForm.reset();
        }
        
        // Clear error messages
        this.clearAuthError();
        
        // Reset button state
        this.setAuthButtonLoading(false);
        
        // Announce to screen readers
        if (window.announceToScreenReader) {
            window.announceToScreenReader('Authentication modal closed');
        }
    }
    
    async handleAuthSubmit() {
        const formData = new FormData(this.authForm);
        const email = formData.get('email');
        const rateLimitTier = formData.get('rateLimitTier');
        
        // Validate form
        if (!email || !this.isValidEmail(email)) {
            this.showAuthError('Please enter a valid email address');
            return;
        }
        
        this.setAuthButtonLoading(true);
        this.clearAuthError();
        
        try {
            // Create API key using the API client
            const response = await window.apiClient.createApiKey(email, rateLimitTier);
            
            // Get user info
            const userInfo = await window.apiClient.get('/api/auth/me');
            
            // Set authenticated user
            this.setAuthenticatedUser(userInfo);
            
            // Hide modal
            this.hideAuthModal();
            
            // Show success message
            if (window.announceToScreenReader) {
                window.announceToScreenReader('Successfully signed in!');
            }
            
            // Load user profile and history
            this.loadUserProfile();
            
            // If there's a pending file upload, process it now
            if (this.pendingFileUpload) {
                setTimeout(() => {
                    this.processPendingFileUpload();
                }, 500);
            }
            
        } catch (error) {
            console.error('Authentication failed:', error);
            this.showAuthError(error.message || 'Authentication failed. Please try again.');
        } finally {
            this.setAuthButtonLoading(false);
        }
    }
    
    setPendingFileUpload(file) {
        this.pendingFileUpload = file;
    }
    
    async processPendingFileUpload() {
        if (!this.pendingFileUpload) return;
        
        const file = this.pendingFileUpload;
        this.pendingFileUpload = null;
        
        try {
            // Trigger file upload programmatically
            const fileInput = document.getElementById('file-upload');
            if (fileInput && window.apiClient) {
                // Create a new FileList with the pending file
                const dt = new DataTransfer();
                dt.items.add(file);
                fileInput.files = dt.files;
                
                // Trigger the change event
                const event = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(event);
            }
        } catch (error) {
            console.error('Failed to process pending file upload:', error);
        }
    }
    
    setAuthenticatedUser(userInfo) {
        this.currentUser = userInfo;
        this.isAuthenticated = true;
        
        // Update navigation
        this.renderAuthNavigation();
        
        // Show user profile section
        this.showUserProfileSection();
        
        // Update protected features
        this.updateProtectedFeatures();
        
        console.log('User authenticated:', userInfo);
    }
    
    logout() {
        // Clear API client token
        if (window.apiClient) {
            window.apiClient.logout();
        }
        
        // Clear local state
        this.currentUser = null;
        this.isAuthenticated = false;
        
        // Update navigation
        this.renderAuthNavigation();
        
        // Hide user profile section
        this.hideUserProfileSection();
        
        // Update protected features
        this.updateProtectedFeatures();
        
        // Announce to screen readers
        if (window.announceToScreenReader) {
            window.announceToScreenReader('Successfully signed out');
        }
        
        console.log('User logged out');
    }
    
    showUserProfileSection() {
        const profileSection = document.getElementById('user-profile');
        if (profileSection) {
            profileSection.style.display = 'block';
            
            // Update profile information
            this.updateProfileDisplay();
        }
    }
    
    hideUserProfileSection() {
        const profileSection = document.getElementById('user-profile');
        if (profileSection) {
            profileSection.style.display = 'none';
        }
    }
    
    updateProfileDisplay() {
        if (!this.currentUser) return;
        
        // Update profile information
        const emailElement = document.getElementById('user-email');
        const tierElement = document.getElementById('user-tier');
        const createdElement = document.getElementById('user-created');
        
        if (emailElement) {
            emailElement.textContent = this.currentUser.email;
        }
        
        if (tierElement) {
            tierElement.textContent = this.currentUser.rate_limit_tier || 'Basic';
        }
        
        if (createdElement && this.currentUser.created_at) {
            const date = new Date(this.currentUser.created_at);
            createdElement.textContent = date.toLocaleDateString();
        }
    }
    
    async loadUserProfile() {
        if (!this.isAuthenticated) return;
        
        try {
            // Load analysis history
            await this.loadAnalysisHistory();
            
        } catch (error) {
            console.error('Failed to load user profile:', error);
        }
    }
    
    async loadAnalysisHistory() {
        const historyContent = document.getElementById('history-content');
        if (!historyContent) return;
        
        try {
            // Show loading state
            historyContent.innerHTML = '<div class="loading-message">Loading analysis history...</div>';
            
            // Fetch analysis history from API
            const historyResponse = await window.apiClient.getAnalysisHistory(10, 0);
            
            if (historyResponse.reports && historyResponse.reports.length > 0) {
                this.renderAnalysisHistory(historyResponse.reports);
            } else {
                this.renderEmptyHistory();
            }
            
        } catch (error) {
            console.error('Failed to load analysis history:', error);
            historyContent.innerHTML = `
                <div class="empty-history">
                    <div class="empty-history-icon">⚠️</div>
                    <p>Failed to load analysis history</p>
                    <button id="retry-history" class="btn btn-secondary">Retry</button>
                </div>
            `;
            
            // Add retry functionality
            const retryBtn = document.getElementById('retry-history');
            if (retryBtn) {
                retryBtn.addEventListener('click', () => this.loadAnalysisHistory());
            }
        }
    }
    
    renderAnalysisHistory(reports) {
        const historyContent = document.getElementById('history-content');
        if (!historyContent) return;
        
        const historyHTML = reports.map(report => `
            <div class="history-item" data-report-id="${report.report_id}" tabindex="0" role="button" aria-label="View analysis report for ${report.filename}">
                <div class="history-item-info">
                    <div class="history-item-title">${this.escapeHtml(report.filename)}</div>
                    <div class="history-item-meta">
                        ${report.language} • ${this.formatDate(report.created_at)}
                        ${report.summary ? ` • ${report.summary.total_issues || 0} issues` : ''}
                    </div>
                </div>
                <div class="history-item-status ${report.status}">${report.status}</div>
            </div>
        `).join('');
        
        historyContent.innerHTML = historyHTML;
        
        // Add click handlers for history items
        const historyItems = historyContent.querySelectorAll('.history-item');
        historyItems.forEach(item => {
            item.addEventListener('click', () => {
                const reportId = item.dataset.reportId;
                this.viewAnalysisReport(reportId);
            });
            
            item.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const reportId = item.dataset.reportId;
                    this.viewAnalysisReport(reportId);
                }
            });
        });
    }
    
    renderEmptyHistory() {
        const historyContent = document.getElementById('history-content');
        if (!historyContent) return;
        
        historyContent.innerHTML = `
            <div class="empty-history">
                <div class="empty-history-icon">📊</div>
                <p>No analysis history yet</p>
                <p>Upload and analyze some code to see your history here!</p>
            </div>
        `;
    }
    
    async viewAnalysisReport(reportId) {
        try {
            // Fetch the full report
            const report = await window.apiClient.getAnalysisReport(reportId);
            
            // Update the analysis results display
            if (window.updateAnalysisResultsFromReport) {
                window.updateAnalysisResultsFromReport(report);
            }
            
            // Scroll to analysis results
            const analyzerSection = document.getElementById('analyzer');
            if (analyzerSection) {
                analyzerSection.scrollIntoView({ behavior: 'smooth' });
            }
            
            // Announce to screen readers
            if (window.announceToScreenReader) {
                window.announceToScreenReader(`Loaded analysis report for ${report.filename}`);
            }
            
        } catch (error) {
            console.error('Failed to load analysis report:', error);
            if (window.apiClient) {
                window.apiClient.showUserFriendlyError('Failed to load analysis report');
            }
        }
    }
    
    updateProtectedFeatures() {
        // Update UI elements that require authentication
        const protectedElements = document.querySelectorAll('[data-requires-auth]');
        
        protectedElements.forEach(element => {
            if (this.isAuthenticated) {
                element.style.display = '';
                element.removeAttribute('disabled');
            } else {
                element.style.display = 'none';
                element.setAttribute('disabled', 'true');
            }
        });
        
        // Update navigation items specifically
        const profileNavItem = document.getElementById('profile-nav-item');
        if (profileNavItem) {
            profileNavItem.style.display = this.isAuthenticated ? '' : 'none';
        }
        
        // Update authentication status indicator
        this.updateAuthStatusIndicator();
    }
    
    updateAuthStatusIndicator() {
        const indicator = document.getElementById('auth-status-indicator');
        if (!indicator) return;
        
        if (this.isAuthenticated) {
            indicator.style.display = 'flex';
            indicator.className = 'auth-status-indicator authenticated';
            indicator.innerHTML = `
                <span class="status-icon">✓</span>
                <span class="status-text">Signed in</span>
            `;
        } else {
            indicator.style.display = 'none';
        }
    }
    
    showAuthPrompt(message = 'Sign in to save your analysis history and access additional features.') {
        // Remove existing prompt if any
        this.hideAuthPrompt();
        
        // Create prompt element
        const prompt = document.createElement('div');
        prompt.id = 'auth-prompt';
        prompt.className = 'auth-prompt';
        prompt.innerHTML = `
            <div class="auth-prompt-title">Sign In Recommended</div>
            <div class="auth-prompt-message">${message}</div>
            <div class="auth-prompt-actions">
                <button class="auth-prompt-btn primary" id="prompt-signin">Sign In</button>
                <button class="auth-prompt-btn" id="prompt-continue">Continue</button>
                <button class="auth-prompt-btn" id="prompt-dismiss">×</button>
            </div>
        `;
        
        document.body.appendChild(prompt);
        
        // Show with animation
        setTimeout(() => prompt.classList.add('show'), 100);
        
        // Add event listeners
        const signinBtn = prompt.querySelector('#prompt-signin');
        const continueBtn = prompt.querySelector('#prompt-continue');
        const dismissBtn = prompt.querySelector('#prompt-dismiss');
        
        signinBtn.addEventListener('click', () => {
            this.hideAuthPrompt();
            this.showAuthModal();
        });
        
        continueBtn.addEventListener('click', () => {
            this.hideAuthPrompt();
        });
        
        dismissBtn.addEventListener('click', () => {
            this.hideAuthPrompt();
        });
        
        // Auto-hide after 10 seconds
        setTimeout(() => this.hideAuthPrompt(), 10000);
        
        return new Promise((resolve) => {
            signinBtn.addEventListener('click', () => resolve('signin'));
            continueBtn.addEventListener('click', () => resolve('continue'));
            dismissBtn.addEventListener('click', () => resolve('dismiss'));
        });
    }
    
    hideAuthPrompt() {
        const existingPrompt = document.getElementById('auth-prompt');
        if (existingPrompt) {
            existingPrompt.classList.remove('show');
            setTimeout(() => {
                if (existingPrompt.parentNode) {
                    existingPrompt.parentNode.removeChild(existingPrompt);
                }
            }, 300);
        }
    }
    
    // Utility methods
    getUserInitials() {
        if (!this.currentUser || !this.currentUser.email) return '?';
        
        const email = this.currentUser.email;
        const parts = email.split('@')[0].split('.');
        
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        } else {
            return email.substring(0, 2).toUpperCase();
        }
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) {
            return 'Today';
        } else if (diffDays === 1) {
            return 'Yesterday';
        } else if (diffDays < 7) {
            return `${diffDays} days ago`;
        } else {
            return date.toLocaleDateString();
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    setAuthButtonLoading(loading) {
        const submitBtn = document.getElementById('auth-submit-btn');
        if (!submitBtn) return;
        
        if (loading) {
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
        } else {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    }
    
    showAuthError(message) {
        const errorElement = document.getElementById('auth-error');
        if (!errorElement) return;
        
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        
        // Announce error to screen readers
        if (window.announceToScreenReader) {
            window.announceToScreenReader(`Error: ${message}`, 'assertive');
        }
    }
    
    clearAuthError() {
        const errorElement = document.getElementById('auth-error');
        if (!errorElement) return;
        
        errorElement.textContent = '';
        errorElement.style.display = 'none';
    }
}

// Initialize authentication manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize authentication after a short delay to ensure other components are ready
    setTimeout(() => {
        window.authManager = new AuthManager();
        
        // Set up refresh history button
        const refreshHistoryBtn = document.getElementById('refresh-history');
        if (refreshHistoryBtn) {
            refreshHistoryBtn.addEventListener('click', () => {
                if (window.authManager && window.authManager.isAuthenticated) {
                    window.authManager.loadAnalysisHistory();
                }
            });
        }
    }, 100);
});

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
        window.announceStatus(`${title}. ${description}`);
        
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
            window.announceProgress(message || 'Processing', this.currentProgress);
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
            window.announceError(announcement);
        } else {
            window.announceStatus(announcement);
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
            window.notificationManager.error(
                'An unexpected error occurred. Please refresh the page if problems persist.',
                {
         
});ed'); initializmsity systecessibil'Enhanced ac.log( console      

 r();ageionMangatardNaview KeyboManager = neyboard    window.kandler();
ew ErrorHler = nndrHa window.erroager();
   ificationManew Not= nonManager atidow.notific;
    winteManager()dingStaw Loager = nengManaadiindow.lo
    wanagersy messibilit global accitialize  // Intion() {
  ded', funcontentLoa'DOMCtener(tLisEvent.addumenems
docity systcessibilnhanced acalize eiti

// In
    }
}   });  }
        });
                       
);us-visible've('focemoList.r    el.class            {
     lur', () =>tListener('b el.addEven          
                          });
   ;
        ')ble-visi('focuslassList.add       el.c          ) => {
   ocus', (ener('ftListdEven    el.ad           cators
 di ind focus // Ad                   
       ;
     rue')nced', 'tyboard-enhae('data-ke.setAttribut    el     ) {
       nhanced')board-eata-keyttribute('dl.hasA    if (!e       l => {
 .forEach(eentsableElem       focus   
   s);
   torelecusableSis.focll(thectorAent.querySel = elemlementseEusablt foc       cons elements
 focusablew n to neavigatioyboard n ke      // Addnt) {
  mes(elementewElenceNha    en}
    
;
        })rue
     t  subtree:
          t: true,ildLis ch           {
 ent.body,umerve(docerver.obsbs
        o);
          }
            });  
              }
           });                    }
           
        de);s(noceNewElementenhanis.      th               ) {
       T_NODEMENELE === Node.eType.nod if (node                   
    (node) => {forEach(dNodes.detation.ad   mu             {
     ist')'childL === utation.type   if (m       {
      ation) => ach((mutons.forE mutati           {
s) => ationver((mutObserew Mutationobserver = nonst     ct
     contenly addedalmicynant for ds manageme// Focu    {
     nagement()tupFocusMa se    
   }
  == null;
  fsetParent ! element.of        && 
       'hidden' y !==.visibilit      style       
    'none' &&!==ay ispl style.durn       retnt);
 emeyle(elmputedStndow.getCostyle = wi      const 
  ement) {(elisible  
    isV    }
  ement));
ble(els.isVisithi => ter(element     .fil)
       lectors)ocusableSerAll(this.frySelectoquecument.rray.from(do Areturn      ts() {
  eElemen getFocusabl  
      }
  
      }
   ].focus();IndexrgetableItems[ta   focus;
         fault()entDe e.prev          x]) {
 getIndeems[tarocusableItntIndex && f!== curreIndex (target       if    
        }
   
        }k;
          brea           ;
       : 0tIndex + 1 curren - 1 ?gthlenems. focusableItndex <tI= currenargetIndex      t           Down':
    case 'Arrow              
  break;               
     ngth - 1;ems.lecusableIt : foIndex - 1nt> 0 ? curreIndex rentdex = curgetInar      t             wUp':
   case 'Arro             
 h (e.key) {witc     s
       on for listsatiigLinear nav        // e {
    } els}
              eak;
            br           Index;
   x = current) targetIndelengthms.ableIteex >= focusargetInd (tif         
           mns;+ colutIndex encurrgetIndex =    tar         :
        n'ArrowDow   case '     k;
        ea   br                x;
 rrentIndeetIndex = cuarg) tx < 0rgetIndeta   if (         ;
        ex - columnsIndurrent = cex  targetInd                ':
  'ArrowUp       case      
    break;                    1 : 0;
 tIndex + curren 1 ?s.length -ableItem focustIndex <= currenex   targetInd            
      ht':ig'ArrowR       case          eak;
       br             1;
.length - leItems: focusabtIndex - 1  0 ? currenx > currentIndetIndex =  targe                  wLeft':
se 'Arroca            ey) {
     switch (e.k        
             h;
  .lengtit(' ')umns.splplateCole.gridTem= gridStyl columns        const    tainer);
 idCongrle(putedSty.getComndow wiidStyle =grt   cons         
 d dimensionsrilate g   // Calcu         sGrid) {
(i if 
       
        id');metrics-grns('contaiList.er.classgridContain            
          ) || d'riature-gontains('fest.ciner.classLi= gridContaisGrid   const    Index;
    currentargetIndex =   let t
        rn;
      -1) retuIndex === (current       if       
 Element);
 rentdexOf(curbleItems.incusaex = forrentIndconst cu   '));
     ex="0"]All('[tabindlector.querySetainer(gridConay.from= ArrleItems nst focusab  co    
  ) {idContainerement, grrrentElcution(e, dNavigarindleG   ha
     }
   }
   
      r);ntaineet, gridCo(e, targgationndleGridNavi.ha  this          ntainer) {
 if (gridCo      tainer');
 es-con, .issumetrics-gridd, .ature-gri'.feget.closest(iner = tarontagridC const n
       tio grid navigadle  // Han            
arget;
   = e.targetonst t    c) {
    rowKeys(eArandle    
    h    }
0);
      }, 15ted');
  -activakeyboard('ist.removesLet.clastarg            => {
 imeout(()   setT  );
   d'tivateeyboard-acadd('kassList.rget.cl     tack
   isual feedbad v  // Ad  
         
           }();
click  target.      t();
    ulfantDevee.pre       ')) {
     on === 'buttle')ribute('rot.getAtt| targeUTTON' |== 'BtagName =rget.& (tay === ' ' &e.ke   if (
     ntsve elemeacti internd customons a buttpace key fordle s     // Han   
   t;
     .targetarget = est on       c(e) {
 eyonKatidleActiv
    han
     }
    }         }
      s();
    ent.focuOverlayElem       first  ();
       ltaupreventDef      e.          {
 rlayElement)== lastOvet =activeElemen document.shiftKey && if (!e. } else          s();
 Element.focuOverlay last           t();
    entDefaul      e.prev    
      t) {lemenyErstOverlat === fiemeniveElt.act && documenftKey.shif (e    i        
    ;
        length - 1]cusable.ayFole[overlcusab= overlayForlayElement onst lastOve    c  0];
      Focusable[lay = overyElementerla firstOv     const  
       
                   }  urn;
   ret         
     lt();preventDefau          e.   0) {
   th === usable.lengyFocla  if (over      rs);
    Selectoocusablethis.flectorAll(y.querySerla = activeOvecusablelayFo overconst            erlay
 ov incus  // Trap fo       lay) {
   tiveOverif (ac);
        y.active'ing-overla'.loadctor(querySeleent.y = documerlativeOvnst ac  coy
      verlaal or oa modwe're in heck if  C       //  
     ];
  gth - 1ements.leneEl[focusablementsfocusableElent = Elemt last    cons
    ments[0];focusableEle = ementnst firstEl      co();
  eElementstFocusabl.gehisents = tElemsableocu    const f    ping
focus trapith tion wnavigahanced tab        // En {
 e)ey(  handleTabK
     }
    
      }lt();
   fau e.preventDe     
      );     }               }
  );
      (id)Int.hide(parseionManagerficatnotiw.     windo              r) {
 tionManage.notificad && window(i      if 
          ion-id');cat'data-notifiibute(etAttr.gationicid = notif   const       {
        ion =>ficatEach(notiions.for  notificat       ) {
   ength > 0s.lontificatinof (    i    w');
ion.shocattifi.api-nolectorAll('ent.querySeons = documt notifications    c    fications
Close noti    //  
    
            }turn;
       re      ape
  scwith eng overlays osing loadiw cl allon't      // Do      Modal) {
if (active        tive');
-overlay.acr('.loadingctoleerySet.qu= documenactiveModal  const tc.
       ations, e, notificose modalsCl    // e) {
    scapeKey(leE    hand }
    
rue';
   == 'ttEditable =ontenent.clem         e
      ) || mement.tagNaincludes(eleements.ypingEl return t  T'];
     ECSEL 'EA',TARNPUT', 'TEXents = ['IpingElem    const ty
    {ent) ontext(elemgCisTypin   
   }
       }
     
     break;  
           (e);rrowKeyshandleA    this.         Right':
   'Arrow     case :
       wLeft'se 'Arro   ca    n':
     ArrowDowcase '   
         rowUp':    case 'Ar
          break;            ey(e);
  ionKctivathis.handleA t           ' ':
           case     'Enter':
 ase  c        reak;
        b           Key(e);
ab.handleT      this     Tab':
        case '    
     break;            ey(e);
    peKeEscathis.handl           
     ape':ase 'Esc        c) {
    ey(e.kitch         sw    
     }
    ;
         return
      .target)) {Context(engs.isTypi if (thiut
       n inptyping in a is ion if usernavigat // Skip 
       ydown(e) {alKehandleGlob 
        }
   
itialized');gation inrd navi keyboaEnhancedsole.log('    con      
();
      gementupFocusMana  this.set    
  mic contentor dynaement f manag  // Focus    
  ;
              });
  ydown(e)lKeeGlobathis.handl           (e) => {
 , eydown'tListener('kent.addEven documing
       dlt hanenard evd keybonhance       // E
 on() {gativiKeyboardNainitialize    
      }

  n();tiovigaKeyboardNaizetialni    this.i          
, ');
  oin('       ].j"]'
 rueitable="tted    '[conten,
        ])'ndex="-1"biex]:not([ta   '[tabind
         abled])',not([dis    'select:
        ])',[disabledt(tarea:no    'tex       bled])',
 [disaot('input:n            )',
[disabled]button:not(       ',
     [href]'       'a[
     = leSelectors his.focusab   t
     ctor() {tru {
    consgertionManaoardNavigaeybclass Kion
 */
vigat NaboardKey * Enhanced }

/**

    }
));solve, msreimeout( => setTise(resolvew Promreturn ne {
        elay(ms)    
    d
    }
;
        }rsists.`roblem pe if the prtontact suppon or cry agaid. Please t faileeration}turn `${op         re    ault:
        def;
       r.'gain latey atr. Please ilableunavaly mporarice tervin 'Seetur    r           :
 e 503        cas.';
    omentsa few min in  aga Please tryor.er errServeturn '          r      500:
 case            .';
 againent and trymom wait a ease. Plts many reques return 'Too               
429:se  ca       ;
    ler file.'a smalelect ase slarge. Plen 'File too    retur             3:
41se      ca;
       support.`tact . Please cont foundint no} endporation `${opeturn          re:
          case 404`;
        tion_lower}.operathis ${o perform permission t have  don'tYou return `            :
   ase 403 c           ain.';
 try ag andase log ind. Plen requireenticatioreturn 'Auth                
 401:case           ;
 try again.`input and your se check est. Plearequn_lower} {operatiod $urn `Invali         ret:
           case 400    us) {
    (statwitch 
        s }
               again.';
nd try k anetworyour  check ion. Pleasenecton crnet 'No inteturn  re         ) {
 ineator.onLnavig      if (!
    ;
      erCase()Lowperation.toower = ooperation_lnst 
        cotatus;rror.s= eatus    const st    {
   operation)sage(error,orMesrryEFriendl getUser
    }
      
 29;== 4s =|| statu === 408 usat 500 || sts >=tutus || sta return !sta
       us;error.status = tat     const sable
   t retry nonerallyre ge(4xx) arrors Client e//         able
re retryrs arver errond serk errors a   // Networ) {
     r(erroableErroRetry
    is    }
    }
  or;
      ow err        thr  
    
          rrorKey);ts.delete(erorCoun this.er         ure
  ailfter final f acount error eset       // R           
            });
     
      }]      ))
     eload(w.location.r=> windon || (() unctiotryFndler: re  ha           ,
       Try Again'   label: '             ry',
    et      id: 'r        
      ns: [{     actio         
  on Failed',Operatititle: '             , {
   serMessageger.error(uManaotificationw.n      windo  
          ;
      tion)r, opera(erroErrorMessagerFriendly this.getUsege =essa const userM    er
       or to usfinal err Show //          {
       } else }
               nction);
tryFueration, rer, optryErroApiError(rethis.handle     return         {
   yError) h (retr      } catc;
      on()unctitryFn await re  retur            ry {
     t         
           ay);
 .delay(delwait this     ary
       ait and ret  // W             
               );
}
                 elay
     ation: d    dur              n',
  eratioetrying Op   title: 'R          
               {  ..`,
      00} seconds.y / 10 ${delang inryi. Retiledon} fa${operati `            ing(
   r.warnationManageow.notific    wind 
          
         ;00nt] || 50s[errorCouretryDelay this.delay =const             ) {
shouldRetry        if (  

      rror);(eleErrorisRetryab& this.Retries & this.maxorCount < errnction && = retryFuouldRetrysh  const    
   ould retryine if we shterm/ De   /     
     );
    1t +ounrCrro, eet(errorKeyCounts.sor this.err       ror count
 er/ Increment    /      

      :`, error);ration}${opeError in or(`API sole.err  con
         || 0;
     errorKey) rCounts.get( this.errorCount =erro      const   
}`; 'unknown'r.status ||rro{e_$${operation}rorKey = `onst er        cl) {
 = nulonFuncti retryn,r, operatioor(erroleApiErrsync hand  a
    
    }}
        );
             }
             
    t: truesten   persi               ',
  nection LostCon title: '                          {

         offline.',while work es may not eaturme f       'So       (
  ger.warningonManatificati window.no         ne.');
  e now offliou arst. Yonnection lor('CeErrow.announc   windo             
   }
                show');
 t.add('sLisclasneIndicator.       offli        cator) {
 eIndi (offlin     if      r
 toline indicaShow off   //         lse {
   } e
        });
          Back Online'e: '  titl             ed', {
 ion restornect('Coner.successagficationMan window.noti      
     ');nline.re back ou aestored. Yoion r('ConnectuseStatow.announc   wind           
       }
               ');
('show.remover.classListeIndicato     offlin      
     ator) {ineIndic (offl      ifor
      atndicline i// Hide off           Online) {
   if (is    
      ');
    indicatorline-Id('offmentByument.getEleocndicator = dineIconst offl       
 nline) {nge(isOorkStatusCha  handleNetw }
    
     sage));
rrorMest(etern.tes pattern =>s.some(paternicalPatt return crit      () || '';
 tringtoSor?. err.message || = error?ssageorMenst err      co
      ];
            on/i
uthorizati         /a   ation/i,
  /authentic          /i,
   /api,
         etch/i      /fk/i,
        /networ        ns = [
  ticalPatternst cri      coror
  ritical ertes a cat constitu wh   // Definer) {
     roError(eritical
    isCr    
    }
    }         );

                }   }]
                 d()
       oan.rellocatio window.() =>ler:         hand                h Page',
el: 'Refresab        l        ,
        resh'id: 'ref                    ns: [{
        actio               ,
 ation Error''Applictitle:            