#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-03 01:56:15 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/metrics/_calc_seizure_prediction_metrics.py
"""Calculate clinical seizure prediction metrics.

This module provides both window-based and event-based seizure prediction metrics
following FDA/clinical guidelines.

Two Approaches:
  1. Window-based: Measures % of seizure time windows detected
  2. Event-based: Measures % of seizure events detected (≥1 alarm per event)

Key Metrics:
  - seizure_sensitivity: % detected (interpretation depends on window vs event-based)
  - fp_per_hour: False positives per hour during interictal periods
  - time_in_warning: % of total time in alarm state

Clinical Targets (FDA guidelines):
  - Sensitivity ≥ 90%
  - FP/h ≤ 0.2
  - Time in warning ≤ 20%
"""
from __future__ import annotations
from typing import Dict
import numpy as np
import pandas as pd


def calc_seizure_window_prediction_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    metadata: pd.DataFrame,
    window_duration_min: float = 1.0,
) -> Dict[str, float]:
    """Calculate clinical seizure prediction metrics (window-based).

    This function calculates window-based sensitivity, meaning it measures
    the percentage of seizure time windows that were correctly identified.
    This is NOT event-based sensitivity (which would measure % of seizure
    events detected regardless of how many windows within each event).

    Parameters
    ----------
    y_true : np.ndarray
        True labels (string: 'seizure' or 'interictal_control')
    y_pred : np.ndarray
        Predicted labels (string: 'seizure' or 'interictal_control')
    metadata : pd.DataFrame
        Metadata with 'seizure_type' column indicating seizure/interictal periods
    window_duration_min : float, optional
        Duration of each time window in minutes (default: 1.0)

    Returns
    -------
    Dict[str, float]
        Dictionary containing:
        - seizure_sensitivity: % of seizure *time windows* detected (NOT event-based)
        - fp_per_hour: False positives per hour during interictal periods
        - time_in_warning: % of total time in alarm state
        - n_seizure_windows: Number of seizure windows
        - n_interictal_windows: Number of interictal windows
        - n_true_positives: Correctly predicted seizure windows
        - n_false_positives: Incorrectly predicted as seizure
        - n_false_negatives: Missed seizure windows
        - n_true_negatives: Correctly predicted as interictal
        - meets_sensitivity_target: Whether sensitivity ≥ 90%
        - meets_fp_target: Whether FP/h ≤ 0.2
        - meets_tiw_target: Whether time in warning ≤ 20%

    Notes
    -----
    - False positives are calculated only during interictal periods
    - True positives/false negatives are calculated only during seizure periods
    - Clinical targets based on FDA guidance for seizure prediction devices
    - For event-based sensitivity, use calc_seizure_event_prediction_metrics instead

    Example
    -------
    >>> # 1 seizure spanning 20 windows, detect 5 windows
    >>> # Window-based sensitivity: 5/20 = 25%
    >>> # This measures temporal coverage of the seizure

    References
    ----------
    FDA guidance on seizure prediction devices
    """
    # Create masks for seizure and interictal periods
    seizure_mask = metadata["seizure_type"] == "seizure"
    interictal_mask = metadata["seizure_type"] == "interictal_control"

    # Convert string labels to binary for calculations
    y_true_bin = (y_true == "seizure").astype(int)
    y_pred_bin = (y_pred == "seizure").astype(int)

    # True positives (seizure windows correctly identified)
    tp = np.sum((y_true_bin == 1) & (y_pred_bin == 1) & seizure_mask)

    # False negatives (seizure windows missed)
    fn = np.sum((y_true_bin == 1) & (y_pred_bin == 0) & seizure_mask)

    # False positives (interictal windows incorrectly alarmed)
    fp = np.sum((y_true_bin == 0) & (y_pred_bin == 1) & interictal_mask)

    # True negatives (interictal windows correctly identified)
    tn = np.sum((y_true_bin == 0) & (y_pred_bin == 0) & interictal_mask)

    # Sensitivity (seizure detection rate) - WINDOW-BASED
    n_seizures = seizure_mask.sum()
    seizure_sensitivity = (tp / n_seizures * 100) if n_seizures > 0 else 0.0

    # False positives per hour
    n_interictal = interictal_mask.sum()
    total_interictal_hours = (n_interictal * window_duration_min) / 60.0
    fp_per_hour = (
        fp / total_interictal_hours if total_interictal_hours > 0 else 0.0
    )

    # Time in warning (% of total time in alarm state)
    total_windows = len(y_pred)
    alarm_windows = np.sum(y_pred_bin == 1)
    time_in_warning = (
        (alarm_windows / total_windows * 100) if total_windows > 0 else 0.0
    )

    metrics = {
        # Primary prediction metrics
        "seizure_sensitivity": round(seizure_sensitivity, 3),
        "fp_per_hour": round(fp_per_hour, 3),
        "time_in_warning": round(time_in_warning, 3),
        # Counts (time windows, not events)
        "n_seizure_windows": int(n_seizures),
        "n_interictal_windows": int(n_interictal),
        "n_true_positives": int(tp),
        "n_false_positives": int(fp),
        "n_false_negatives": int(fn),
        "n_true_negatives": int(tn),
        # Clinical targets (FDA/clinical guidelines)
        "meets_sensitivity_target": bool(seizure_sensitivity >= 90.0),
        "meets_fp_target": bool(fp_per_hour <= 0.2),
        "meets_tiw_target": bool(time_in_warning <= 20.0),
    }

    return metrics


def calc_seizure_event_prediction_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    metadata: pd.DataFrame,
    window_duration_min: float = 1.0,
) -> Dict[str, float]:
    """Calculate clinical seizure prediction metrics (event-based).

    This function calculates event-based sensitivity, meaning it measures
    whether each seizure EVENT was detected (at least one alarm raised),
    regardless of how many windows within that event were predicted.

    This is clinically more relevant as one timely alarm per seizure event
    is sufficient for intervention, matching the clinical requirement:
    "Did the system raise an alarm for this seizure?"

    Parameters
    ----------
    y_true : np.ndarray
        True labels (string: 'seizure' or 'interictal_control')
    y_pred : np.ndarray
        Predicted labels (string: 'seizure' or 'interictal_control')
    metadata : pd.DataFrame
        Metadata with 'seizure_type' and 'seizure_id' columns.
        seizure_id: Unique identifier for each seizure event (e.g., 'sz_001', 'sz_002')
                   Should be NaN or empty for interictal periods
    window_duration_min : float, optional
        Duration of each time window in minutes (default: 1.0)

    Returns
    -------
    Dict[str, float]
        Dictionary containing:
        - seizure_sensitivity: % of seizure *events* detected (event-based)
        - fp_per_hour: False positives per hour during interictal periods
        - time_in_warning: % of total time in alarm state
        - n_seizure_events: Number of unique seizure events
        - n_detected_events: Number of events with at least one alarm
        - n_missed_events: Number of events with zero alarms
        - n_interictal_windows: Number of interictal windows
        - n_false_positives: Incorrectly predicted as seizure
        - n_true_negatives: Correctly predicted as interictal
        - meets_sensitivity_target: Whether sensitivity ≥ 90%
        - meets_fp_target: Whether FP/h ≤ 0.2
        - meets_tiw_target: Whether time in warning ≤ 20%

    Notes
    -----
    - Requires 'seizure_id' column in metadata to group windows by event
    - False positives are calculated only during interictal periods
    - Event detection requires at least one window predicted as seizure
    - Clinical targets based on FDA guidance for seizure prediction devices
    - For window-based sensitivity, use calc_seizure_window_prediction_metrics instead

    Example
    -------
    >>> # 1 seizure spanning 20 windows, detect just 1 window
    >>> # Event-based sensitivity: 1/1 = 100% (event was detected!)
    >>> # This measures "did we catch the seizure at all?"

    References
    ----------
    FDA guidance on seizure prediction devices
    """
    # Validate required column
    if "seizure_id" not in metadata.columns:
        raise ValueError(
            "metadata must contain 'seizure_id' column for event-based metrics. "
            "Use calc_seizure_window_prediction_metrics for window-based metrics."
        )

    # Create masks
    seizure_mask = metadata["seizure_type"] == "seizure"
    interictal_mask = metadata["seizure_type"] == "interictal_control"

    # Convert string labels to binary
    y_true_bin = (y_true == "seizure").astype(int)
    y_pred_bin = (y_pred == "seizure").astype(int)

    # Event-based sensitivity calculation
    # Group by seizure_id and check if any window in that event was predicted
    seizure_events = metadata[seizure_mask]["seizure_id"].unique()
    n_seizure_events = len(seizure_events)

    detected_events = 0
    for event_id in seizure_events:
        event_mask = (metadata["seizure_id"] == event_id).values
        # Check if at least one window in this event was predicted as seizure
        event_predictions = y_pred_bin[event_mask]
        if np.any(event_predictions == 1):
            detected_events += 1

    missed_events = n_seizure_events - detected_events

    # Event-based sensitivity: % of events detected
    seizure_sensitivity = (
        (detected_events / n_seizure_events * 100) if n_seizure_events > 0 else 0.0
    )

    # False positives (interictal windows incorrectly alarmed)
    fp = np.sum((y_true_bin == 0) & (y_pred_bin == 1) & interictal_mask)

    # True negatives (interictal windows correctly identified)
    tn = np.sum((y_true_bin == 0) & (y_pred_bin == 0) & interictal_mask)

    # False positives per hour
    n_interictal = interictal_mask.sum()
    total_interictal_hours = (n_interictal * window_duration_min) / 60.0
    fp_per_hour = (
        fp / total_interictal_hours if total_interictal_hours > 0 else 0.0
    )

    # Time in warning (% of total time in alarm state)
    total_windows = len(y_pred)
    alarm_windows = np.sum(y_pred_bin == 1)
    time_in_warning = (
        (alarm_windows / total_windows * 100) if total_windows > 0 else 0.0
    )

    metrics = {
        # Primary prediction metrics
        "seizure_sensitivity": round(seizure_sensitivity, 3),
        "fp_per_hour": round(fp_per_hour, 3),
        "time_in_warning": round(time_in_warning, 3),
        # Counts (events, not windows)
        "n_seizure_events": int(n_seizure_events),
        "n_detected_events": int(detected_events),
        "n_missed_events": int(missed_events),
        "n_interictal_windows": int(n_interictal),
        "n_false_positives": int(fp),
        "n_true_negatives": int(tn),
        # Clinical targets (FDA/clinical guidelines)
        "meets_sensitivity_target": bool(seizure_sensitivity >= 90.0),
        "meets_fp_target": bool(fp_per_hour <= 0.2),
        "meets_tiw_target": bool(time_in_warning <= 20.0),
    }

    return metrics


# Backward compatibility aliases
calc_seizure_prediction_metrics = calc_seizure_window_prediction_metrics
calculate_seizure_prediction_metrics = calc_seizure_window_prediction_metrics


def parse_args():
    """Parse command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Demonstrate seizure prediction metrics calculation"
    )
    parser.add_argument(
        "--n-windows",
        type=int,
        default=1000,
        help="Number of time windows to simulate (default: %(default)s)",
    )
    parser.add_argument(
        "--window-duration",
        type=float,
        default=1.0,
        help="Duration of each window in minutes (default: %(default)s)",
    )
    parser.add_argument(
        "--sensitivity",
        type=float,
        default=0.9,
        help="Target sensitivity to simulate (default: %(default)s)",
    )
    args = parser.parse_args()
    return args


def main(args):
    """Demonstrate seizure prediction metrics with synthetic data."""
    from scitex import logging

    logger = logging.getLogger(__name__)

    logger.info("Creating synthetic seizure prediction data")
    logger.info(f"  n_windows: {args.n_windows}")
    logger.info(f"  window_duration: {args.window_duration} min")
    logger.info(f"  target_sensitivity: {args.sensitivity * 100}%")

    # Create synthetic test data
    n_windows = args.n_windows
    window_duration_min = args.window_duration

    # Create labels and metadata with seizure_id for event-based metrics
    y_true = np.array(["interictal_control"] * n_windows)
    y_pred = np.array(["interictal_control"] * n_windows)
    metadata = pd.DataFrame({
        "seizure_type": ["interictal_control"] * n_windows,
        "seizure_id": [None] * n_windows  # seizure_id for event-based metrics
    })

    # Add TWO seizure events (event 1: 100-119, event 2: 500-529)
    event1_indices = list(range(100, 120))  # 20 windows
    event2_indices = list(range(500, 530))  # 30 windows
    seizure_indices = event1_indices + event2_indices

    y_true[event1_indices] = "seizure"
    y_true[event2_indices] = "seizure"
    metadata.loc[event1_indices, "seizure_type"] = "seizure"
    metadata.loc[event1_indices, "seizure_id"] = "sz_001"
    metadata.loc[event2_indices, "seizure_type"] = "seizure"
    metadata.loc[event2_indices, "seizure_id"] = "sz_002"

    logger.info(f"Created 2 seizure events spanning {len(seizure_indices)} windows total")
    logger.info(f"  Event 1 (sz_001): 20 windows")
    logger.info(f"  Event 2 (sz_002): 30 windows")

    # Predict some seizures correctly based on target sensitivity
    # For event-based demo: detect only 1 window from event 1, most of event 2
    n_detect = int(len(seizure_indices) * args.sensitivity)
    # Detect 1 window from event 1, rest from event 2
    detected_indices = [event1_indices[0]] + event2_indices[:n_detect-1]
    y_pred[detected_indices] = "seizure"

    logger.info(f"Simulating detection of {n_detect}/{len(seizure_indices)} seizure windows")
    logger.info(f"  Event 1: 1/20 windows detected")
    logger.info(f"  Event 2: {n_detect-1}/30 windows detected")

    # Add some false positives
    fp_indices = [200, 300, 400, 600, 700]
    y_pred[fp_indices] = "seizure"

    logger.info(f"Added {len(fp_indices)} false positive alarms")

    # Calculate WINDOW-BASED metrics
    logger.info("")
    logger.info("Calculating WINDOW-BASED seizure prediction metrics")
    metrics_window = calc_seizure_window_prediction_metrics(
        y_true, y_pred, metadata, window_duration_min
    )

    # Print window-based results
    logger.info("=" * 70)
    logger.info("WINDOW-BASED Metrics (How well did we cover seizure duration?)")
    logger.info("=" * 70)
    logger.info(f"Seizure Sensitivity: {metrics_window['seizure_sensitivity']:.1f}%")
    logger.info(f"False Positives/Hour: {metrics_window['fp_per_hour']:.3f}")
    logger.info(f"Time in Warning: {metrics_window['time_in_warning']:.1f}%")
    logger.info("")
    logger.info("Counts:")
    logger.info(f"  Seizure windows: {metrics_window['n_seizure_windows']}")
    logger.info(f"  Interictal windows: {metrics_window['n_interictal_windows']}")
    logger.info(f"  True positives: {metrics_window['n_true_positives']}")
    logger.info(f"  False positives: {metrics_window['n_false_positives']}")
    logger.info(f"  False negatives: {metrics_window['n_false_negatives']}")
    logger.info(f"  True negatives: {metrics_window['n_true_negatives']}")
    logger.info("")
    logger.info("Clinical Targets (FDA Guidelines):")
    logger.info(
        f"  Meets sensitivity target (≥90%): {metrics_window['meets_sensitivity_target']}"
    )
    logger.info(f"  Meets FP/h target (≤0.2): {metrics_window['meets_fp_target']}")
    logger.info(f"  Meets time in warning target (≤20%): {metrics_window['meets_tiw_target']}")
    logger.info("=" * 70)

    # Calculate EVENT-BASED metrics
    logger.info("")
    logger.info("Calculating EVENT-BASED seizure prediction metrics")
    metrics_event = calc_seizure_event_prediction_metrics(
        y_true, y_pred, metadata, window_duration_min
    )

    # Print event-based results
    logger.info("=" * 70)
    logger.info("EVENT-BASED Metrics (Did we detect each seizure event?)")
    logger.info("=" * 70)
    logger.info(f"Seizure Sensitivity: {metrics_event['seizure_sensitivity']:.1f}%")
    logger.info(f"False Positives/Hour: {metrics_event['fp_per_hour']:.3f}")
    logger.info(f"Time in Warning: {metrics_event['time_in_warning']:.1f}%")
    logger.info("")
    logger.info("Counts:")
    logger.info(f"  Seizure events: {metrics_event['n_seizure_events']}")
    logger.info(f"  Detected events: {metrics_event['n_detected_events']}")
    logger.info(f"  Missed events: {metrics_event['n_missed_events']}")
    logger.info(f"  Interictal windows: {metrics_event['n_interictal_windows']}")
    logger.info(f"  False positives: {metrics_event['n_false_positives']}")
    logger.info(f"  True negatives: {metrics_event['n_true_negatives']}")
    logger.info("")
    logger.info("Clinical Targets (FDA Guidelines):")
    logger.info(
        f"  Meets sensitivity target (≥90%): {metrics_event['meets_sensitivity_target']}"
    )
    logger.info(f"  Meets FP/h target (≤0.2): {metrics_event['meets_fp_target']}")
    logger.info(f"  Meets time in warning target (≤20%): {metrics_event['meets_tiw_target']}")
    logger.info("=" * 70)

    # Comparison summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("KEY DIFFERENCE DEMONSTRATION")
    logger.info("=" * 70)
    logger.info(f"Window-based sensitivity: {metrics_window['seizure_sensitivity']:.1f}% (detected {metrics_window['n_true_positives']}/{metrics_window['n_seizure_windows']} windows)")
    logger.info(f"Event-based sensitivity:  {metrics_event['seizure_sensitivity']:.1f}% (detected {metrics_event['n_detected_events']}/{metrics_event['n_seizure_events']} events)")
    logger.info("")
    logger.info("Interpretation:")
    logger.info("  - Window-based: Detected only 1 window from Event 1 → Low sensitivity")
    logger.info("  - Event-based: Detected at least 1 window from BOTH events → 100% sensitivity!")
    logger.info("  - Clinical relevance: One timely alarm per seizure is sufficient")
    logger.info("=" * 70)

    return 0


def run_main():
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys
    import matplotlib.pyplot as plt
    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__file__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
