#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 18:01:49 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/externals/impact_factor/src/impact_factor/core/journal_matcher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./impact_factor/core/journal_matcher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import re
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from collections import Counter

from scitex.logging import getLogger

logger = getLogger(__name__)


class JournalMatcher:
    """
    Advanced journal matching system for finding journals across different data sources
    
    This class provides sophisticated matching algorithms to identify the same journal
    across OpenAlex, Crossref, and Semantic Scholar databases, accounting for:
    - Name variations and abbreviations
    - Different formatting conventions
    - Publisher-specific naming patterns
    - ISSN matching when available
    """
    
    def __init__(self):
        """Initialize the matcher with common abbreviations and patterns"""
        self.common_abbreviations = {
            'journal': ['j', 'jrnl', 'jour'],
            'international': ['int', 'intl', 'intern'],
            'american': ['am', 'amer'],
            'british': ['br', 'brit'],
            'european': ['eur', 'euro'],
            'proceedings': ['proc', 'proceedings'],
            'transactions': ['trans', 'transaction'],
            'communications': ['comm', 'commun'],
            'letters': ['lett', 'let'],
            'reports': ['rep', 'report'],
            'science': ['sci', 'sc'],
            'technology': ['tech', 'technol'],
            'engineering': ['eng', 'engin'],
            'medicine': ['med', 'medic'],
            'biology': ['bio', 'biol'],
            'chemistry': ['chem', 'chemical'],
            'physics': ['phys', 'physical'],
            'mathematics': ['math', 'mathematical'],
            'computer': ['comp', 'comput'],
            'review': ['rev', 'reviews'],
            'research': ['res', 'research'],
            'applied': ['appl', 'application'],
            'theoretical': ['theor', 'theory'],
            'experimental': ['exp', 'experiment'],
            'clinical': ['clin', 'clinic'],
            'molecular': ['mol', 'molec'],
            'cellular': ['cell', 'cellular']
        }
        
        self.stop_words = {
            'the', 'of', 'and', 'in', 'on', 'for', 'with', 'by', 'at', 'from',
            'to', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being'
        }
    
    def find_best_match(
        self,
        query_journal: str,
        journal_list: List[Dict],
        name_field: str,
        threshold: float = 0.7
    ) -> Optional[Dict]:
        """
        Find the best matching journal from a list
        
        Args:
            query_journal: Journal name to search for
            journal_list: List of journal dictionaries to search in
            name_field: Field name containing the journal name
            threshold: Minimum similarity score (0-1)
            
        Returns:
            Best matching journal dictionary or None
        """
        if not journal_list:
            return None
        
        logger.info(f"Searching for '{query_journal}' in {len(journal_list)} journals")
        
        best_match = None
        best_score = 0.0
        
        normalized_query = self._normalize_name(query_journal)
        
        for journal in journal_list:
            journal_name = journal.get(name_field, '')
            if not journal_name:
                continue
                
            # Try multiple matching strategies
            scores = []
            
            # 1. Exact match (case insensitive)
            if normalized_query.lower() == self._normalize_name(journal_name).lower():
                scores.append(1.0)
            
            # 2. ISSN match (if available)
            issn_score = self._match_issn(query_journal, journal)
            if issn_score > 0:
                scores.append(issn_score)
            
            # 3. Fuzzy string matching
            fuzzy_score = self._fuzzy_match(normalized_query, journal_name)
            scores.append(fuzzy_score)
            
            # 4. Token-based matching
            token_score = self._token_match(normalized_query, journal_name)
            scores.append(token_score)
            
            # 5. Abbreviation-aware matching
            abbrev_score = self._abbreviation_match(normalized_query, journal_name)
            scores.append(abbrev_score)
            
            # Take the maximum score from all strategies
            final_score = max(scores)
            
            if final_score > best_score and final_score >= threshold:
                best_score = final_score
                best_match = journal
                best_match['_match_score'] = final_score
                best_match['_match_field'] = name_field
        
        if best_match:
            logger.info(f"Found match: '{best_match.get(name_field)}' (score: {best_score:.3f})")
        else:
            logger.warning(f"No match found for '{query_journal}' above threshold {threshold}")
        
        return best_match
    
    def _normalize_name(self, name: str) -> str:
        """Normalize journal name for better matching"""
        if not name:
            return ""
        
        # Remove special characters and extra whitespace
        normalized = re.sub(r'[^\w\s-]', ' ', name)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Convert to lowercase for comparison
        return normalized.lower()
    
    def _fuzzy_match(self, query: str, target: str) -> float:
        """Calculate fuzzy string similarity using SequenceMatcher"""
        normalized_target = self._normalize_name(target)
        return SequenceMatcher(None, query.lower(), normalized_target.lower()).ratio()
    
    def _token_match(self, query: str, target: str) -> float:
        """Calculate similarity based on token overlap"""
        query_tokens = set(self._tokenize(query))
        target_tokens = set(self._tokenize(target))
        
        if not query_tokens or not target_tokens:
            return 0.0
        
        intersection = query_tokens.intersection(target_tokens)
        union = query_tokens.union(target_tokens)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _abbreviation_match(self, query: str, target: str) -> float:
        """Match considering common abbreviations"""
        query_expanded = self._expand_abbreviations(query)
        target_expanded = self._expand_abbreviations(target)
        
        # Try both directions
        score1 = SequenceMatcher(None, query_expanded, target_expanded).ratio()
        score2 = SequenceMatcher(None, query, self._expand_abbreviations(target)).ratio()
        score3 = SequenceMatcher(None, self._expand_abbreviations(query), target).ratio()
        
        return max(score1, score2, score3)
    
    def _expand_abbreviations(self, text: str) -> str:
        """Expand common abbreviations in journal names"""
        words = self._tokenize(text)
        expanded_words = []
        
        for word in words:
            word_lower = word.lower()
            expanded = False
            
            # Check if word is an abbreviation
            for full_word, abbrevs in self.common_abbreviations.items():
                if word_lower in abbrevs:
                    expanded_words.append(full_word)
                    expanded = True
                    break
            
            if not expanded:
                # Check if word is a full form that could be abbreviated
                for full_word, abbrevs in self.common_abbreviations.items():
                    if word_lower == full_word:
                        expanded_words.extend([full_word] + abbrevs)
                        expanded = True
                        break
            
            if not expanded:
                expanded_words.append(word)
        
        return ' '.join(expanded_words)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into meaningful words"""
        if not text:
            return []
        
        # Split by whitespace and hyphens
        tokens = re.split(r'[\s\-]+', text.lower())
        
        # Remove stop words and empty tokens
        meaningful_tokens = [
            token for token in tokens 
            if token and token not in self.stop_words and len(token) > 1
        ]
        
        return meaningful_tokens
    
    def _match_issn(self, query: str, journal_dict: Dict) -> float:
        """Match based on ISSN if available"""
        # Extract ISSN from query (if present)
        query_issn = self._extract_issn(query)
        if not query_issn:
            return 0.0
        
        # Check journal dictionary for ISSN fields
        journal_issns = []
        
        # Common ISSN field names
        for field in ['issn', 'issn_l', 'ISSN', 'print_issn', 'online_issn']:
            issn_value = journal_dict.get(field)
            if issn_value:
                if isinstance(issn_value, list):
                    journal_issns.extend(issn_value)
                else:
                    journal_issns.append(issn_value)
        
        # Normalize and compare ISSNs
        query_issn_normalized = self._normalize_issn(query_issn)
        for journal_issn in journal_issns:
            if self._normalize_issn(journal_issn) == query_issn_normalized:
                return 1.0  # Perfect match
        
        return 0.0
    
    def _extract_issn(self, text: str) -> Optional[str]:
        """Extract ISSN from text using regex"""
        # ISSN pattern: XXXX-XXXX
        issn_pattern = r'\b\d{4}-\d{4}\b'
        match = re.search(issn_pattern, text)
        return match.group(0) if match else None
    
    def _normalize_issn(self, issn: str) -> str:
        """Normalize ISSN format"""
        if not issn:
            return ""
        # Remove spaces and convert to standard format
        return re.sub(r'[^\d\-X]', '', str(issn).upper())
    
    def find_multiple_matches(
        self,
        query_journal: str,
        journal_lists: Dict[str, List[Dict]],
        name_fields: Dict[str, str],
        threshold: float = 0.7
    ) -> Dict[str, Optional[Dict]]:
        """
        Find matches across multiple data sources
        
        Args:
            query_journal: Journal name to search for
            journal_lists: Dict of source_name -> journal_list
            name_fields: Dict of source_name -> name_field
            threshold: Minimum similarity score
            
        Returns:
            Dict of source_name -> best_match (or None)
        """
        logger.info(f"Searching for '{query_journal}' across {len(journal_lists)} sources")
        
        matches = {}
        
        for source_name, journal_list in journal_lists.items():
            name_field = name_fields.get(source_name)
            if not name_field:
                logger.warning(f"No name field specified for source '{source_name}'")
                matches[source_name] = None
                continue
            
            match = self.find_best_match(query_journal, journal_list, name_field, threshold)
            matches[source_name] = match
            
            if match:
                logger.info(f"Found match in {source_name}: {match.get(name_field)}")
        
        return matches
    
    def get_match_statistics(self, matches: Dict[str, Optional[Dict]]) -> Dict:
        """Get statistics about matches found"""
        stats = {
            'total_sources': len(matches),
            'sources_with_matches': sum(1 for match in matches.values() if match is not None),
            'match_scores': {},
            'coverage': 0.0
        }
        
        for source, match in matches.items():
            if match and '_match_score' in match:
                stats['match_scores'][source] = match['_match_score']
        
        stats['coverage'] = stats['sources_with_matches'] / stats['total_sources'] if stats['total_sources'] > 0 else 0.0
        
        return stats


def main():
    """Demonstration of JournalMatcher functionality"""
    logger.info("Starting Journal Matcher demonstration")
    
    matcher = JournalMatcher()
    
    # Test data simulating different data sources
    test_journals = {
        'openalex': [
            {'display_name': 'Nature', 'issn': ['0028-0836', '1476-4687']},
            {'display_name': 'Science', 'issn': ['0036-8075', '1095-9203']},
            {'display_name': 'Cell', 'issn': ['0092-8674', '1097-4172']},
            {'display_name': 'The Journal of Biological Chemistry', 'issn': ['0021-9258']},
            {'display_name': 'Proceedings of the National Academy of Sciences', 'issn': ['0027-8424']},
            {'display_name': 'Scientific Reports', 'issn': ['2045-2322']}
        ],
        'crossref': [
            {'title': 'Nature', 'ISSN': ['0028-0836', '1476-4687']},
            {'title': 'Science', 'ISSN': ['0036-8075', '1095-9203']},
            {'title': 'Cell', 'ISSN': ['0092-8674']},
            {'title': 'J. Biol. Chem.', 'ISSN': ['0021-9258']},
            {'title': 'PNAS', 'ISSN': ['0027-8424']},
            {'title': 'Sci Rep', 'ISSN': ['2045-2322']}
        ]
    }
    
    # Test queries with various formats
    test_queries = [
        'Nature',
        'Science',
        'Cell',
        'Journal of Biological Chemistry',
        'Proceedings of the National Academy of Sciences',
        'Scientific Reports',
        'PNAS',
        'J Biol Chem',
        'Sci Rep'
    ]
    
    name_fields = {
        'openalex': 'display_name',
        'crossref': 'title'
    }
    
    logger.info("Testing journal matching across sources")
    logger.info("=" * 50)
    
    for query in test_queries:
        logger.info(f"Searching for: '{query}'")
        
        # Find matches in each source
        matches = matcher.find_multiple_matches(query, test_journals, name_fields)
        
        # Display results
        for source, match in matches.items():
            if match:
                name_field = name_fields[source]
                score = match.get('_match_score', 0.0)
                logger.info(f"  {source}: '{match.get(name_field)}' (score: {score:.3f})")
            else:
                logger.info(f"  {source}: No match found")
        
        # Get statistics
        stats = matcher.get_match_statistics(matches)
        logger.info(f"  Coverage: {stats['coverage']:.1%} ({stats['sources_with_matches']}/{stats['total_sources']} sources)")
        
        logger.info("")
    
    # Test individual matching strategies
    logger.info("Testing individual matching strategies")
    logger.info("=" * 40)
    
    test_pairs = [
        ('Nature', 'Nature'),
        ('Journal of Biological Chemistry', 'J. Biol. Chem.'),
        ('Proceedings of the National Academy of Sciences', 'PNAS'),
        ('Scientific Reports', 'Sci Rep'),
        ('Nature Communications', 'Nat Commun')
    ]
    
    for query, target in test_pairs:
        logger.info(f"Matching '{query}' vs '{target}'")
        
        fuzzy_score = matcher._fuzzy_match(matcher._normalize_name(query), target)
        token_score = matcher._token_match(matcher._normalize_name(query), target)
        abbrev_score = matcher._abbreviation_match(matcher._normalize_name(query), target)
        
        logger.info(f"  Fuzzy score: {fuzzy_score:.3f}")
        logger.info(f"  Token score: {token_score:.3f}")
        logger.info(f"  Abbreviation score: {abbrev_score:.3f}")
        logger.info("")
    
    logger.success("Journal Matcher demonstration completed")


if __name__ == "__main__":
    main()

# EOF