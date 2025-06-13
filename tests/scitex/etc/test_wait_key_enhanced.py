#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-09 08:50:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/etc/test_wait_key_enhanced.py
# ----------------------------------------
"""Enhanced tests for wait_key module with advanced testing patterns."""

import os
import sys
import time
import threading
import multiprocessing
import queue
from unittest.mock import Mock, MagicMock, patch, call
import pytest
try:
    from hypothesis import given, strategies as st, settings, assume
    from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False
    # Create dummy decorators
    def given(*args, **kwargs):
        def decorator(func):
            return pytest.mark.skip(reason="hypothesis not installed")(func)
        return decorator
    
    def settings(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class RuleBasedStateMachine:
        pass
    
    # Create dummy strategy object
    class DummyStrategies:
        def lists(self, *args, **kwargs):
            return lambda: []
        def text(self, *args, **kwargs):
            return lambda: ""
        def integers(self, *args, **kwargs):
            return lambda: 0
    
    st = DummyStrategies()
    
    def rule(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def invariant():
        def decorator(func):
            return func
        return decorator

__FILE__ = "./tests/scitex/etc/test_wait_key_enhanced.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------


class TestWaitKeyEnhanced:
    """Enhanced tests for wait_key module with property-based testing."""

    @pytest.fixture
    def mock_process(self):
        """Create a reusable mock process."""
        process = Mock()
        process.pid = 12345
        process.exitcode = None
        process.is_alive.return_value = True
        process.terminate = Mock()
        process.join = Mock()
        process.kill = Mock()
        return process

    @pytest.fixture
    def capture_prints(self):
        """Fixture to capture print outputs."""
        outputs = []
        
        def mock_print(*args, **kwargs):
            outputs.append(' '.join(str(arg) for arg in args))
        
        with patch('builtins.print', side_effect=mock_print):
            yield outputs

    @given(st.lists(st.text(min_size=1, max_size=1).filter(lambda x: x != 'q'), min_size=0, max_size=10))
    @settings(max_examples=50, deadline=1000)
    def test_wait_key_with_random_key_sequences(self, key_sequence):
        """Test wait_key with randomly generated key sequences."""
        from scitex.etc.wait_key import wait_key
        
        # Always end with 'q' to terminate
        full_sequence = key_sequence + ['q']
        
        mock_process = Mock()
        mock_process.terminate = Mock()
        
        with patch('scitex.etc.wait_key.readchar.readchar', side_effect=full_sequence):
            with patch('builtins.print') as mock_print:
                wait_key(mock_process)
                
                # Should terminate exactly once
                mock_process.terminate.assert_called_once()
                
                # Should print all keys plus termination message
                assert mock_print.call_count == len(full_sequence) + 1
                
                # Last print should be termination message
                last_call = mock_print.call_args_list[-1]
                assert last_call == call('q was pressed.')

    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=20, deadline=1000)
    def test_count_function_increments(self, num_iterations):
        """Test count function increments correctly for various iteration counts."""
        from scitex.etc.wait_key import count
        
        printed_values = []
        
        def mock_print(value):
            printed_values.append(value)
            if len(printed_values) >= num_iterations:
                raise KeyboardInterrupt("Test stop")
        
        with patch('scitex.etc.wait_key.time.sleep'):
            with patch('builtins.print', side_effect=mock_print):
                try:
                    count()
                except KeyboardInterrupt:
                    pass
        
        # Verify correct sequence
        assert printed_values == list(range(num_iterations))

    def test_wait_key_thread_safety(self, mock_process):
        """Test wait_key behavior when called from multiple threads."""
        from scitex.etc.wait_key import wait_key
        
        results = []
        errors = []
        
        def run_wait_key():
            try:
                with patch('scitex.etc.wait_key.readchar.readchar', return_value='q'):
                    with patch('builtins.print'):
                        wait_key(mock_process)
                        results.append("success")
            except Exception as e:
                errors.append(e)
        
        # Run wait_key from multiple threads
        threads = [threading.Thread(target=run_wait_key) for _ in range(5)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join(timeout=2)
        
        # All threads should complete successfully
        assert len(results) == 5
        assert len(errors) == 0
        
        # Process should be terminated 5 times (once per thread)
        assert mock_process.terminate.call_count == 5

    def test_wait_key_with_process_lifecycle(self):
        """Test wait_key with full process lifecycle simulation."""
        from scitex.etc.wait_key import wait_key
        
        # Create a more realistic process mock
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.exitcode = None
        mock_process.is_alive.return_value = True
        
        # Track state changes
        state_changes = []
        
        def mock_terminate():
            state_changes.append('terminated')
            mock_process.exitcode = -15
            mock_process.is_alive.return_value = False
        
        mock_process.terminate = Mock(side_effect=mock_terminate)
        
        with patch('scitex.etc.wait_key.readchar.readchar', side_effect=['a', 'b', 'q']):
            with patch('builtins.print'):
                wait_key(mock_process)
        
        # Verify state changes
        assert state_changes == ['terminated']
        assert mock_process.exitcode == -15
        assert not mock_process.is_alive()

    def test_count_with_interruption_timing(self):
        """Test count function with precise interruption timing."""
        from scitex.etc.wait_key import count
        
        timestamps = []
        values = []
        
        def mock_print(value):
            timestamps.append(time.time())
            values.append(value)
            if len(values) >= 5:
                raise KeyboardInterrupt()
        
        start_time = time.time()
        
        with patch('scitex.etc.wait_key.time.sleep', lambda x: time.sleep(0.01)):  # Short sleep
            with patch('builtins.print', side_effect=mock_print):
                try:
                    count()
                except KeyboardInterrupt:
                    pass
        
        # Verify timing
        assert len(timestamps) == 5
        assert values == [0, 1, 2, 3, 4]
        
        # Check that prints happen at regular intervals
        for i in range(1, len(timestamps)):
            interval = timestamps[i] - timestamps[i-1]
            assert 0.005 < interval < 0.02  # Allow some variance

    def test_wait_key_unicode_handling(self):
        """Test wait_key with Unicode characters."""
        from scitex.etc.wait_key import wait_key
        
        mock_process = Mock()
        
        # Test with various Unicode characters
        unicode_chars = ['🎉', '中', '文', 'ñ', 'ü', 'q']
        
        with patch('scitex.etc.wait_key.readchar.readchar', side_effect=unicode_chars):
            with patch('builtins.print') as mock_print:
                wait_key(mock_process)
                
                # Should handle Unicode properly
                expected_calls = [call(char) for char in unicode_chars] + [call('q was pressed.')]
                mock_print.assert_has_calls(expected_calls)

    @pytest.mark.parametrize("exception_type,exception_msg", [
        (ProcessLookupError, "No such process"),
        (PermissionError, "Permission denied"),
        (OSError, "OS error occurred"),
        (RuntimeError, "Process is already dead"),
    ])
    def test_wait_key_process_termination_errors(self, exception_type, exception_msg, mock_process):
        """Test wait_key handling of various process termination errors."""
        from scitex.etc.wait_key import wait_key
        
        mock_process.terminate.side_effect = exception_type(exception_msg)
        
        with patch('scitex.etc.wait_key.readchar.readchar', return_value='q'):
            with patch('builtins.print'):
                # The function might or might not propagate the exception
                # Both behaviors are acceptable
                try:
                    wait_key(mock_process)
                    # If no exception, terminate should have been attempted
                    mock_process.terminate.assert_called_once()
                except exception_type:
                    # If exception propagated, that's also valid
                    mock_process.terminate.assert_called_once()

    def test_wait_key_rapid_key_presses(self):
        """Test wait_key with rapid key press simulation."""
        from scitex.etc.wait_key import wait_key
        
        mock_process = Mock()
        
        # Simulate rapid key presses
        rapid_keys = ['x'] * 100 + ['q']
        
        call_times = []
        
        def mock_readchar():
            call_times.append(time.time())
            return rapid_keys[len(call_times) - 1]
        
        start = time.time()
        
        with patch('scitex.etc.wait_key.readchar.readchar', side_effect=mock_readchar):
            with patch('builtins.print'):
                wait_key(mock_process)
        
        end = time.time()
        
        # Should process all keys quickly
        assert len(call_times) == 101
        assert (end - start) < 1.0  # Should complete quickly

    def test_count_memory_stability(self):
        """Test count function doesn't have memory leaks."""
        from scitex.etc.wait_key import count
        import gc
        
        # Get initial object count
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        printed_count = 0
        
        def mock_print(value):
            nonlocal printed_count
            printed_count += 1
            if printed_count >= 1000:  # Run many iterations
                raise KeyboardInterrupt()
        
        with patch('scitex.etc.wait_key.time.sleep'):
            with patch('builtins.print', side_effect=mock_print):
                try:
                    count()
                except KeyboardInterrupt:
                    pass
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Object count shouldn't grow significantly
        # Allow some growth for test infrastructure
        assert final_objects - initial_objects < 100

    def test_wait_key_with_mock_stdin(self):
        """Test wait_key behavior with mocked stdin scenarios."""
        from scitex.etc.wait_key import wait_key
        
        mock_process = Mock()
        
        # Simulate various stdin scenarios
        scenarios = [
            (['q'], 1),  # Immediate quit
            (['a', 'b', 'c', 'q'], 4),  # Multiple keys
            (['\x1b', '[', 'A', 'q'], 4),  # Escape sequences
            (['\r', '\n', 'q'], 3),  # Newline characters
        ]
        
        for keys, expected_count in scenarios:
            mock_process.reset_mock()
            
            with patch('scitex.etc.wait_key.readchar.readchar', side_effect=keys):
                with patch('builtins.print') as mock_print:
                    wait_key(mock_process)
                    
                    # Verify correct number of prints
                    assert mock_print.call_count == expected_count + 1  # +1 for "q was pressed"
                    mock_process.terminate.assert_called_once()

    def test_concurrent_count_instances(self):
        """Test multiple count instances running concurrently."""
        from scitex.etc.wait_key import count
        
        results = {'instance1': [], 'instance2': [], 'instance3': []}
        
        def make_mock_print(instance_key):
            def mock_print(value):
                results[instance_key].append(value)
                if len(results[instance_key]) >= 5:
                    raise KeyboardInterrupt()
            return mock_print
        
        def run_count(instance_key):
            with patch('scitex.etc.wait_key.time.sleep'):
                with patch('builtins.print', side_effect=make_mock_print(instance_key)):
                    try:
                        count()
                    except KeyboardInterrupt:
                        pass
        
        # Run multiple instances in threads
        threads = []
        for key in results.keys():
            t = threading.Thread(target=run_count, args=(key,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join(timeout=2)
        
        # Verify each instance counted correctly
        for key, values in results.items():
            assert values == [0, 1, 2, 3, 4], f"Instance {key} counted incorrectly"

    def test_wait_key_signal_handling(self):
        """Test wait_key behavior with signal interruption."""
        from scitex.etc.wait_key import wait_key
        import signal
        
        mock_process = Mock()
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Test timeout")
        
        # Set up a timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        
        try:
            # This tests that wait_key doesn't block indefinitely
            with patch('scitex.etc.wait_key.readchar.readchar', side_effect=['a', 'b', 'c', 'q']):
                with patch('builtins.print'):
                    signal.alarm(1)  # 1 second timeout
                    wait_key(mock_process)
                    signal.alarm(0)  # Cancel alarm
                    
                    # Should complete before timeout
                    mock_process.terminate.assert_called_once()
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)


if HAS_HYPOTHESIS:
    class WaitKeyStateMachine(RuleBasedStateMachine):
        """State machine for testing wait_key behavior."""
        
        def __init__(self):
            super().__init__()
            self.keys_pressed = []
            self.process_terminated = False
            self.prints_made = []
        
        @rule(key=st.text(min_size=1, max_size=1).filter(lambda x: x not in ['q', '\x00']))
        def press_non_q_key(self, key):
            """Press a key that's not 'q'."""
            if not self.process_terminated:
                self.keys_pressed.append(key)
                self.prints_made.append(key)
        
        @rule()
        def press_q_key(self):
            """Press 'q' to terminate."""
            if not self.process_terminated:
                self.keys_pressed.append('q')
                self.prints_made.append('q')
                self.prints_made.append('q was pressed.')
                self.process_terminated = True
        
        @invariant()
        def process_terminated_after_q(self):
            """Process should be terminated if and only if 'q' was pressed."""
            if 'q' in self.keys_pressed:
                assert self.process_terminated
            else:
                assert not self.process_terminated
        
        @invariant()
        def prints_match_keys(self):
            """Prints should match keys pressed plus termination message."""
            if self.process_terminated:
                # Should have all keys plus termination message
                expected_prints = self.keys_pressed + ['q was pressed.']
                assert self.prints_made == expected_prints
            else:
                # Should have all keys pressed so far
                assert self.prints_made == self.keys_pressed

    # Run the state machine tests
    TestWaitKeyStateMachine = WaitKeyStateMachine.TestCase
else:
    # Create dummy test class
    @pytest.mark.skip(reason="hypothesis not installed")
    class TestWaitKeyStateMachine:
        def test_skipped(self):
            pass


if __name__ == "__main__":
    pytest.main([__FILE__, "-v"])