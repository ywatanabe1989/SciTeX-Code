#!/usr/bin/env python3
"""
Generalized PDF Detection System

This module consolidates all the scattered JavaScript PDF detection patterns
into a unified, publisher-agnostic system based on Zotero translator knowledge
and proven working patterns from Science.org, Nature.com, and other publishers.

Based on user feedback: "there are many js scripts; it would be very grateful
if pdf detection logics can be generalizable"
"""

import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class PDFCandidate:
    """Represents a potential PDF download link with confidence scoring."""
    text: str
    href: str
    selector: str
    element_type: str  # 'link', 'button', 'form', etc.
    confidence: float  # 0.0 to 1.0
    is_main_article: bool = True
    is_supplementary: bool = False
    file_size_hint: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PublisherProfile:
    """Publisher-specific detection patterns based on Zotero translator knowledge."""
    name: str
    domain_patterns: List[str]
    primary_selectors: List[str]
    fallback_selectors: List[str]
    exclusion_patterns: List[str]
    confidence_boost: float = 0.0  # Boost confidence for known good publishers


class GeneralizedPDFDetector:
    """
    Unified PDF detection system that consolidates patterns from multiple sources:
    - Zotero translator knowledge
    - Working Science.org patterns
    - Working Nature.com patterns
    - Atypon Journals patterns
    - General academic publisher patterns
    """
    
    def __init__(self):
        self.publisher_profiles = self._initialize_publisher_profiles()
        self._generic_selectors = self._initialize_generic_selectors()
        
    def _initialize_publisher_profiles(self) -> Dict[str, PublisherProfile]:
        """Initialize known publisher profiles based on Zotero translator patterns."""
        profiles = {}
        
        # Science.org (AAAS) - Based on working implementation
        profiles['science'] = PublisherProfile(
            name="Science (AAAS)",
            domain_patterns=['science.org', 'sciencemag.org'],
            primary_selectors=[
                'a[href*="/doi/pdf/"]',  # Direct PDF URL pattern
                'a[data-track-action*="pdf"]',  # Science.org specific
                'a[title*="PDF"]',
                '.article-pdf-link',
                '.pdf-link'
            ],
            fallback_selectors=[
                'a[href*=".pdf"]',
                'a:contains("PDF")',
                'button[title*="PDF"]'
            ],
            exclusion_patterns=['supplement', 'supporting', 'appendix'],
            confidence_boost=0.2
        )
        
        # Nature.com - Based on working implementation
        profiles['nature'] = PublisherProfile(
            name="Nature Publishing Group",
            domain_patterns=['nature.com', 'springernature.com'],
            primary_selectors=[
                'a[href*="/articles/"][href*=".pdf"]',  # Nature direct PDF
                'a[data-track-action*="download pdf"]',
                '.c-pdf-download__link',
                '.pdf-download-link',
                'a[title*="Download PDF"]'
            ],
            fallback_selectors=[
                'a[href*="pdf"]',
                '.c-article-pdf-download',
                'button:contains("PDF")'
            ],
            exclusion_patterns=['supplementary', 'extended data', 'correction'],
            confidence_boost=0.2
        )
        
        # Atypon Journals - Based on Zotero translator
        profiles['atypon'] = PublisherProfile(
            name="Atypon Journals",
            domain_patterns=['acs.org', 'liebertpub.com', 'future-science.com'],
            primary_selectors=[
                'a[href*="/doi/pdf"]',
                '.pdf-link',
                'a[title*="PDF"]',
                '.article-pdfLink'
            ],
            fallback_selectors=[
                'a[href*="pdf"]',
                '.downloadPdf'
            ],
            exclusion_patterns=['supporting', 'supplement'],
            confidence_boost=0.15
        )
        
        # Elsevier ScienceDirect
        profiles['elsevier'] = PublisherProfile(
            name="Elsevier ScienceDirect",
            domain_patterns=['sciencedirect.com', 'elsevier.com'],
            primary_selectors=[
                'a[href*="pdfft"]',  # ScienceDirect PDF pattern
                '.download-pdf-link',
                'a[aria-label*="Download PDF"]',
                '.pdf-download'
            ],
            fallback_selectors=[
                'a[href*="pdf"]',
                'button:contains("PDF")'
            ],
            exclusion_patterns=['supplementary material'],
            confidence_boost=0.15
        )
        
        # Wiley
        profiles['wiley'] = PublisherProfile(
            name="Wiley",
            domain_patterns=['wiley.com', 'onlinelibrary.wiley.com'],
            primary_selectors=[
                'a[href*="pdf"]',
                '.pdf-link',
                'a[title*="PDF"]'
            ],
            fallback_selectors=[
                '.download-pdf'
            ],
            exclusion_patterns=['supporting information'],
            confidence_boost=0.1
        )
        
        return profiles
    
    def _initialize_generic_selectors(self) -> Dict[str, List[str]]:
        """Initialize generic selectors that work across publishers."""
        return {
            'high_confidence': [
                # Direct PDF links
                'a[href$=".pdf"]',
                'a[href*="/pdf/"]',
                'a[href*="pdf"][href*="download"]',
                
                # Semantic selectors
                '.pdf-download',
                '.pdf-link',
                '.article-pdf',
                '.download-pdf',
                
                # ARIA and accessibility
                'a[aria-label*="PDF"]',
                'a[title*="Download PDF"]',
                'button[aria-label*="PDF"]'
            ],
            
            'medium_confidence': [
                # Generic PDF references
                'a[href*="pdf"]',
                'a[title*="PDF"]',
                'button[title*="PDF"]',
                
                # Download buttons
                '.download-link',
                'a:contains("Download")',
                'button:contains("PDF")',
                
                # Form submissions
                'input[value*="PDF"]',
                'input[title*="PDF"]'
            ],
            
            'low_confidence': [
                # Very generic patterns
                'a:contains("PDF")',
                'button:contains("Download")',
                '.download',
                '[onclick*="pdf"]'
            ]
        }
    
    def detect_publisher(self, url: str, page_content: str = "") -> Optional[PublisherProfile]:
        """Detect which publisher profile to use based on URL and content."""
        url_lower = url.lower()
        
        for profile in self.publisher_profiles.values():
            for pattern in profile.domain_patterns:
                if pattern in url_lower:
                    logger.info(f"Detected publisher: {profile.name}")
                    return profile
        
        return None
    
    async def detect_pdf_candidates(self, page, doi: str = "", url: str = "") -> List[PDFCandidate]:
        """
        Main detection method that finds all PDF candidates on a page.
        
        Args:
            page: Playwright page object
            doi: DOI of the article (optional, helps with pattern matching)
            url: Current page URL (optional, helps with publisher detection)
        
        Returns:
            List of PDFCandidate objects sorted by confidence score
        """
        candidates = []
        
        # Detect publisher
        current_url = url or await page.url()
        publisher = self.detect_publisher(current_url)
        
        # Get all potential PDF elements using comprehensive JavaScript
        pdf_detection_js = self._generate_detection_javascript(doi, publisher)
        raw_candidates = await page.evaluate(pdf_detection_js)
        
        # Process and score candidates
        for raw_candidate in raw_candidates:
            candidate = self._process_raw_candidate(raw_candidate, publisher)
            if candidate and candidate.confidence > 0.1:  # Filter very low confidence
                candidates.append(candidate)
        
        # Sort by confidence (highest first)
        candidates.sort(key=lambda x: x.confidence, reverse=True)
        
        # Remove duplicates (same href)
        seen_hrefs = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate.href not in seen_hrefs:
                seen_hrefs.add(candidate.href)
                unique_candidates.append(candidate)
        
        logger.info(f"Found {len(unique_candidates)} unique PDF candidates out of {len(candidates)} total")
        
        return unique_candidates
    
    def _generate_detection_javascript(self, doi: str, publisher: Optional[PublisherProfile]) -> str:
        """Generate comprehensive JavaScript for PDF detection."""
        
        # Build selector lists
        selectors = []
        
        # Add publisher-specific selectors first (higher priority)
        if publisher:
            selectors.extend(publisher.primary_selectors)
            selectors.extend(publisher.fallback_selectors)
        
        # Add generic selectors
        for confidence_level in ['high_confidence', 'medium_confidence', 'low_confidence']:
            selectors.extend(self._generic_selectors[confidence_level])
        
        # Generate JavaScript
        js_code = f"""
        () => {{
            const doi = "{doi}";
            const selectors = {selectors};
            const exclusionPatterns = {publisher.exclusion_patterns if publisher else []};
            
            let candidates = [];
            
            // Process each selector
            for (let i = 0; i < selectors.length; i++) {{
                const selector = selectors[i];
                let confidence = 1.0 - (i * 0.05); // Decrease confidence for later selectors
                
                try {{
                    const elements = Array.from(document.querySelectorAll(selector));
                    
                    for (const el of elements) {{
                        // Skip invisible elements
                        if (el.offsetParent === null) continue;
                        
                        const text = (el.textContent || '').trim();
                        const href = el.href || el.getAttribute('href') || '';
                        const title = el.title || el.getAttribute('title') || '';
                        const ariaLabel = el.getAttribute('aria-label') || '';
                        
                        // Skip if no useful content
                        if (!text && !href && !title && !ariaLabel) continue;
                        
                        // Check exclusion patterns
                        const fullText = (text + ' ' + title + ' ' + ariaLabel).toLowerCase();
                        let isExcluded = false;
                        for (const pattern of exclusionPatterns) {{
                            if (fullText.includes(pattern.toLowerCase())) {{
                                isExcluded = true;
                                break;
                            }}
                        }}
                        
                        if (isExcluded) continue;
                        
                        // Calculate confidence adjustments
                        let confidenceAdjustment = 0;
                        
                        // Boost confidence for direct PDF links
                        if (href.includes('.pdf')) confidenceAdjustment += 0.3;
                        if (href.includes('/pdf/')) confidenceAdjustment += 0.2;
                        if (href.includes(doi) && doi) confidenceAdjustment += 0.2;
                        
                        // Boost for explicit PDF text
                        if (text.toLowerCase().includes('pdf')) confidenceAdjustment += 0.1;
                        if (title.toLowerCase().includes('pdf')) confidenceAdjustment += 0.1;
                        
                        // Reduce confidence for supplementary materials
                        if (fullText.includes('supplement') || fullText.includes('supporting')) {{
                            confidenceAdjustment -= 0.3;
                        }}
                        
                        candidates.push({{
                            text: text,
                            href: href,
                            selector: selector,
                            element_type: el.tagName.toLowerCase(),
                            confidence: Math.max(0, Math.min(1, confidence + confidenceAdjustment)),
                            is_main_article: !fullText.includes('supplement') && !fullText.includes('supporting'),
                            is_supplementary: fullText.includes('supplement') || fullText.includes('supporting'),
                            metadata: {{
                                title: title,
                                ariaLabel: ariaLabel,
                                className: el.className,
                                id: el.id
                            }}
                        }});
                    }}
                }} catch (e) {{
                    // Skip invalid selectors
                    console.warn('Invalid selector:', selector, e);
                }}
            }}
            
            return candidates;
        }}
        """
        
        return js_code
    
    def _process_raw_candidate(self, raw_candidate: Dict, publisher: Optional[PublisherProfile]) -> Optional[PDFCandidate]:
        """Process raw candidate data into PDFCandidate object."""
        try:
            candidate = PDFCandidate(
                text=raw_candidate.get('text', ''),
                href=raw_candidate.get('href', ''),
                selector=raw_candidate.get('selector', ''),
                element_type=raw_candidate.get('element_type', ''),
                confidence=raw_candidate.get('confidence', 0.0),
                is_main_article=raw_candidate.get('is_main_article', True),
                is_supplementary=raw_candidate.get('is_supplementary', False),
                metadata=raw_candidate.get('metadata', {})
            )
            
            # Apply publisher confidence boost
            if publisher:
                candidate.confidence += publisher.confidence_boost
                candidate.confidence = min(1.0, candidate.confidence)
            
            return candidate
            
        except Exception as e:
            logger.warning(f"Failed to process candidate: {e}")
            return None
    
    async def download_best_pdf(self, page, candidates: List[PDFCandidate], 
                               download_path: Path, timeout: int = 30000) -> Tuple[bool, Optional[str]]:
        """
        Attempt to download PDF using the best candidate.
        
        Returns:
            (success: bool, error_message: Optional[str])
        """
        if not candidates:
            return False, "No PDF candidates found"
        
        best_candidate = candidates[0]  # Already sorted by confidence
        
        logger.info(f"Attempting download with best candidate: {best_candidate.text[:40]}... (confidence: {best_candidate.confidence:.2f})")
        
        try:
            # Method 1: Direct URL navigation
            if best_candidate.href and ('.pdf' in best_candidate.href or '/pdf/' in best_candidate.href):
                download_promise = page.wait_for_event('download', timeout=timeout)
                await page.goto(best_candidate.href)
                
                try:
                    download = await download_promise
                    await download.save_as(str(download_path))
                    
                    if download_path.exists() and download_path.stat().st_size > 1000:
                        return True, None
                        
                except Exception as download_error:
                    logger.warning(f"Direct URL download failed: {download_error}")
            
            # Method 2: Element interaction
            if best_candidate.selector:
                download_promise = page.wait_for_event('download', timeout=timeout)
                
                click_js = f"""
                () => {{
                    const elements = Array.from(document.querySelectorAll('{best_candidate.selector}'));
                    for (const el of elements) {{
                        const text = (el.textContent || '').trim();
                        if (text === '{best_candidate.text}' && el.offsetParent !== null) {{
                            el.click();
                            return 'clicked: ' + text;
                        }}
                    }}
                    
                    // Fallback: click first visible element with the selector
                    for (const el of elements) {{
                        if (el.offsetParent !== null) {{
                            el.click();
                            return 'fallback-clicked: ' + (el.textContent || '').trim();
                        }}
                    }}
                    
                    return 'no-clickable-element';
                }}
                """
                
                click_result = await page.evaluate(click_js)
                
                if 'clicked' in click_result:
                    try:
                        download = await download_promise
                        await download.save_as(str(download_path))
                        
                        if download_path.exists() and download_path.stat().st_size > 1000:
                            return True, None
                            
                    except Exception as click_download_error:
                        logger.warning(f"Click download failed: {click_download_error}")
            
            return False, f"All download methods failed for candidate: {best_candidate.text[:40]}..."
            
        except Exception as e:
            return False, f"Download attempt failed: {str(e)}"
    
    def get_download_report(self, candidates: List[PDFCandidate]) -> str:
        """Generate a human-readable report of PDF detection results."""
        if not candidates:
            return "❌ No PDF candidates found"
        
        report = f"📄 Found {len(candidates)} PDF candidates:\n\n"
        
        for i, candidate in enumerate(candidates[:5]):  # Show top 5
            status = "🎯" if candidate.confidence > 0.7 else "📋" if candidate.confidence > 0.4 else "📝"
            article_type = "📄 Main" if candidate.is_main_article else "📎 Supplement"
            
            report += f"{status} [{i+1}] {article_type} | Confidence: {candidate.confidence:.2f}\n"
            report += f"    Text: \"{candidate.text[:50]}...\"\n"
            report += f"    Selector: {candidate.selector}\n"
            report += f"    URL: {candidate.href[:60]}...\n\n"
        
        if len(candidates) > 5:
            report += f"... and {len(candidates) - 5} more candidates\n\n"
        
        # Recommendations
        best = candidates[0]
        if best.confidence > 0.7:
            report += f"✅ Recommendation: High confidence in best candidate\n"
        elif best.confidence > 0.4:
            report += f"⚠️  Recommendation: Medium confidence - may need manual verification\n"
        else:
            report += f"❌ Recommendation: Low confidence - manual download likely needed\n"
        
        return report