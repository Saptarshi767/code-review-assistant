/**
 * Code Review Assistant Dashboard JavaScript
 * Handles file uploads, report management, and interactive UI
 */

class CodeReviewDashboard {
    constructor() {
        this.apiKey = null;
        this.currentReports = [];
        this.currentReport = null;
        this.uploadInProgress = false;
        
        this.initializeElements();
        this.bindEvents();
        this.initializeTabs();
        
        // Initialize API key and load reports
        this.initialize();
    }
    
    async initialize() {
        this.apiKey = await this.getApiKey();
        this.loadReports();
    }

    initializeElements() {
        // Upload elements
        this.fileDropZone = document.getElementById('fileDropZone');
        this.fileInput = document.getElementById('fileInput');
        this.progressContainer = document.getElementById('progressContainer');
        this.progressBar = document.getElementById('progressBar');
        this.progressText = document.getElementById('progressText');
        this.statusMessage = document.getElementById('statusMessage');
        this.asyncProcessing = document.getElementById('asyncProcessing');
        this.languageSelect = document.getElementById('languageSelect');
        
        // Reports elements
        this.reportsGrid = document.getElementById('reportsGrid');
        this.reportsLoading = document.getElementById('reportsLoading');
        this.noReports = document.getElementById('noReports');
        this.statusFilter = document.getElementById('statusFilter');
        this.languageFilter = document.getElementById('languageFilter');
        this.refreshReports = document.getElementById('refreshReports');
        
        // Report detail elements
        this.reportDetail = document.getElementById('reportDetail');
        this.reportDetailTitle = document.getElementById('reportDetailTitle');
        this.reportDetailMeta = document.getElementById('reportDetailMeta');
        this.reportDetailContent = document.getElementById('reportDetailContent');
        this.backToReports = document.getElementById('backToReports');
        
        // Loading overlay
        this.loadingOverlay = document.getElementById('loadingOverlay');
    }

    bindEvents() {
        // File upload events
        this.fileDropZone.addEventListener('click', () => this.fileInput.click());
        this.fileDropZone.addEventListener('dragover', this.handleDragOver.bind(this));
        this.fileDropZone.addEventListener('dragleave', this.handleDragLeave.bind(this));
        this.fileDropZone.addEventListener('drop', this.handleDrop.bind(this));
        this.fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        
        // Tab navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
        });
        
        // Reports events
        this.refreshReports.addEventListener('click', () => this.loadReports());
        this.statusFilter.addEventListener('change', () => this.filterReports());
        this.languageFilter.addEventListener('change', () => this.filterReports());
        
        // Report detail events
        this.backToReports.addEventListener('click', () => this.showReportsView());
    }

    initializeTabs() {
        // Set up initial tab state
        this.switchTab('upload');
    }

    async getApiKey() {
        // Get API key from backend configuration
        try {
            const response = await fetch('/api/config');
            if (response.ok) {
                const config = await response.json();
                return config.gemini_api_key || 'demo-key-12345';
            }
        } catch (error) {
            console.error('Failed to fetch API key from backend:', error);
        }
        
        // Fallback to demo key if backend is not available
        return 'demo-key-12345';
    }

    // Tab Management
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}Tab`);
        });
        
        // Hide report detail view when switching tabs
        this.reportDetail.classList.remove('active');
        
        // Load reports when switching to reports tab
        if (tabName === 'reports') {
            this.loadReports();
        }
    }

    // File Upload Handling
    handleDragOver(e) {
        e.preventDefault();
        this.fileDropZone.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.fileDropZone.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.fileDropZone.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        this.processFiles(files);
    }

    handleFileSelect(e) {
        const files = Array.from(e.target.files);
        this.processFiles(files);
    }

    async processFiles(files) {
        if (this.uploadInProgress) {
            this.showStatus('Upload already in progress', 'error');
            return;
        }

        if (files.length === 0) {
            return;
        }

        // Validate files
        const validFiles = files.filter(file => this.validateFile(file));
        if (validFiles.length === 0) {
            this.showStatus('No valid files selected', 'error');
            return;
        }

        // Process first valid file (for MVP, handle one file at a time)
        const file = validFiles[0];
        await this.uploadFile(file);
    }

    validateFile(file) {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedExtensions = ['.py', '.js', '.java', '.ts', '.go', '.cpp', '.c', '.rb', '.php', '.zip'];
        
        if (file.size > maxSize) {
            this.showStatus(`File ${file.name} is too large (max 10MB)`, 'error');
            return false;
        }

        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedExtensions.includes(extension)) {
            this.showStatus(`File type ${extension} not supported`, 'error');
            return false;
        }

        return true;
    }

    async uploadFile(file) {
        if (!this.apiKey) {
            this.showStatus('API key not available. Please refresh the page.', 'error');
            return;
        }

        this.uploadInProgress = true;
        this.fileDropZone.classList.add('processing');
        this.showProgress(0, 'Preparing upload...');

        try {
            const formData = new FormData();
            formData.append('file', file);
            
            if (this.languageSelect.value) {
                formData.append('language', this.languageSelect.value);
            }
            
            if (this.asyncProcessing.checked) {
                formData.append('async_processing', 'true');
            }

            const response = await fetch('/api/review', {
                method: 'POST',
                headers: {
                    'X-API-Key': this.apiKey
                },
                body: formData
            });

            if (!response.ok) {
                let errorMessage = `HTTP ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail?.message || errorMessage;
                } catch (e) {
                    // If we can't parse error response, use status code
                }
                throw new Error(errorMessage);
            }

            const result = await response.json();
            this.showProgress(100, 'Upload complete!');
            
            setTimeout(() => {
                this.hideProgress();
                this.showStatus(`File uploaded successfully! Report ID: ${result.report_id}`, 'success');
                
                // If processing is complete, show the report
                if (result.status === 'completed') {
                    setTimeout(() => {
                        this.viewReport(result.report_id);
                    }, 2000);
                } else {
                    // Start polling for completion
                    this.pollReportStatus(result.report_id);
                }
                
                // Refresh reports list
                this.loadReports();
            }, 1000);

        } catch (error) {
            console.error('Upload error:', error);
            this.hideProgress();
            this.showStatus(`Upload failed: ${error.message}`, 'error');
        } finally {
            this.uploadInProgress = false;
            this.fileDropZone.classList.remove('processing');
            this.fileInput.value = ''; // Reset file input
        }
    }

    async pollReportStatus(reportId, maxAttempts = 30) {
        let attempts = 0;
        
        const poll = async () => {
            try {
                const response = await fetch(`/api/review/${reportId}`, {
                    headers: {
                        'X-API-Key': this.apiKey
                    }
                });

                if (response.ok) {
                    const report = await response.json();
                    
                    if (report.status === 'completed') {
                        this.showStatus('Analysis complete! Click to view report.', 'success');
                        this.loadReports(); // Refresh reports list
                        return;
                    } else if (report.status === 'failed') {
                        this.showStatus('Analysis failed. Please try again.', 'error');
                        return;
                    }
                }

                attempts++;
                if (attempts < maxAttempts) {
                    setTimeout(poll, 2000); // Poll every 2 seconds
                } else {
                    this.showStatus('Analysis is taking longer than expected. Check reports tab.', 'info');
                }
            } catch (error) {
                console.error('Polling error:', error);
            }
        };

        poll();
    }

    // Progress and Status Management
    showProgress(percent, text) {
        this.progressContainer.style.display = 'block';
        this.progressBar.style.width = `${percent}%`;
        this.progressText.textContent = text;
    }

    hideProgress() {
        this.progressContainer.style.display = 'none';
        this.progressBar.style.width = '0%';
    }

    showStatus(message, type) {
        this.statusMessage.textContent = message;
        this.statusMessage.className = `status-message status-${type}`;
        this.statusMessage.style.display = 'block';
        
        // Auto-hide success messages
        if (type === 'success') {
            setTimeout(() => {
                this.statusMessage.style.display = 'none';
            }, 5000);
        }
    }

    // Reports Management
    async loadReports() {
        if (!this.apiKey) {
            return; // Skip loading if API key not ready yet
        }

        this.showReportsLoading(true);
        
        try {
            const response = await fetch('/api/reviews?limit=50', {
                headers: {
                    'X-API-Key': this.apiKey
                }
            });

            if (!response.ok) {
                // If reports endpoint fails, just show empty state instead of error
                console.warn(`Reports endpoint returned ${response.status}, showing empty state`);
                this.currentReports = [];
                this.renderReports();
                return;
            }

            const data = await response.json();
            this.currentReports = data.reports || [];
            this.renderReports();
            
        } catch (error) {
            console.warn('Error loading reports, showing empty state:', error);
            // Show empty state instead of error to avoid breaking the UI
            this.currentReports = [];
            this.renderReports();
        } finally {
            this.showReportsLoading(false);
        }
    }

    filterReports() {
        const statusFilter = this.statusFilter.value;
        const languageFilter = this.languageFilter.value;
        
        let filteredReports = this.currentReports;
        
        if (statusFilter) {
            filteredReports = filteredReports.filter(report => report.status === statusFilter);
        }
        
        if (languageFilter) {
            filteredReports = filteredReports.filter(report => report.language === languageFilter);
        }
        
        this.renderReports(filteredReports);
    }

    renderReports(reports = this.currentReports) {
        if (reports.length === 0) {
            this.reportsGrid.style.display = 'none';
            this.noReports.style.display = 'block';
            return;
        }

        this.reportsGrid.style.display = 'grid';
        this.noReports.style.display = 'none';
        
        this.reportsGrid.innerHTML = reports.map(report => this.createReportCard(report)).join('');
        
        // Bind click events for report cards
        this.reportsGrid.querySelectorAll('.report-card').forEach(card => {
            const reportId = card.dataset.reportId;
            card.addEventListener('click', () => this.viewReport(reportId));
        });
        
        // Bind delete buttons
        this.reportsGrid.querySelectorAll('.delete-report').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.deleteReport(btn.dataset.reportId);
            });
        });
    }

    createReportCard(report) {
        const createdAt = new Date(report.created_at).toLocaleString();
        const statusClass = `status-${report.status}`;
        
        return `
            <div class="report-card" data-report-id="${report.report_id}">
                <div class="report-header">
                    <h3 class="report-title">${this.escapeHtml(report.filename)}</h3>
                    <span class="report-status ${statusClass}">${report.status}</span>
                </div>
                <div class="report-meta">
                    <div><strong>Language:</strong> ${report.language || 'Unknown'}</div>
                    <div><strong>Created:</strong> ${createdAt}</div>
                    <div><strong>Size:</strong> ${this.formatFileSize(report.file_size)}</div>
                </div>
                ${report.summary ? `<div class="report-summary">${this.escapeHtml(report.summary)}</div>` : ''}
                <div class="report-actions">
                    <button class="btn btn-primary btn-sm">View Report</button>
                    <button class="btn btn-secondary btn-sm delete-report" data-report-id="${report.report_id}">Delete</button>
                </div>
            </div>
        `;
    }

    showReportsLoading(show) {
        this.reportsLoading.style.display = show ? 'block' : 'none';
    }

    showReportsError(message) {
        this.reportsGrid.innerHTML = `
            <div class="text-center">
                <p style="color: var(--danger-color);">${message}</p>
                <button class="btn btn-primary" onclick="dashboard.loadReports()">Retry</button>
            </div>
        `;
    }

    // Report Detail View
    async viewReport(reportId) {
        this.showLoading(true);
        
        try {
            const response = await fetch(`/api/review/${reportId}`, {
                headers: {
                    'X-API-Key': this.apiKey
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const report = await response.json();
            this.currentReport = report;
            this.renderReportDetail(report);
            this.showReportDetail();
            
        } catch (error) {
            console.error('Error loading report:', error);
            this.showStatus(`Failed to load report: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    renderReportDetail(report) {
        this.reportDetailTitle.textContent = report.filename;
        
        const createdAt = new Date(report.created_at).toLocaleString();
        const completedAt = report.completed_at ? new Date(report.completed_at).toLocaleString() : 'N/A';
        
        this.reportDetailMeta.innerHTML = `
            <div><strong>Status:</strong> <span class="report-status status-${report.status}">${report.status}</span></div>
            <div><strong>Language:</strong> ${report.language || 'Unknown'}</div>
            <div><strong>Created:</strong> ${createdAt}</div>
            <div><strong>Completed:</strong> ${completedAt}</div>
            <div><strong>Processing Time:</strong> ${report.processing_time_ms ? `${report.processing_time_ms}ms` : 'N/A'}</div>
        `;

        if (report.status === 'completed') {
            this.reportDetailContent.innerHTML = this.renderAnalysisResults(report);
        } else if (report.status === 'processing') {
            this.reportDetailContent.innerHTML = `
                <div class="text-center">
                    <div class="loading"></div>
                    <p>Analysis in progress...</p>
                </div>
            `;
        } else if (report.status === 'failed') {
            this.reportDetailContent.innerHTML = `
                <div class="text-center">
                    <p style="color: var(--danger-color);">Analysis failed</p>
                </div>
            `;
        }
    }

    renderAnalysisResults(report) {
        const issues = report.issues || [];
        const recommendations = report.recommendations || [];
        
        let html = '';
        
        // Summary
        if (report.summary) {
            html += `
                <div class="section">
                    <h3 class="section-title">Summary</h3>
                    <p>${this.escapeHtml(report.summary)}</p>
                </div>
            `;
        }
        
        // Issues
        if (issues.length > 0) {
            html += `
                <div class="issues-section">
                    <h3 class="section-title">Issues Found (${issues.length})</h3>
                    <div class="issues-filters">
                        <button class="filter-btn active" data-filter="all">All</button>
                        <button class="filter-btn" data-filter="high">High</button>
                        <button class="filter-btn" data-filter="medium">Medium</button>
                        <button class="filter-btn" data-filter="low">Low</button>
                    </div>
                    <div class="issues-list">
                        ${issues.map(issue => this.renderIssue(issue)).join('')}
                    </div>
                </div>
            `;
        }
        
        // Recommendations
        if (recommendations.length > 0) {
            html += `
                <div class="section">
                    <h3 class="section-title">Recommendations (${recommendations.length})</h3>
                    <div class="recommendations-grid">
                        ${recommendations.map(rec => this.renderRecommendation(rec)).join('')}
                    </div>
                </div>
            `;
        }
        
        if (issues.length === 0 && recommendations.length === 0) {
            html = `
                <div class="text-center">
                    <h3>🎉 Great job!</h3>
                    <p>No issues found in your code. Keep up the good work!</p>
                </div>
            `;
        }
        
        return html;
    }

    renderIssue(issue) {
        return `
            <div class="issue-item severity-${issue.severity}" data-severity="${issue.severity}">
                <div class="issue-header">
                    <span class="issue-type">${this.escapeHtml(issue.type)}</span>
                    <span class="issue-severity severity-${issue.severity}">${issue.severity}</span>
                </div>
                <div class="issue-line">Line ${issue.line}</div>
                <div class="issue-message">${this.escapeHtml(issue.message)}</div>
                ${issue.suggestion ? `<div class="issue-suggestion"><strong>Suggestion:</strong> ${this.escapeHtml(issue.suggestion)}</div>` : ''}
                ${issue.code_snippet ? `<div class="code-snippet">${this.escapeHtml(issue.code_snippet)}</div>` : ''}
            </div>
        `;
    }

    renderRecommendation(rec) {
        return `
            <div class="recommendation-item">
                <div class="recommendation-header">
                    <span class="recommendation-area">${rec.area}</span>
                    <div class="impact-effort">
                        <span class="impact-badge impact-${rec.impact}">Impact: ${rec.impact}</span>
                        <span class="effort-badge effort-${rec.effort}">Effort: ${rec.effort}</span>
                    </div>
                </div>
                <div class="recommendation-message">${this.escapeHtml(rec.message)}</div>
            </div>
        `;
    }

    showReportDetail() {
        // Hide other views
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Show report detail
        this.reportDetail.classList.add('active');
        
        // Bind issue filter events
        this.reportDetail.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => this.filterIssues(btn.dataset.filter));
        });
    }

    showReportsView() {
        this.reportDetail.classList.remove('active');
        this.switchTab('reports');
    }

    filterIssues(severity) {
        // Update filter buttons
        this.reportDetail.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === severity);
        });
        
        // Filter issues
        const issues = this.reportDetail.querySelectorAll('.issue-item');
        issues.forEach(issue => {
            if (severity === 'all' || issue.dataset.severity === severity) {
                issue.style.display = 'block';
            } else {
                issue.style.display = 'none';
            }
        });
    }

    async deleteReport(reportId) {
        if (!confirm('Are you sure you want to delete this report?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/review/${reportId}`, {
                method: 'DELETE',
                headers: {
                    'X-API-Key': this.apiKey
                }
            });

            if (response.ok) {
                this.showStatus('Report deleted successfully', 'success');
                this.loadReports();
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('Delete error:', error);
            this.showStatus(`Failed to delete report: ${error.message}`, 'error');
        }
    }

    // Utility Methods
    showLoading(show) {
        this.loadingOverlay.style.display = show ? 'flex' : 'none';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new CodeReviewDashboard();
});