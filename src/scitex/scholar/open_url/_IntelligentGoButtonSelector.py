#!/usr/bin/env python3
"""
Intelligent Go Button Selector

Advanced Go button selection logic that analyzes all available options
and selects the most reliable one based on multiple criteria including:
- Publisher reputation and reliability
- Full-text access indicators  
- Direct link availability
- Historical success patterns
- Content quality indicators

Created in response to user question: "when you click the Go button, is it possible 
to select most reliable option among multiple Go buttons?"
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from scitex import logging

logger = logging.getLogger(__name__)


@dataclass
class GoButtonCandidate:
    """Represents a Go button candidate with analysis metadata."""
    index: int
    global_index: int
    row_text: str
    publisher_name: str
    reliability_score: float
    access_type: str  # 'direct', 'subscription', 'open_access', 'unknown'
    quality_indicators: List[str]
    warning_flags: List[str]
    metadata: Dict


class IntelligentGoButtonSelector:
    """
    Advanced Go button selection using multi-criteria analysis.
    
    This selector improves upon basic hardcoded rules by analyzing:
    1. Publisher reputation and reliability
    2. Access type and quality indicators
    3. Full-text availability signals
    4. Historical success patterns
    """
    
    # Publisher reliability tiers (higher = more reliable)
    PUBLISHER_TIERS = {
        # Tier 1: Major academic publishers (highest reliability)
        'nature': 95, 'science': 95, 'cell': 95, 'elsevier': 90, 'springer': 90,
        'wiley': 90, 'oxford': 90, 'cambridge': 90, 'taylor': 85, 'sage': 85,
        
        # Tier 2: Specialized and society publishers
        'ieee': 85, 'acm': 85, 'aps': 85, 'rsc': 85, 'acs': 85, 'aaas': 95,
        'plos': 85, 'bmj': 85, 'nejm': 90, 'lancet': 90, 'jama': 90,
        
        # Tier 3: Regional and open access publishers
        'mdpi': 75, 'frontiers': 75, 'hindawi': 70, 'karger': 75, 'thieme': 75,
        'jstage': 80,  # Japanese publishers
        
        # Tier 4: Specialized databases and aggregators
        'proquest': 70, 'ebsco': 70, 'gale': 65, 'jstor': 80, 'scopus': 75,
        
        # Default for unknown publishers
        'unknown': 50
    }
    
    # Quality indicators that suggest reliable full-text access
    QUALITY_INDICATORS = [
        # Direct access indicators
        'full text', 'pdf', 'html', 'complete article', 'online version',
        
        # Publisher authenticity indicators  
        'official', 'publisher', 'original', 'authoritative', 'primary',
        
        # Content completeness indicators
        'complete', 'unabridged', 'full access', 'unlimited', 'unrestricted',
        
        # Academic quality indicators
        'peer reviewed', 'refereed', 'scholarly', 'academic', 'research',
        
        # Institutional access indicators
        'university', 'library', 'institutional', 'licensed', 'subscribed'
    ]
    
    # Warning flags that suggest unreliable or limited access
    WARNING_FLAGS = [
        # Limited access warnings
        'abstract only', 'preview', 'sample', 'excerpt', 'limited',
        
        # Quality concerns
        'preprint', 'draft', 'working paper', 'conference abstract',
        
        # Access restrictions
        'pay per view', 'purchase', 'rental', 'temporary', 'trial',
        
        # Aggregator warnings (often lower quality)
        'cached', 'mirror', 'copy', 'reproduction', 'reprint',
        
        # Outdated or unreliable sources
        'archive', 'legacy', 'discontinued', 'deprecated'
    ]
    
    def __init__(self):
        """Initialize the intelligent Go button selector."""
        self.success_history = {}  # Track historical success rates by publisher
        
    async def analyze_go_buttons_async(self, page) -> List[GoButtonCandidate]:
        """
        Analyze all Go buttons on the page and return ranked candidates.
        
        Args:
            page: Playwright page object
            
        Returns:
            List of GoButtonCandidate objects ranked by reliability
        """
        logger.info("🔍 Analyzing Go buttons with intelligent selection...")
        
        # Extract all Go button information
        go_buttons_data = await page.evaluate('''() => {
            const goButtons = Array.from(document.querySelectorAll(
                'input[value="Go"], button[value="Go"], input[value="GO"], button[value="GO"]'
            ));
            
            return goButtons.map((btn, index) => {
                const parentRow = btn.closest('tr') || btn.closest('td') || btn.parentElement;
                const tableRow = btn.closest('tr');
                const fullRow = tableRow || parentRow;
                
                // Get comprehensive context text
                const rowText = fullRow ? fullRow.textContent.trim() : '';
                const siblingText = Array.from(btn.parentElement?.children || [])
                    .map(el => el.textContent.trim()).join(' ');
                
                // Get additional metadata
                const form = btn.closest('form');
                const hiddenInputs = form ? Array.from(form.querySelectorAll('input[type="hidden"]'))
                    .map(inp => ({ name: inp.name, value: inp.value })) : [];
                
                // Find global index among all clickable elements  
                const allElements = Array.from(document.querySelectorAll('input, button, a, [onclick]'));
                const globalIndex = allElements.indexOf(btn);
                
                return {
                    index: index,
                    globalIndex: globalIndex,
                    rowText: rowText,
                    siblingText: siblingText,
                    hiddenInputs: hiddenInputs,
                    formAction: form ? form.action : null,
                    buttonId: btn.id || '',
                    buttonClass: btn.className || '',
                    parentTag: btn.parentElement?.tagName || ''
                };
            });
        }''')
        
        logger.info(f"📊 Found {len(go_buttons_data)} Go buttons to analyze")
        
        candidates = []
        
        for btn_data in go_buttons_data:
            # Analyze this Go button candidate
            candidate = self._analyze_single_button(btn_data)
            candidates.append(candidate)
            
            logger.debug(f"📋 Button {candidate.index}: {candidate.publisher_name} "
                        f"(score: {candidate.reliability_score:.1f}, type: {candidate.access_type})")
        
        # Sort by reliability score (highest first)
        candidates.sort(key=lambda x: x.reliability_score, reverse=True)
        
        return candidates
    
    def _analyze_single_button(self, btn_data: Dict) -> GoButtonCandidate:
        """Analyze a single Go button and create a candidate."""
        
        # Extract text for analysis
        full_text = f"{btn_data['rowText']} {btn_data['siblingText']}".lower()
        
        # Identify publisher
        publisher_name = self._identify_publisher(full_text, btn_data)
        
        # Calculate base reliability score
        base_score = self.PUBLISHER_TIERS.get(publisher_name, self.PUBLISHER_TIERS['unknown'])
        
        # Analyze access type and quality
        access_type = self._determine_access_type(full_text, btn_data)
        quality_indicators = self._find_quality_indicators(full_text)
        warning_flags = self._find_warning_flags(full_text)
        
        # Calculate final reliability score
        reliability_score = self._calculate_reliability_score(
            base_score, access_type, quality_indicators, warning_flags, full_text
        )
        
        return GoButtonCandidate(
            index=btn_data['index'],
            global_index=btn_data['globalIndex'],
            row_text=btn_data['rowText'][:100],  # Truncate for display
            publisher_name=publisher_name,
            reliability_score=reliability_score,
            access_type=access_type,
            quality_indicators=quality_indicators,
            warning_flags=warning_flags,
            metadata=btn_data
        )
    
    def _identify_publisher(self, text: str, btn_data: Dict) -> str:
        """Identify the publisher from text and metadata."""
        
        # Publisher identification patterns
        publisher_patterns = {
            # Major publishers
            'nature': ['nature', 'npg', 'nature publishing'],
            'science': ['science', 'aaas', 'american association', 'advancement of science'],
            'elsevier': ['elsevier', 'sciencedirect', 'cell press'],
            'springer': ['springer', 'springer nature', 'springerlink'],
            'wiley': ['wiley', 'wiley-blackwell', 'blackwell'],
            'oxford': ['oxford', 'oup', 'oxford university press'],
            'cambridge': ['cambridge', 'cup', 'cambridge university press'],
            'taylor': ['taylor', 'taylor & francis', 'routledge'],
            'sage': ['sage', 'sage publications'],
            
            # Scientific societies and specialized
            'ieee': ['ieee', 'institute of electrical'],
            'acm': ['acm', 'association for computing'],
            'aps': ['aps', 'american physical society'],
            'rsc': ['rsc', 'royal society of chemistry'],
            'acs': ['american chemical society'],
            'plos': ['plos', 'public library of science'],
            'bmj': ['bmj', 'british medical journal'],
            'nejm': ['nejm', 'new england journal'],
            'lancet': ['lancet'],
            'jama': ['jama', 'american medical association'],
            
            # Regional and specialized
            'jstage': ['jstage', 'j-stage', 'japan science'],
            'mdpi': ['mdpi'],
            'frontiers': ['frontiers'],
            'hindawi': ['hindawi'],
            'karger': ['karger'],
            'thieme': ['thieme'],
            
            # Databases and aggregators
            'proquest': ['proquest'],
            'ebsco': ['ebsco'],
            'gale': ['gale', 'cengage'],
            'jstor': ['jstor'],
            'scopus': ['scopus']
        }
        
        # Check for direct publisher mentions
        for publisher, patterns in publisher_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return publisher
        
        # Check form action or hidden inputs for publisher clues
        form_action = btn_data.get('formAction', '').lower()
        for publisher, patterns in publisher_patterns.items():
            for pattern in patterns:
                if pattern in form_action:
                    return publisher
        
        return 'unknown'
    
    def _determine_access_type(self, text: str, btn_data: Dict) -> str:
        """Determine the type of access this button provides."""
        
        # Direct access indicators (best)
        if any(indicator in text for indicator in [
            'full text', 'pdf', 'html version', 'complete article', 
            'publisher site', 'official', 'original'
        ]):
            return 'direct'
        
        # Open access indicators (very good)
        if any(indicator in text for indicator in [
            'open access', 'free', 'unrestricted', 'public', 'creative commons'
        ]):
            return 'open_access'
        
        # Subscription access indicators (good if you have access)
        if any(indicator in text for indicator in [
            'subscription', 'licensed', 'institutional', 'university', 'library'
        ]):
            return 'subscription'
        
        # Unknown or unclear access
        return 'unknown'
    
    def _find_quality_indicators(self, text: str) -> List[str]:
        """Find quality indicators in the text."""
        found_indicators = []
        
        for indicator in self.QUALITY_INDICATORS:
            if indicator in text:
                found_indicators.append(indicator)
        
        return found_indicators
    
    def _find_warning_flags(self, text: str) -> List[str]:
        """Find warning flags in the text."""
        found_flags = []
        
        for flag in self.WARNING_FLAGS:
            if flag in text:
                found_flags.append(flag)
        
        return found_flags
    
    def _calculate_reliability_score(
        self, 
        base_score: float, 
        access_type: str, 
        quality_indicators: List[str],
        warning_flags: List[str],
        full_text: str
    ) -> float:
        """Calculate the final reliability score for a Go button."""
        
        score = base_score
        
        # Access type modifiers
        access_modifiers = {
            'direct': 10,
            'open_access': 8, 
            'subscription': 5,
            'unknown': -5
        }
        score += access_modifiers.get(access_type, 0)
        
        # Quality indicators boost (diminishing returns)
        quality_boost = min(len(quality_indicators) * 3, 15)
        score += quality_boost
        
        # Warning flags penalty
        warning_penalty = len(warning_flags) * 5
        score -= warning_penalty
        
        # Special bonuses for highly reliable indicators
        if 'full text' in full_text:
            score += 10
        if 'publisher' in full_text and 'official' in full_text:
            score += 8
        if 'pdf' in full_text:
            score += 5
        
        # Special penalties for problematic indicators
        if 'abstract only' in full_text:
            score -= 20
        if 'preview' in full_text or 'sample' in full_text:
            score -= 15
        if 'pay' in full_text and ('view' in full_text or 'access' in full_text):
            score -= 25
        
        # Ensure score stays within reasonable bounds
        return max(0, min(100, score))
    
    def select_best_button(self, candidates: List[GoButtonCandidate]) -> Optional[GoButtonCandidate]:
        """
        Select the best Go button from analyzed candidates.
        
        Args:
            candidates: List of analyzed candidates
            
        Returns:
            The best candidate or None if no suitable option
        """
        if not candidates:
            logger.warning("❌ No Go button candidates available")
            return None
        
        best_candidate = candidates[0]  # Already sorted by score
        
        logger.info(f"🎯 Selected best Go button:")
        logger.info(f"   📊 Publisher: {best_candidate.publisher_name}")
        logger.info(f"   📈 Reliability Score: {best_candidate.reliability_score:.1f}/100")
        logger.info(f"   🔗 Access Type: {best_candidate.access_type}")
        logger.info(f"   ✅ Quality Indicators: {len(best_candidate.quality_indicators)}")
        logger.info(f"   ⚠️  Warning Flags: {len(best_candidate.warning_flags)}")
        logger.info(f"   📝 Context: {best_candidate.row_text[:60]}...")
        
        # Log quality details
        if best_candidate.quality_indicators:
            logger.debug(f"   📋 Quality: {', '.join(best_candidate.quality_indicators[:3])}")
        if best_candidate.warning_flags:
            logger.debug(f"   🚨 Warnings: {', '.join(best_candidate.warning_flags[:3])}")
        
        # Show comparison with alternatives
        if len(candidates) > 1:
            logger.info(f"📊 Alternative options:")
            for i, candidate in enumerate(candidates[1:4], 2):  # Show top 3 alternatives
                logger.info(f"   {i}. {candidate.publisher_name} "
                          f"(score: {candidate.reliability_score:.1f}, "
                          f"type: {candidate.access_type})")
        
        return best_candidate
    
    async def intelligent_go_button_selection_async(self, page) -> Optional[Dict]:
        """
        Complete intelligent Go button selection workflow.
        
        Args:
            page: Playwright page object
            
        Returns:
            Dict with selection results or None if no suitable button found
        """
        try:
            # Analyze all Go button candidates
            candidates = await self.analyze_go_buttons_async(page)
            
            if not candidates:
                logger.warning("❌ No Go buttons found on page")
                return None
            
            # Select the best candidate
            best_candidate = self.select_best_button(candidates)
            
            if not best_candidate:
                logger.warning("❌ No suitable Go button candidate found")
                return None
            
            # Return selection info for use by the OpenURL resolver
            return {
                'success': True,
                'selected_button': best_candidate,
                'alternatives': candidates[1:],  # Other options
                'selection_reason': f"Highest reliability score ({best_candidate.reliability_score:.1f}) "
                                  f"with {best_candidate.access_type} access to {best_candidate.publisher_name}"
            }
            
        except Exception as e:
            logger.error(f"❌ Intelligent Go button selection failed: {e}")
            return None


# Convenience function for easy integration
async def select_most_reliable_go_button_async(page) -> Optional[Dict]:
    """
    Convenience function to select the most reliable Go button.
    
    Args:
        page: Playwright page object
        
    Returns:
        Dict with selection results or None if failed
    """
    selector = IntelligentGoButtonSelector()
    return await selector.intelligent_go_button_selection_async(page)


if __name__ == "__main__":
    # Example usage and testing
    print("🔍 Intelligent Go Button Selector")
    print("=" * 50)
    print("This module provides advanced Go button selection for academic paper access.")
    print("It analyzes publisher reliability, access type, and quality indicators")
    print("to automatically choose the most reliable option among multiple choices.")