#!/usr/bin/env python3
"""
Comprehensive Regression Test Suite

Ensures that all breakthrough implementations continue working as we expand.
This test suite should be run before any major changes to prevent regressions.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import json

sys.path.insert(0, 'src')

# Test configuration
REGRESSION_TESTS = [
    {
        "name": "Science.org Baseline",
        "url": "https://www.science.org/doi/10.1126/science.aao0702",
        "doi": "10.1126/science.aao0702",
        "expected_main_pdfs": 1,
        "expected_total_pdfs": 3,
        "expected_translator": "Atypon Journals",
        "critical": True  # Must pass for system to be functional
    }
    # Future test cases will be added here:
    # {
    #     "name": "Nature Article",
    #     "url": "https://www.nature.com/articles/...",
    #     "expected_main_pdfs": 1,
    #     "expected_total_pdfs": 2,
    #     "critical": True
    # }
]

class RegressionTester:
    """Comprehensive regression testing for all breakthrough implementations."""
    
    def __init__(self):
        self.results = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_dir = Path(f"downloads/regression_test_{self.timestamp}")
        self.test_dir.mkdir(parents=True, exist_ok=True)
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete regression test suite."""
        print('🧪 COMPREHENSIVE REGRESSION TEST SUITE')
        print('='*60)
        print('🎯 Goal: Ensure no regressions in breakthrough implementations')
        print('🔍 Testing: Invisible browser + Classification + Screenshots')
        print('='*60)
        
        overall_results = {
            "timestamp": self.timestamp,
            "total_tests": len(REGRESSION_TESTS),
            "passed": 0,
            "failed": 0,
            "critical_failures": 0,
            "test_results": [],
            "system_status": "UNKNOWN"
        }
        
        for i, test_case in enumerate(REGRESSION_TESTS, 1):
            print(f'\n🧪 Test {i}/{len(REGRESSION_TESTS)}: {test_case["name"]}')
            print(f'{"🔥 CRITICAL" if test_case["critical"] else "📋 STANDARD"} | URL: {test_case["url"][:50]}...')
            
            test_result = await self.run_single_test(test_case)
            overall_results["test_results"].append(test_result)
            
            if test_result["passed"]:
                overall_results["passed"] += 1
                print(f'✅ PASSED: {test_case["name"]}')
            else:
                overall_results["failed"] += 1
                print(f'❌ FAILED: {test_case["name"]}')
                if test_case["critical"]:
                    overall_results["critical_failures"] += 1
                    print(f'🚨 CRITICAL FAILURE: System functionality compromised')
        
        # Determine overall system status
        if overall_results["critical_failures"] > 0:
            overall_results["system_status"] = "CRITICAL_FAILURE"
        elif overall_results["failed"] > 0:
            overall_results["system_status"] = "DEGRADED"
        else:
            overall_results["system_status"] = "HEALTHY"
        
        # Save detailed results
        results_file = self.test_dir / "regression_results.json"
        with open(results_file, 'w') as f:
            json.dump(overall_results, f, indent=2, default=str)
        
        # Print summary
        self.print_summary(overall_results)
        
        return overall_results
    
    async def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single regression test case."""
        test_result = {
            "name": test_case["name"],
            "url": test_case["url"],
            "timestamp": datetime.now().isoformat(),
            "passed": False,
            "failures": [],
            "measurements": {},
            "critical": test_case["critical"]
        }
        
        try:
            # Import here to avoid import issues during startup
            from scitex.scholar.browser.local._BrowserManager import BrowserManager
            from scitex.scholar.auth._AuthenticationManager import AuthenticationManager
            from scitex.scholar.utils._JavaScriptInjectionPDFDetector import JavaScriptInjectionPDFDetector
            from scitex.scholar.utils._PDFClassifier import PDFClassifier
            
            # Test 1: Invisible Browser Initialization
            print('   🎭 Testing invisible browser initialization...')
            auth_manager = AuthenticationManager()
            manager = BrowserManager(
                auth_manager=auth_manager,
                invisible=True,
                viewport_size=(1, 1),
                profile_name=f'regression_test_{test_case["name"].lower().replace(" ", "_")}'
            )
            
            try:
                browser, context = await manager.get_authenticated_context()
                test_result["measurements"]["browser_init"] = "SUCCESS"
                print('   ✅ Invisible browser initialized')
            except Exception as e:
                test_result["failures"].append(f"Browser initialization failed: {e}")
                test_result["measurements"]["browser_init"] = "FAILED"
                return test_result
            
            page = await context.new_page()
            
            # Test 2: Dimension Spoofing
            print('   🎭 Testing dimension spoofing...')
            start_time = datetime.now()
            await page.goto(test_case["url"], timeout=60000)
            await page.wait_for_timeout(3000)
            navigation_time = (datetime.now() - start_time).total_seconds()
            
            dimension_check = await page.evaluate('''
                () => {
                    return {
                        reportedWidth: window.innerWidth,
                        reportedHeight: window.innerHeight,
                        blocked: document.body.textContent.toLowerCase().includes('verifying you are human'),
                        hasArticle: document.querySelector('[data-testid="article-title"], .article-title, h1') !== null
                    };
                }
            ''')
            
            test_result["measurements"]["navigation_time"] = navigation_time
            test_result["measurements"]["reported_dimensions"] = f"{dimension_check['reportedWidth']}x{dimension_check['reportedHeight']}"
            test_result["measurements"]["bot_detection_bypassed"] = not dimension_check["blocked"]
            test_result["measurements"]["article_loaded"] = dimension_check["hasArticle"]
            
            if dimension_check["blocked"]:
                test_result["failures"].append("Bot detection not bypassed")
                print('   ❌ Bot detection failed')
            else:
                print('   ✅ Bot detection bypassed')
            
            if not dimension_check["hasArticle"]:
                test_result["failures"].append("Article content not loaded")
                print('   ❌ Article content not loaded')
            else:
                print('   ✅ Article content loaded')
            
            # Test 3: PDF Classification
            print('   🔍 Testing PDF classification...')
            
            # Direct classifier test with known URLs
            classifier = PDFClassifier()
            test_urls = [
                "https://www.science.org/doi/suppl/10.1126/science.aao0702/suppl_file/aao0702_norimoto_sm.pdf",
                "https://www.science.org/doi/suppl/10.1126/science.aao0702/suppl_file/aao0702_norimoto_sm.revision.1.pdf", 
                "https://www.science.org/doi/pdf/10.1126/science.aao0702"
            ]
            
            classification_result = classifier.classify_pdf_list(test_urls)
            
            test_result["measurements"]["total_pdfs_classified"] = classification_result["total_count"]
            test_result["measurements"]["main_pdfs_found"] = classification_result["main_count"]
            test_result["measurements"]["supplementary_pdfs_found"] = classification_result["supplementary_count"]
            
            # Check expectations
            if "expected_main_pdfs" in test_case:
                if classification_result["main_count"] != test_case["expected_main_pdfs"]:
                    test_result["failures"].append(f"Expected {test_case['expected_main_pdfs']} main PDFs, got {classification_result['main_count']}")
                else:
                    print(f'   ✅ Correct main PDF count: {classification_result["main_count"]}')
            
            if "expected_total_pdfs" in test_case:
                if classification_result["total_count"] != test_case["expected_total_pdfs"]:
                    test_result["failures"].append(f"Expected {test_case['expected_total_pdfs']} total PDFs, got {classification_result['total_count']}")
                else:
                    print(f'   ✅ Correct total PDF count: {classification_result["total_count"]}')
            
            # Test 4: Screenshot Integration
            print('   📸 Testing screenshot capability...')
            try:
                from scitex.scholar.utils._DirectPDFDownloader import DirectPDFDownloader
                downloader = DirectPDFDownloader(capture_screenshots=True)
                
                # Test screenshot capture without download
                screenshot_path = await downloader._capture_download_screenshot(
                    page, 
                    self.test_dir / f"{test_case['name'].replace(' ', '_')}_test.pdf",
                    "regression_test"
                )
                
                if screenshot_path and Path(screenshot_path).exists():
                    screenshot_size = Path(screenshot_path).stat().st_size / 1024
                    test_result["measurements"]["screenshot_captured"] = True
                    test_result["measurements"]["screenshot_size_kb"] = screenshot_size
                    print(f'   ✅ Screenshot captured: {screenshot_size:.1f}KB')
                else:
                    test_result["failures"].append("Screenshot capture failed")
                    test_result["measurements"]["screenshot_captured"] = False
                    print('   ❌ Screenshot capture failed')
                    
            except Exception as e:
                test_result["failures"].append(f"Screenshot test failed: {e}")
                test_result["measurements"]["screenshot_captured"] = False
            
            # Test 5: Overall System Integration
            print('   🔧 Testing system integration...')
            
            integration_checks = [
                ("invisible_browser", manager.invisible == True),
                ("viewport_size", manager.viewport_size == (1, 1)),
                ("dimension_spoofing", dimension_check["reportedWidth"] > 1000),  # Should report large dimensions
                ("classification_working", classification_result["main_count"] > 0),
                ("no_bot_detection", not dimension_check["blocked"]),
                ("article_accessible", dimension_check["hasArticle"])
            ]
            
            test_result["measurements"]["integration_checks"] = {}
            for check_name, passed in integration_checks:
                test_result["measurements"]["integration_checks"][check_name] = passed
                if not passed:
                    test_result["failures"].append(f"Integration check failed: {check_name}")
            
            await manager.__aexit__(None, None, None)
            
        except Exception as e:
            test_result["failures"].append(f"Test execution failed: {e}")
        
        # Determine if test passed
        test_result["passed"] = len(test_result["failures"]) == 0
        
        return test_result
    
    def print_summary(self, results: Dict[str, Any]):
        """Print comprehensive test summary."""
        print(f'\n🏆 REGRESSION TEST SUMMARY')
        print('='*60)
        print(f'📊 System Status: {results["system_status"]}')
        print(f'📈 Tests Passed: {results["passed"]}/{results["total_tests"]}')
        print(f'📉 Tests Failed: {results["failed"]}/{results["total_tests"]}')
        print(f'🚨 Critical Failures: {results["critical_failures"]}')
        
        if results["system_status"] == "HEALTHY":
            print('\n✅ ALL SYSTEMS OPERATIONAL')
            print('🎉 No regressions detected - safe to deploy!')
            
        elif results["system_status"] == "DEGRADED":
            print('\n⚠️  SYSTEM DEGRADED')
            print('🔍 Non-critical issues detected - review recommended')
            
        else:
            print('\n🚨 CRITICAL SYSTEM FAILURE')
            print('❌ Core functionality broken - deployment blocked!')
            
        print(f'\n📁 Detailed results: {self.test_dir}/regression_results.json')
        print('='*60)
        
        # Show critical test details
        for test_result in results["test_results"]:
            if not test_result["passed"] and test_result["critical"]:
                print(f'\n🚨 CRITICAL FAILURE: {test_result["name"]}')
                for failure in test_result["failures"]:
                    print(f'   ❌ {failure}')
        
        # Show system health metrics
        print(f'\n📊 SYSTEM HEALTH METRICS:')
        for test_result in results["test_results"]:
            if test_result["passed"]:
                measurements = test_result["measurements"]
                print(f'✅ {test_result["name"]}:')
                print(f'   🎭 Invisible: {measurements.get("browser_init", "?")}')
                print(f'   🤖 Bot bypass: {measurements.get("bot_detection_bypassed", "?")}')
                print(f'   🔍 Classification: {measurements.get("main_pdfs_found", "?")} main PDFs')
                print(f'   📸 Screenshots: {measurements.get("screenshot_captured", "?")}')

async def main():
    """Run regression test suite."""
    # Set environment variables
    os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"] = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    os.environ["SCITEX_SCHOLAR_ZOTERO_TRANSLATORS_DIR"] = "/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/zotero_translators/"
    
    # Remove ZenRows to ensure local browser
    if "SCITEX_SCHOLAR_ZENROWS_API_KEY" in os.environ:
        del os.environ["SCITEX_SCHOLAR_ZENROWS_API_KEY"]
    
    tester = RegressionTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    if results["system_status"] == "CRITICAL_FAILURE":
        print('\n🚨 DEPLOYMENT BLOCKED due to critical failures!')
        exit(1)
    elif results["system_status"] == "DEGRADED":
        print('\n⚠️  DEPLOYMENT WITH CAUTION - non-critical issues detected')
        exit(2)
    else:
        print('\n🚀 DEPLOYMENT APPROVED - all systems operational!')
        exit(0)

if __name__ == "__main__":
    asyncio.run(main())