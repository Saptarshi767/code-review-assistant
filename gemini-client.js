/**
 * Direct Gemini API Client
 * Handles code review using Google Gemini API directly from the frontend
 */

class GeminiClient {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseURL = 'https://generativelanguage.googleapis.com/v1beta/models';
        this.model = 'gemini-2.0-flash-exp';
        
        console.log('Gemini Client initialized');
    }

    /**
     * Analyze code using Gemini API
     */
    async analyzeCode(code, filename = 'code.txt') {
        if (!this.apiKey) {
            throw new Error('Gemini API key is required');
        }

        const fileExtension = filename.split('.').pop().toLowerCase();
        const language = this.detectLanguage(fileExtension);

        const prompt = this.createCodeReviewPrompt(code, language, filename);

        try {
            const response = await fetch(`${this.baseURL}/${this.model}:generateContent?key=${this.apiKey}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    contents: [{
                        parts: [{
                            text: prompt
                        }]
                    }],
                    generationConfig: {
                        temperature: 0.1,
                        topK: 40,
                        topP: 0.95,
                        maxOutputTokens: 4000,
                    }
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Gemini API error: ${errorData.error?.message || response.statusText}`);
            }

            const data = await response.json();
            const analysisText = data.candidates?.[0]?.content?.parts?.[0]?.text;

            if (!analysisText) {
                throw new Error('No analysis received from Gemini API');
            }

            return this.parseAnalysisResponse(analysisText, filename);

        } catch (error) {
            console.error('Gemini API error:', error);
            throw error;
        }
    }

    /**
     * Create a comprehensive code review prompt
     */
    createCodeReviewPrompt(code, language, filename) {
        return `Please perform a comprehensive code review of the following ${language} code from file "${filename}".

Analyze the code for:
1. **Code Quality**: Readability, maintainability, and best practices
2. **Security Issues**: Potential vulnerabilities and security concerns
3. **Performance**: Optimization opportunities and performance issues
4. **Bugs**: Logic errors, potential runtime errors, and edge cases
5. **Style**: Coding standards and consistency
6. **Architecture**: Design patterns and code organization

Please provide your response in the following JSON format:
\`\`\`json
{
  "summary": {
    "total_issues": 0,
    "high_severity_issues": 0,
    "medium_severity_issues": 0,
    "low_severity_issues": 0,
    "overall_quality_score": 85,
    "security_score": 90,
    "performance_score": 80
  },
  "issues": [
    {
      "type": "security|performance|bug|style|quality",
      "severity": "high|medium|low",
      "line": 15,
      "message": "Brief description of the issue",
      "suggestion": "Detailed suggestion for fixing the issue",
      "confidence": 0.9
    }
  ],
  "recommendations": [
    "General recommendations for improving the code"
  ],
  "positive_aspects": [
    "Things that are done well in the code"
  ]
}
\`\`\`

Code to review:
\`\`\`${language}
${code}
\`\`\`

Please ensure your response is valid JSON and includes specific line numbers where issues are found.`;
    }

    /**
     * Parse the analysis response from Gemini
     */
    parseAnalysisResponse(analysisText, filename) {
        try {
            // Extract JSON from the response (handle markdown code blocks)
            const jsonMatch = analysisText.match(/```json\s*([\s\S]*?)\s*```/);
            let jsonText = jsonMatch ? jsonMatch[1] : analysisText;
            
            // Clean up the JSON text
            jsonText = jsonText.trim();
            
            const analysis = JSON.parse(jsonText);
            
            // Ensure the response has the expected structure
            const report = {
                id: this.generateReportId(),
                filename: filename,
                status: 'completed',
                timestamp: new Date().toISOString(),
                report_summary: analysis.summary || {
                    total_issues: 0,
                    high_severity_issues: 0,
                    medium_severity_issues: 0,
                    low_severity_issues: 0,
                    overall_quality_score: 85,
                    security_score: 90,
                    performance_score: 80
                },
                issues: analysis.issues || [],
                recommendations: analysis.recommendations || [],
                positive_aspects: analysis.positive_aspects || []
            };

            // Validate and fix issue counts
            this.validateIssueCounts(report);

            return report;

        } catch (error) {
            console.error('Failed to parse analysis response:', error);
            
            // Return a fallback response
            return {
                id: this.generateReportId(),
                filename: filename,
                status: 'completed',
                timestamp: new Date().toISOString(),
                report_summary: {
                    total_issues: 0,
                    high_severity_issues: 0,
                    medium_severity_issues: 0,
                    low_severity_issues: 0,
                    overall_quality_score: 75,
                    security_score: 80,
                    performance_score: 75
                },
                issues: [{
                    type: 'quality',
                    severity: 'low',
                    line: 1,
                    message: 'Analysis completed but response format was unexpected',
                    suggestion: 'The code was analyzed but the detailed results could not be parsed properly.',
                    confidence: 0.5
                }],
                recommendations: ['Consider running the analysis again for detailed results'],
                positive_aspects: ['Code was successfully processed']
            };
        }
    }

    /**
     * Validate and fix issue counts in the report
     */
    validateIssueCounts(report) {
        const issues = report.issues || [];
        const severityCounts = {
            high: 0,
            medium: 0,
            low: 0
        };

        issues.forEach(issue => {
            const severity = issue.severity?.toLowerCase();
            if (severityCounts.hasOwnProperty(severity)) {
                severityCounts[severity]++;
            }
        });

        // Update summary with actual counts
        report.report_summary.total_issues = issues.length;
        report.report_summary.high_severity_issues = severityCounts.high;
        report.report_summary.medium_severity_issues = severityCounts.medium;
        report.report_summary.low_severity_issues = severityCounts.low;
    }

    /**
     * Detect programming language from file extension
     */
    detectLanguage(extension) {
        const languageMap = {
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'py': 'Python',
            'java': 'Java',
            'cpp': 'C++',
            'c': 'C',
            'cs': 'C#',
            'php': 'PHP',
            'rb': 'Ruby',
            'go': 'Go',
            'rs': 'Rust',
            'swift': 'Swift',
            'kt': 'Kotlin',
            'scala': 'Scala',
            'html': 'HTML',
            'css': 'CSS',
            'sql': 'SQL',
            'sh': 'Shell',
            'bash': 'Bash',
            'ps1': 'PowerShell'
        };

        return languageMap[extension] || 'Unknown';
    }

    /**
     * Generate a unique report ID
     */
    generateReportId() {
        return 'report_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Analyze file content (for file uploads)
     */
    async analyzeFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = async (e) => {
                try {
                    const code = e.target.result;
                    const report = await this.analyzeCode(code, file.name);
                    resolve(report);
                } catch (error) {
                    reject(error);
                }
            };
            
            reader.onerror = () => {
                reject(new Error('Failed to read file'));
            };
            
            reader.readAsText(file);
        });
    }

    /**
     * Check if API key is valid
     */
    async validateApiKey() {
        try {
            const testResponse = await fetch(`${this.baseURL}/${this.model}:generateContent?key=${this.apiKey}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    contents: [{
                        parts: [{
                            text: 'Hello, this is a test.'
                        }]
                    }]
                })
            });

            return testResponse.ok;
        } catch (error) {
            console.error('API key validation failed:', error);
            return false;
        }
    }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.GeminiClient = GeminiClient;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = GeminiClient;
}