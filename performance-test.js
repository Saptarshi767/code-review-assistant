// Performance Testing Script for AI Code Reviewer Landing Page
// Run this in the browser console to check performance metrics

(function() {
    'use strict';
    
    console.log('⚡ Running Performance Tests...\n');
    
    const results = {
        metrics: {},
        recommendations: [],
        score: 0
    };
    
    // Test 1: Check Core Web Vitals
    console.log('1. Checking Core Web Vitals...');
    
    // Largest Contentful Paint (LCP)
    if ('PerformanceObserver' in window) {
        try {
            const lcpObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                results.metrics.lcp = Math.round(lastEntry.startTime);
                
                if (results.metrics.lcp <= 2500) {
                    console.log(`✅ LCP: ${results.metrics.lcp}ms (Good)`);
                } else if (results.metrics.lcp <= 4000) {
                    console.log(`⚠️ LCP: ${results.metrics.lcp}ms (Needs Improvement)`);
                    results.recommendations.push('Optimize LCP by reducing server response time and optimizing images');
                } else {
                    console.log(`❌ LCP: ${results.metrics.lcp}ms (Poor)`);
                    results.recommendations.push('LCP is too slow - critical performance issue');
                }
            });
            
            lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        } catch (error) {
            console.warn('Could not measure LCP:', error);
        }
    }
    
    // Test 2: Check resource loading
    console.log('2. Analyzing resource loading...');
    
    if ('performance' in window && 'getEntriesByType' in performance) {
        const resources = performance.getEntriesByType('resource');
        const totalResources = resources.length;
        let slowResources = 0;
        let totalSize = 0;
        
        resources.forEach(resource => {
            const loadTime = resource.responseEnd - resource.startTime;
            if (loadTime > 1000) {
                slowResources++;
                console.warn(`⚠️ Slow resource: ${resource.name} (${Math.round(loadTime)}ms)`);
            }
            
            if (resource.transferSize) {
                totalSize += resource.transferSize;
            }
        });
        
        results.metrics.totalResources = totalResources;
        results.metrics.slowResources = slowResources;
        results.metrics.totalSize = Math.round(totalSize / 1024); // KB
        
        console.log(`📊 Total resources: ${totalResources}`);
        console.log(`📊 Slow resources (>1s): ${slowResources}`);
        console.log(`📊 Total transfer size: ${results.metrics.totalSize}KB`);
        
        if (slowResources > 0) {
            results.recommendations.push(`Optimize ${slowResources} slow-loading resources`);
        }
        
        if (results.metrics.totalSize > 2000) {
            results.recommendations.push('Consider reducing total page size (currently > 2MB)');
        }
    }
    
    // Test 3: Check image optimization
    console.log('3. Checking image optimization...');
    
    const images = document.querySelectorAll('img');
    let unoptimizedImages = 0;
    let imagesWithoutLazyLoading = 0;
    
    images.forEach(img => {
        // Check for WebP support
        if (!img.src.includes('.webp') && !img.dataset.webp) {
            unoptimizedImages++;
        }
        
        // Check for lazy loading
        if (!img.hasAttribute('loading') && !img.dataset.src) {
            imagesWithoutLazyLoading++;
        }
    });
    
    results.metrics.totalImages = images.length;
    results.metrics.unoptimizedImages = unoptimizedImages;
    results.metrics.imagesWithoutLazyLoading = imagesWithoutLazyLoading;
    
    console.log(`📊 Total images: ${images.length}`);
    console.log(`📊 Images without WebP: ${unoptimizedImages}`);
    console.log(`📊 Images without lazy loading: ${imagesWithoutLazyLoading}`);
    
    if (unoptimizedImages > 0) {
        results.recommendations.push('Consider using WebP format for better compression');
    }
    
    if (imagesWithoutLazyLoading > 0) {
        results.recommendations.push('Implement lazy loading for all non-critical images');
    }
    
    // Test 4: Check CSS and JS optimization
    console.log('4. Checking CSS and JS optimization...');
    
    const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
    const scripts = document.querySelectorAll('script[src]');
    
    let externalCSS = 0;
    let externalJS = 0;
    let inlineCSS = document.querySelectorAll('style').length;
    let inlineJS = document.querySelectorAll('script:not([src])').length;
    
    stylesheets.forEach(link => {
        if (link.href.startsWith('http')) {
            externalCSS++;
        }
    });
    
    scripts.forEach(script => {
        if (script.src.startsWith('http')) {
            externalJS++;
        }
    });
    
    results.metrics.externalCSS = externalCSS;
    results.metrics.externalJS = externalJS;
    results.metrics.inlineCSS = inlineCSS;
    results.metrics.inlineJS = inlineJS;
    
    console.log(`📊 External CSS files: ${externalCSS}`);
    console.log(`📊 External JS files: ${externalJS}`);
    console.log(`📊 Inline CSS blocks: ${inlineCSS}`);
    console.log(`📊 Inline JS blocks: ${inlineJS}`);
    
    if (externalCSS > 3) {
        results.recommendations.push('Consider combining CSS files to reduce HTTP requests');
    }
    
    if (externalJS > 5) {
        results.recommendations.push('Consider combining JavaScript files to reduce HTTP requests');
    }
    
    // Test 5: Check font loading
    console.log('5. Checking font loading...');
    
    const fontLinks = document.querySelectorAll('link[href*="fonts.googleapis.com"]');
    let fontsOptimized = 0;
    
    fontLinks.forEach(link => {
        if (link.href.includes('display=swap')) {
            fontsOptimized++;
        }
    });
    
    results.metrics.totalFonts = fontLinks.length;
    results.metrics.optimizedFonts = fontsOptimized;
    
    console.log(`📊 Total font links: ${fontLinks.length}`);
    console.log(`📊 Fonts with display=swap: ${fontsOptimized}`);
    
    if (fontsOptimized < fontLinks.length) {
        results.recommendations.push('Add font-display: swap to all web fonts');
    }
    
    // Test 6: Check for service worker
    console.log('6. Checking service worker...');
    
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then(registrations => {
            if (registrations.length > 0) {
                console.log('✅ Service worker registered');
                results.metrics.serviceWorker = true;
            } else {
                console.log('⚠️ No service worker found');
                results.metrics.serviceWorker = false;
                results.recommendations.push('Consider implementing a service worker for caching');
            }
        });
    } else {
        console.log('❌ Service worker not supported');
        results.metrics.serviceWorker = false;
    }
    
    // Test 7: Check for preload/prefetch hints
    console.log('7. Checking resource hints...');
    
    const preloadLinks = document.querySelectorAll('link[rel="preload"]');
    const prefetchLinks = document.querySelectorAll('link[rel="prefetch"]');
    const dnsPreconnect = document.querySelectorAll('link[rel="preconnect"], link[rel="dns-prefetch"]');
    
    results.metrics.preloadHints = preloadLinks.length;
    results.metrics.prefetchHints = prefetchLinks.length;
    results.metrics.dnsHints = dnsPreconnect.length;
    
    console.log(`📊 Preload hints: ${preloadLinks.length}`);
    console.log(`📊 Prefetch hints: ${prefetchLinks.length}`);
    console.log(`📊 DNS hints: ${dnsPreconnect.length}`);
    
    if (dnsPreconnect.length === 0) {
        results.recommendations.push('Add DNS prefetch/preconnect hints for external resources');
    }
    
    // Test 8: Check animation performance
    console.log('8. Checking animation performance...');
    
    const animatedElements = document.querySelectorAll('[style*="transform"], [style*="opacity"], .gsap-enabled *');
    let animationsOptimized = 0;
    
    // Check if animations use transform/opacity (GPU accelerated)
    const styles = Array.from(document.styleSheets);
    styles.forEach(sheet => {
        try {
            Array.from(sheet.cssRules).forEach(rule => {
                if (rule.style && (rule.style.transform || rule.style.opacity)) {
                    animationsOptimized++;
                }
            });
        } catch (e) {
            // Cross-origin stylesheet
        }
    });
    
    results.metrics.animatedElements = animatedElements.length;
    results.metrics.optimizedAnimations = animationsOptimized;
    
    console.log(`📊 Animated elements: ${animatedElements.length}`);
    console.log(`📊 GPU-optimized animations: ${animationsOptimized}`);
    
    // Calculate performance score
    let score = 100;
    
    // Deduct points for issues
    if (results.metrics.slowResources > 0) score -= 10;
    if (results.metrics.totalSize > 2000) score -= 15;
    if (results.metrics.unoptimizedImages > 0) score -= 10;
    if (results.metrics.imagesWithoutLazyLoading > 0) score -= 10;
    if (results.metrics.externalCSS > 3) score -= 5;
    if (results.metrics.externalJS > 5) score -= 5;
    if (!results.metrics.serviceWorker) score -= 10;
    if (results.metrics.dnsHints === 0) score -= 5;
    if (results.metrics.optimizedFonts < results.metrics.totalFonts) score -= 5;
    
    results.score = Math.max(0, score);
    
    // Display results
    console.log('\n📊 Performance Test Results:');
    console.log(`🎯 Performance Score: ${results.score}%`);
    
    if (results.recommendations.length > 0) {
        console.log('\n💡 Recommendations:');
        results.recommendations.forEach((rec, index) => {
            console.log(`${index + 1}. ${rec}`);
        });
    }
    
    if (results.score >= 90) {
        console.log('🎉 Excellent performance!');
    } else if (results.score >= 75) {
        console.log('👍 Good performance, minor optimizations possible');
    } else if (results.score >= 60) {
        console.log('⚠️ Moderate performance, several optimizations recommended');
    } else {
        console.log('❌ Poor performance, significant optimizations needed');
    }
    
    return results;
})();