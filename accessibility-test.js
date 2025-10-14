// Accessibility Testing Script for AI Code Reviewer Landing Page
// Run this in the browser console to check accessibility compliance

(function() {
    'use strict';
    
    console.log('🔍 Running Accessibility Tests...\n');
    
    const results = {
        passed: 0,
        failed: 0,
        warnings: 0,
        issues: []
    };
    
    function addResult(type, test, message, element = null) {
        results[type]++;
        results.issues.push({
            type,
            test,
            message,
            element: element ? element.tagName + (element.id ? '#' + element.id : '') + (element.className ? '.' + element.className.split(' ')[0] : '') : null
        });
    }
    
    // Test 1: Check for skip links
    console.log('1. Testing skip links...');
    const skipLinks = document.querySelectorAll('.skip-link');
    if (skipLinks.length > 0) {
        addResult('passed', 'Skip Links', `Found ${skipLinks.length} skip links`);
        
        // Check if skip links are properly hidden and focusable
        skipLinks.forEach(link => {
            const styles = window.getComputedStyle(link);
            if (styles.position === 'absolute' && styles.top.includes('-')) {
                addResult('passed', 'Skip Link Positioning', 'Skip link properly positioned off-screen');
            } else {
                addResult('failed', 'Skip Link Positioning', 'Skip link not properly hidden', link);
            }
        });
    } else {
        addResult('failed', 'Skip Links', 'No skip links found');
    }
    
    // Test 2: Check heading hierarchy
    console.log('2. Testing heading hierarchy...');
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    let previousLevel = 0;
    let hierarchyValid = true;
    
    headings.forEach(heading => {
        const level = parseInt(heading.tagName.charAt(1));
        if (level > previousLevel + 1) {
            hierarchyValid = false;
            addResult('failed', 'Heading Hierarchy', `Heading level ${level} follows level ${previousLevel}`, heading);
        }
        previousLevel = level;
    });
    
    if (hierarchyValid) {
        addResult('passed', 'Heading Hierarchy', 'Heading hierarchy is valid');
    }
    
    // Test 3: Check for alt text on images
    console.log('3. Testing image alt text...');
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        if (!img.hasAttribute('alt')) {
            addResult('failed', 'Image Alt Text', 'Image missing alt attribute', img);
        } else if (img.alt.trim() === '') {
            addResult('warnings', 'Image Alt Text', 'Image has empty alt text (decorative?)', img);
        } else {
            addResult('passed', 'Image Alt Text', 'Image has alt text');
        }
    });
    
    // Test 4: Check for ARIA labels and roles
    console.log('4. Testing ARIA attributes...');
    const ariaElements = document.querySelectorAll('[aria-label], [aria-labelledby], [aria-describedby], [role]');
    if (ariaElements.length > 0) {
        addResult('passed', 'ARIA Attributes', `Found ${ariaElements.length} elements with ARIA attributes`);
    } else {
        addResult('warnings', 'ARIA Attributes', 'No ARIA attributes found');
    }
    
    // Test 5: Check for keyboard accessibility
    console.log('5. Testing keyboard accessibility...');
    const interactiveElements = document.querySelectorAll('a, button, input, textarea, select, [tabindex]');
    let keyboardAccessible = 0;
    
    interactiveElements.forEach(element => {
        const tabIndex = element.getAttribute('tabindex');
        if (tabIndex !== '-1') {
            keyboardAccessible++;
        }
    });
    
    if (keyboardAccessible === interactiveElements.length) {
        addResult('passed', 'Keyboard Accessibility', 'All interactive elements are keyboard accessible');
    } else {
        addResult('failed', 'Keyboard Accessibility', `${interactiveElements.length - keyboardAccessible} elements not keyboard accessible`);
    }
    
    // Test 6: Check for focus indicators
    console.log('6. Testing focus indicators...');
    const focusStyles = Array.from(document.styleSheets).some(sheet => {
        try {
            return Array.from(sheet.cssRules).some(rule => 
                rule.selectorText && rule.selectorText.includes(':focus')
            );
        } catch (e) {
            return false;
        }
    });
    
    if (focusStyles) {
        addResult('passed', 'Focus Indicators', 'Focus styles found in CSS');
    } else {
        addResult('warnings', 'Focus Indicators', 'No focus styles detected in CSS');
    }
    
    // Test 7: Check for semantic HTML
    console.log('7. Testing semantic HTML...');
    const semanticElements = document.querySelectorAll('main, nav, header, footer, section, article, aside');
    if (semanticElements.length > 0) {
        addResult('passed', 'Semantic HTML', `Found ${semanticElements.length} semantic elements`);
    } else {
        addResult('warnings', 'Semantic HTML', 'Limited semantic HTML elements found');
    }
    
    // Test 8: Check for lang attribute
    console.log('8. Testing language attribute...');
    const htmlElement = document.documentElement;
    if (htmlElement.hasAttribute('lang')) {
        addResult('passed', 'Language Attribute', `Page language set to: ${htmlElement.lang}`);
    } else {
        addResult('failed', 'Language Attribute', 'No lang attribute on html element');
    }
    
    // Test 9: Check for form labels (if any forms exist)
    console.log('9. Testing form labels...');
    const formInputs = document.querySelectorAll('input, textarea, select');
    if (formInputs.length > 0) {
        formInputs.forEach(input => {
            const hasLabel = document.querySelector(`label[for="${input.id}"]`) || 
                           input.hasAttribute('aria-label') || 
                           input.hasAttribute('aria-labelledby');
            
            if (hasLabel) {
                addResult('passed', 'Form Labels', 'Form input has associated label');
            } else {
                addResult('failed', 'Form Labels', 'Form input missing label', input);
            }
        });
    } else {
        addResult('passed', 'Form Labels', 'No form inputs found');
    }
    
    // Test 10: Check for color contrast (basic check)
    console.log('10. Testing color contrast...');
    if (window.validateColorContrast) {
        const contrastIssues = window.validateColorContrast();
        if (contrastIssues.length === 0) {
            addResult('passed', 'Color Contrast', 'No obvious contrast issues detected');
        } else {
            addResult('warnings', 'Color Contrast', `${contrastIssues.length} potential contrast issues found`);
        }
    } else {
        addResult('warnings', 'Color Contrast', 'Color contrast validation not available');
    }
    
    // Display results
    console.log('\n📊 Accessibility Test Results:');
    console.log(`✅ Passed: ${results.passed}`);
    console.log(`⚠️  Warnings: ${results.warnings}`);
    console.log(`❌ Failed: ${results.failed}`);
    
    if (results.issues.length > 0) {
        console.log('\n📋 Detailed Results:');
        results.issues.forEach(issue => {
            const icon = issue.type === 'passed' ? '✅' : issue.type === 'warnings' ? '⚠️' : '❌';
            console.log(`${icon} ${issue.test}: ${issue.message}${issue.element ? ` (${issue.element})` : ''}`);
        });
    }
    
    // Calculate score
    const totalTests = results.passed + results.failed + results.warnings;
    const score = Math.round((results.passed / totalTests) * 100);
    
    console.log(`\n🎯 Accessibility Score: ${score}%`);
    
    if (score >= 90) {
        console.log('🎉 Excellent accessibility implementation!');
    } else if (score >= 75) {
        console.log('👍 Good accessibility, but room for improvement');
    } else {
        console.log('⚠️  Accessibility needs significant improvement');
    }
    
    return results;
})();