#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 19:00:13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/doi/engines/_EngineRotationManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/engines/_EngineRotationManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Intelligent engine rotation manager for DOI resolution.

This module manages which DOI engines to use based on rate limiting status,
success rates, and paper characteristics to optimize resolution performance.
"""

import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, List

from scitex import log

from ._RateLimitHandler import RateLimitHandler

logger = log.getLogger(__name__)


@dataclass
class EnginePerformance:
    """Track performance metrics for a engine."""

    total_attempts: int = 0
    successful_resolutions: int = 0
    total_response_time: float = 0.0
    recent_success_rate: float = 0.0
    specialty_scores: Dict[str, float] = None

    def __post_init__(self):
        if self.specialty_scores is None:
            self.specialty_scores = {}

    @property
    def overall_success_rate(self) -> float:
        """Calculate overall success rate."""
        if self.total_attempts == 0:
            return 0.0
        return self.successful_resolutions / self.total_attempts

    @property
    def avg_response_time(self) -> float:
        """Calculate average response time."""
        if self.successful_resolutions == 0:
            return float("inf")
        return self.total_response_time / self.successful_resolutions


class EngineRotationManager:
    """Manages intelligent rotation and selection of DOI engines."""

    def __init__(self, rate_limit_handler: RateLimitHandler):
        """Initialize engine rotation manager.

        Args:
            rate_limit_handler: Rate limit handler instance
        """
        self.rate_limit_handler = rate_limit_handler
        self.engine_performance: Dict[str, EnginePerformance] = {}
        self.recent_attempts = deque(
            maxlen=100
        )  # Track recent attempts for adaptive behavior

        # Engine specialties based on observed patterns
        self.engine_specialties = {
            "crossref": {
                "journal_articles": 0.9,
                "conference_papers": 0.7,
                "books": 0.6,
                "general": 0.8,
            },
            "pubmed": {
                "biomedical": 0.95,
                "medical": 0.95,
                "life_sciences": 0.9,
                "journal_articles": 0.8,
                "general": 0.5,
            },
            "semantic_scholar": {
                "computer_science": 0.95,
                "ai_ml": 0.98,
                "conference_papers": 0.9,
                "preprints": 0.8,
                "general": 0.7,
            },
            "openalex": {
                "academic_papers": 0.85,
                "citation_data": 0.9,
                "interdisciplinary": 0.8,
                "general": 0.7,
            },
            "arxiv": {
                "preprints": 0.98,
                "physics": 0.95,
                "mathematics": 0.95,
                "computer_science": 0.9,
                "general": 0.3,
            },
        }

    def get_engine_performance(self, engine: str) -> EnginePerformance:
        """Get or create performance tracker for engine."""
        if engine not in self.engine_performance:
            self.engine_performance[engine] = EnginePerformance()
        return self.engine_performance[engine]

    def record_attempt(
        self,
        engine: str,
        paper_info: Dict,
        success: bool,
        response_time: float = 0.0,
    ):
        """Record an attempt to resolve DOI with a engine.

        Args:
            engine: Engine name
            paper_info: Paper metadata (title, journal, etc.)
            success: Whether resolution was successful
            response_time: Time taken for resolution
        """
        perf = self.get_engine_performance(engine)
        perf.total_attempts += 1

        if success:
            perf.successful_resolutions += 1
            perf.total_response_time += response_time

            # Update specialty scores based on paper type
            paper_type = self._classify_paper(paper_info)
            if paper_type in perf.specialty_scores:
                # Exponential moving average for specialty score
                perf.specialty_scores[paper_type] = (
                    perf.specialty_scores[paper_type] * 0.9 + 1.0 * 0.1
                )
            else:
                perf.specialty_scores[paper_type] = (
                    0.8  # Start with decent score
                )
        else:
            # Reduce specialty scores on failure
            paper_type = self._classify_paper(paper_info)
            if paper_type in perf.specialty_scores:
                perf.specialty_scores[paper_type] *= 0.95

        # Update recent success rate (last 20 attempts)
        recent_attempts_for_engine = [
            attempt
            for attempt in list(self.recent_attempts)[-20:]
            if attempt["engine"] == engine
        ]
        if recent_attempts_for_engine:
            recent_successes = sum(
                1 for a in recent_attempts_for_engine if a["success"]
            )
            perf.recent_success_rate = recent_successes / len(
                recent_attempts_for_engine
            )

        # Record in recent attempts
        self.recent_attempts.append(
            {
                "engine": engine,
                "success": success,
                "paper_type": self._classify_paper(paper_info),
                "timestamp": time.time(),
            }
        )

    def _classify_paper(self, paper_info: Dict) -> str:
        """Classify paper type based on metadata."""
        title = paper_info.get("title", "").lower()
        journal = paper_info.get("journal", "").lower()
        authors = paper_info.get("authors", [])

        # Check for preprints
        preprint_indicators = [
            "arxiv",
            "biorxiv",
            "medrxiv",
            "preprint",
            "submitted",
        ]
        if any(
            indicator in journal or indicator in title
            for indicator in preprint_indicators
        ):
            return "preprints"

        # Check for biomedical/medical
        biomedical_terms = [
            "medicine",
            "medical",
            "biology",
            "biomedical",
            "clinical",
            "health",
            "disease",
            "therapy",
            "treatment",
            "patient",
            "cell",
            "molecular",
            "genetics",
            "pharmaceutical",
            "drug",
        ]
        if any(term in title or term in journal for term in biomedical_terms):
            return "biomedical"

        # Check for computer science/AI
        cs_terms = [
            "computer",
            "computing",
            "algorithm",
            "machine learning",
            "artificial intelligence",
            "neural network",
            "deep learning",
            "data science",
            "software",
            "programming",
        ]
        if any(term in title or term in journal for term in cs_terms):
            return "computer_science"

        # Check for physics/mathematics
        physics_terms = [
            "physics",
            "quantum",
            "relativity",
            "particle",
            "cosmology",
        ]
        math_terms = [
            "mathematics",
            "mathematical",
            "theorem",
            "proof",
            "algebra",
        ]
        if any(term in title or term in journal for term in physics_terms):
            return "physics"
        if any(term in title or term in journal for term in math_terms):
            return "mathematics"

        # Check for conference papers
        conference_indicators = [
            "proceedings",
            "conference",
            "workshop",
            "symposium",
            "ieee",
            "acm",
        ]
        if any(indicator in journal for indicator in conference_indicators):
            return "conference_papers"

        # Default classification
        return "journal_articles"

    def get_optimal_engine_order(
        self,
        paper_info: Dict,
        available_engines: List[str],
        max_engines: int = 3,
    ) -> List[str]:
        """Get optimal order of engines to try for a paper.

        Args:
            paper_info: Paper metadata
            available_engines: List of available (non-rate-limited) engines
            max_engines: Maximum number of engines to return

        Returns:
            List of engine names in optimal order
        """
        if not available_engines:
            return []

        paper_type = self._classify_paper(paper_info)

        # Calculate scores for each available engine
        engine_scores = []
        for engine in available_engines:
            score = self._calculate_engine_score(
                engine, paper_type, paper_info
            )
            engine_scores.append((engine, score))

        # Sort by score (descending) and take top max_engines
        engine_scores.sort(key=lambda x: x[1], reverse=True)
        optimal_engines = [engine for engine, _ in engine_scores[:max_engines]]

        logger.debug(
            f"Optimal engine order for {paper_type}: {optimal_engines} "
            f"(scores: {[f'{s}:{score:.2f}' for s, score in engine_scores[:max_engines]]})"
        )

        return optimal_engines

    def _calculate_engine_score(
        self, engine: str, paper_type: str, paper_info: Dict
    ) -> float:
        """Calculate a score for how suitable a engine is for a paper.

        Higher scores indicate better suitability.
        """
        perf = self.get_engine_performance(engine)
        rate_limit_state = self.rate_limit_handler.get_engine_state(engine)

        # Base score from engine specialties
        base_score = self.engine_specialties.get(engine, {}).get(
            paper_type, 0.5
        )

        # Adjust for learned performance
        performance_factor = 1.0
        if perf.total_attempts > 5:  # Only consider if we have enough data
            # Combine overall and recent success rates
            overall_rate = perf.overall_success_rate
            recent_rate = perf.recent_success_rate
            combined_rate = (overall_rate * 0.3) + (
                recent_rate * 0.7
            )  # Favor recent performance
            performance_factor = combined_rate

        # Adjust for specialty performance if we have learned data
        specialty_factor = 1.0
        if paper_type in perf.specialty_scores:
            specialty_factor = perf.specialty_scores[paper_type]

        # Adjust for response time (faster is better)
        speed_factor = 1.0
        if perf.avg_response_time != float("inf"):
            # Normalize response time (1-10 seconds is good, >30 seconds is slow)
            normalized_time = min(perf.avg_response_time / 10.0, 3.0)
            speed_factor = max(0.3, 1.0 - (normalized_time - 1.0) * 0.2)

        # Penalty for rate limiting
        rate_limit_factor = 1.0
        if rate_limit_state.is_rate_limited:
            rate_limit_factor = 0.1  # Heavy penalty for rate limited engines
        elif rate_limit_state.consecutive_failures > 0:
            # Gradual penalty for recent failures
            rate_limit_factor = max(
                0.5, 1.0 - (rate_limit_state.consecutive_failures * 0.1)
            )

        # Bonus for engines that haven't been used recently (avoid overloading)
        recency_factor = 1.0
        current_time = time.time()
        time_since_last = current_time - rate_limit_state.last_success
        if time_since_last > 300:  # 5 minutes
            recency_factor = min(
                1.2, 1.0 + (time_since_last / 3600)
            )  # Bonus up to 20%

        # Calculate final score
        final_score = (
            base_score
            * performance_factor
            * specialty_factor
            * speed_factor
            * rate_limit_factor
            * recency_factor
        )

        return final_score

    def should_rotate_engines(
        self, current_failures: int, total_attempts: int
    ) -> bool:
        """Determine if we should rotate to different engines.

        Args:
            current_failures: Number of consecutive failures
            total_attempts: Total attempts made so far

        Returns:
            True if engines should be rotated
        """
        # Rotate after too many failures
        if current_failures >= 3:
            return True

        # Rotate if overall success rate is too low
        if total_attempts >= 10:
            recent_success_rate = self._calculate_recent_success_rate()
            if recent_success_rate < 0.3:
                return True

        return False

    def _calculate_recent_success_rate(self, window_size: int = 20) -> float:
        """Calculate success rate from recent attempts."""
        recent = list(self.recent_attempts)[-window_size:]
        if not recent:
            return 0.5  # Default rate

        successes = sum(1 for attempt in recent if attempt["success"])
        return successes / len(recent)

    def get_fallback_engines(
        self, tried_engines: List[str], all_engines: List[str]
    ) -> List[str]:
        """Get fallback engines when primary engines fail.

        Args:
            tried_engines: Engines that were originally tried
            all_engines: All available engine names

        Returns:
            List of fallback engines to try
        """
        # Get engines not yet tried
        untried_engines = [s for s in all_engines if s not in tried_engines]

        # Filter by availability
        available_fallbacks = self.rate_limit_handler.get_available_engines(
            untried_engines
        )

        # Sort by general performance
        fallback_scores = []
        for engine in available_fallbacks:
            perf = self.get_engine_performance(engine)
            # Use overall success rate for fallbacks
            score = (
                perf.overall_success_rate if perf.total_attempts > 0 else 0.5
            )
            fallback_scores.append((engine, score))

        fallback_scores.sort(key=lambda x: x[1], reverse=True)
        return [engine for engine, _ in fallback_scores]

    def get_statistics(self) -> Dict:
        """Get engine rotation statistics."""
        stats = {
            "total_engines": len(self.engine_performance),
            "total_attempts": sum(
                p.total_attempts for p in self.engine_performance.values()
            ),
            "overall_success_rate": 0.0,
            "recent_success_rate": self._calculate_recent_success_rate(),
            "engine_details": {},
        }

        # Calculate overall success rate
        total_attempts = stats["total_attempts"]
        total_successes = sum(
            p.successful_resolutions for p in self.engine_performance.values()
        )
        if total_attempts > 0:
            stats["overall_success_rate"] = total_successes / total_attempts

        # Engine-specific details
        for engine, perf in self.engine_performance.items():
            rate_limit_state = self.rate_limit_handler.get_engine_state(engine)
            stats["engine_details"][engine] = {
                "attempts": perf.total_attempts,
                "successes": perf.successful_resolutions,
                "success_rate": perf.overall_success_rate,
                "recent_success_rate": perf.recent_success_rate,
                "avg_response_time": perf.avg_response_time,
                "is_rate_limited": rate_limit_state.is_rate_limited,
                "specialty_scores": dict(perf.specialty_scores),
            }

        return stats


if __name__ == "__main__":
    import asyncio
    from pathlib import Path

    async def test_engine_rotation_manager():
        """Test the engine rotation manager functionality."""
        print("=" * 60)
        print("EngineRotationManager Test")
        print("=" * 60)

        # Create rate limit handler and rotation manager
        state_file = Path("/tmp/test_engine_rotation.json")
        rate_handler = RateLimitHandler()
        rotation_manager = EngineRotationManager(rate_handler)

        print("✅ EngineRotationManager initialized")

        # Test paper classification
        print("\n1. Testing paper classification:")
        test_papers = [
            {
                "title": "Deep Learning for Computer Vision",
                "journal": "IEEE Transactions",
            },
            {
                "title": "Clinical Trial of New Cancer Treatment",
                "journal": "Nature Medicine",
            },
            {
                "title": "Quantum Computing Algorithm",
                "journal": "arXiv preprint",
            },
            {
                "title": "Mathematical Proof of Fermat's Theorem",
                "journal": "Journal of Mathematics",
            },
        ]

        for paper in test_papers:
            paper_type = rotation_manager._classify_paper(paper)
            print(f"   '{paper['title'][:30]}...' -> {paper_type}")

        # Test engine scoring
        print("\n2. Testing engine scoring:")
        cs_paper = {
            "title": "Machine Learning in Healthcare",
            "journal": "AI Conference",
        }
        available_engines = ["crossref", "semantic_scholar", "pubmed"]

        optimal_order = rotation_manager.get_optimal_engine_order(
            cs_paper, available_engines, max_engines=3
        )
        print(f"   Optimal order for CS paper: {optimal_order}")

        # Simulate some attempts
        print("\n3. Simulating resolution attempts:")
        attempts = [
            ("semantic_scholar", cs_paper, True, 2.5),
            ("crossref", cs_paper, False, 5.0),
            ("pubmed", cs_paper, True, 3.2),
            ("semantic_scholar", cs_paper, True, 1.8),
        ]

        for engine, paper, success, time_taken in attempts:
            rotation_manager.record_attempt(engine, paper, success, time_taken)
            status = "✅" if success else "❌"
            print(f"   {status} {engine}: {time_taken:.1f}s")

        # Test updated engine order after learning
        print("\n4. Updated engine order after learning:")
        new_optimal_order = rotation_manager.get_optimal_engine_order(
            cs_paper, available_engines, max_engines=3
        )
        print(f"   New optimal order: {new_optimal_order}")

        # Test fallback engines
        print("\n5. Testing fallback engines:")
        all_engines = [
            "crossref",
            "semantic_scholar",
            "pubmed",
            "openalex",
            "arxiv",
        ]
        failed_engines = ["crossref", "semantic_scholar"]
        fallbacks = rotation_manager.get_fallback_engines(
            failed_engines, all_engines
        )
        print(f"   Fallback engines after {failed_engines}: {fallbacks}")

        # Show statistics
        print("\n6. Statistics:")
        stats = rotation_manager.get_statistics()
        print(f"   Total attempts: {stats['total_attempts']}")
        print(f"   Overall success rate: {stats['overall_success_rate']:.2f}")
        print(f"   Recent success rate: {stats['recent_success_rate']:.2f}")

        for engine, details in stats["engine_details"].items():
            print(
                f"   {engine}: {details['successes']}/{details['attempts']} "
                f"({details['success_rate']:.2f}) - {details['avg_response_time']:.1f}s avg"
            )

        print("\n✅ EngineRotationManager test completed!")

        # Cleanup
        if state_file.exists():
            state_file.unlink()

    asyncio.run(test_engine_rotation_manager())

# python -m scitex.scholar.engines.individual._EngineRotationManager

# EOF
