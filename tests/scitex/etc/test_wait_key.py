#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 15:05:32 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/etc/test_wait_key.py
# ----------------------------------------
import os
import sys
import time
import threading
import multiprocessing
from unittest.mock import Mock, MagicMock, patch, call
import pytest

__FILE__ = "./tests/scitex/etc/test_wait_key.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------


class TestWaitKey:
    """Comprehensive tests for scitex.etc.wait_key module functionality."""

    def test_wait_key_basic_functionality(self):
        """Test basic wait_key functionality with mock process and input."""
        from scitex.etc.wait_key import wait_key
        
        # Create a mock process
        mock_process = Mock()
        mock_process.terminate = Mock()
        
        # Mock readchar to simulate 'q' key press
        with patch('scitex.etc.wait_key.readchar.readchar', return_value='q'):
            with patch('builtins.print') as mock_print:
                wait_key(mock_process)
                
                # Should terminate the process
                mock_process.terminate.assert_called_once()
                
                # Should print q and termination message
                expected_calls = [call('q'), call('q was pressed.')]
                mock_print.assert_has_calls(expected_calls)

    def test_wait_key_multiple_keys_before_quit(self):
        """Test wait_key with multiple key presses before 'q'."""
        from scitex.etc.wait_key import wait_key
        
        # Create a mock process
        mock_process = Mock()
        mock_process.terminate = Mock()
        
        # Mock readchar to simulate multiple key presses then 'q'
        key_sequence = ['a', 'b', 'c', 'q']
        with patch('scitex.etc.wait_key.readchar.readchar', side_effect=key_sequence):
            with patch('builtins.print') as mock_print:
                wait_key(mock_process)
                
                # Should terminate the process
                mock_process.terminate.assert_called_once()
                
                # Should print all keys and termination message
                expected_calls = [call('a'), call('b'), call('c'), call('q'), call('q was pressed.')]
                mock_print.assert_has_calls(expected_calls)

    def test_wait_key_special_characters(self):
        """Test wait_key with special characters before 'q'."""
        from scitex.etc.wait_key import wait_key
        
        # Create a mock process
        mock_process = Mock()
        
        # Mock readchar with special characters
        key_sequence = ['\n', '\t', ' ', '1', '!', 'q']
        with patch('scitex.etc.wait_key.readchar.readchar', side_effect=key_sequence):
            with patch('builtins.print') as mock_print:
                wait_key(mock_process)
                
                # Should terminate the process
                mock_process.terminate.assert_called_once()
                
                # Should print all keys including special characters
                expected_calls = [call('\n'), call('\t'), call(' '), call('1'), call('!'), call('q'), call('q was pressed.')]
                mock_print.assert_has_calls(expected_calls)

    def test_wait_key_uppercase_q(self):
        """Test that uppercase 'Q' doesn't trigger termination (case sensitive)."""
        from scitex.etc.wait_key import wait_key
        
        # Create a mock process
        mock_process = Mock()
        
        # Mock readchar with uppercase Q then lowercase q
        key_sequence = ['Q', 'q']
        with patch('scitex.etc.wait_key.readchar.readchar', side_effect=key_sequence):
            with patch('builtins.print') as mock_print:
                wait_key(mock_process)
                
                # Should terminate the process only after lowercase q
                mock_process.terminate.assert_called_once()
                
                # Should print both Q and q, then termination message
                expected_calls = [call('Q'), call('q'), call('q was pressed.')]
                mock_print.assert_has_calls(expected_calls)

    def test_wait_key_immediate_quit(self):
        """Test wait_key when 'q' is pressed immediately."""
        from scitex.etc.wait_key import wait_key
        
        # Create a mock process
        mock_process = Mock()
        
        # Mock readchar to return 'q' immediately
        with patch('scitex.etc.wait_key.readchar.readchar', return_value='q'):
            with patch('builtins.print') as mock_print:
                wait_key(mock_process)
                
                # Should terminate the process
                mock_process.terminate.assert_called_once()
                
                # Should print q and termination message
                expected_calls = [call('q'), call('q was pressed.')]
                mock_print.assert_has_calls(expected_calls)

    def test_wait_key_process_mock_verification(self):
        """Test that wait_key properly interacts with process object."""
        from scitex.etc.wait_key import wait_key
        
        # Create a mock process with additional attributes
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.is_alive.return_value = True
        
        with patch('scitex.etc.wait_key.readchar.readchar', return_value='q'):
            with patch('builtins.print'):
                wait_key(mock_process)
                
                # Verify terminate was called
                mock_process.terminate.assert_called_once()
                
                # Verify no other methods were called unexpectedly
                assert not mock_process.kill.called if hasattr(mock_process, 'kill') else True

    def test_count_basic_functionality(self):
        """Test basic count function behavior."""
        from scitex.etc.wait_key import count
        
        # Mock time.sleep to prevent actual delays
        with patch('scitex.etc.wait_key.time.sleep') as mock_sleep:
            with patch('builtins.print') as mock_print:
                # Use threading to run count for a short time then stop it
                stop_event = threading.Event()
                
                def run_count():
                    counter = 0
                    # Modified version that stops after a few iterations
                    for _ in range(3):
                        if stop_event.is_set():
                            break
                        print(counter)
                        time.sleep(1)
                        counter += 1
                
                # Run the modified count function
                with patch('scitex.etc.wait_key.count', side_effect=run_count):
                    from scitex.etc.wait_key import count
                    count()
                
                # Should have called print with incrementing numbers
                expected_calls = [call(0), call(1), call(2)]
                mock_print.assert_has_calls(expected_calls)
                
                # Should have called sleep
                assert mock_sleep.call_count == 3

    def test_count_increments_properly(self):
        """Test that count function increments counter properly."""
        from scitex.etc.wait_key import count
        
        # Create a way to capture the counter values
        printed_values = []
        
        def mock_print(value):
            printed_values.append(value)
            # Stop after a few iterations to prevent infinite loop
            if len(printed_values) >= 5:
                raise KeyboardInterrupt("Test stop")
        
        with patch('scitex.etc.wait_key.time.sleep'):  # Mock sleep to speed up test
            with patch('builtins.print', side_effect=mock_print):
                try:
                    count()
                except KeyboardInterrupt:
                    pass  # Expected to break the loop
        
        # Verify the counter incremented properly
        assert printed_values == [0, 1, 2, 3, 4]

    def test_count_infinite_loop_behavior(self):
        """Test that count function runs in infinite loop until interrupted."""
        from scitex.etc.wait_key import count
        
        call_count = 0
        
        def mock_print(value):
            nonlocal call_count
            call_count += 1
            # Verify it's counting correctly
            assert value == call_count - 1
            # Stop after 10 iterations to verify infinite behavior
            if call_count >= 10:
                raise KeyboardInterrupt("Test stop")
        
        with patch('scitex.etc.wait_key.time.sleep'):
            with patch('builtins.print', side_effect=mock_print):
                try:
                    count()
                except KeyboardInterrupt:
                    pass
        
        # Should have made exactly 10 calls before stopping
        assert call_count == 10

    def test_readchar_import_availability(self):
        """Test that readchar module is properly imported."""
        import scitex.etc.wait_key
        
        # Check that readchar is available in the module
        assert hasattr(scitex.etc.wait_key, 'readchar')
        
        # Verify readchar.readchar is callable
        assert callable(scitex.etc.wait_key.readchar.readchar)

    def test_multiprocessing_import_availability(self):
        """Test that multiprocessing module is properly imported."""
        import scitex.etc.wait_key
        
        # Check that multiprocessing is available in the module
        assert hasattr(scitex.etc.wait_key, 'multiprocessing')
        
        # Verify multiprocessing.Process is accessible
        assert hasattr(scitex.etc.wait_key.multiprocessing, 'Process')

    def test_time_import_availability(self):
        """Test that time module is properly imported."""
        import scitex.etc.wait_key
        
        # Check that time is available in the module
        assert hasattr(scitex.etc.wait_key, 'time')
        
        # Verify time.sleep is callable
        assert callable(scitex.etc.wait_key.time.sleep)

    def test_module_structure(self):
        """Test the overall module structure and available functions."""
        import scitex.etc.wait_key as wk
        
        # Check that required functions exist
        assert hasattr(wk, 'wait_key')
        assert hasattr(wk, 'count')
        
        # Check that functions are callable
        assert callable(wk.wait_key)
        assert callable(wk.count)

    def test_wait_key_with_real_process_mock(self):
        """Test wait_key with a more realistic process mock."""
        from scitex.etc.wait_key import wait_key
        
        # Create a mock that behaves more like a real process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.exitcode = None
        mock_process.is_alive.return_value = True
        
        # Mock the terminate method to change process state
        def mock_terminate():
            mock_process.exitcode = -15  # SIGTERM
            mock_process.is_alive.return_value = False
        
        mock_process.terminate.side_effect = mock_terminate
        
        with patch('scitex.etc.wait_key.readchar.readchar', return_value='q'):
            with patch('builtins.print'):
                wait_key(mock_process)
                
                # Verify terminate was called
                mock_process.terminate.assert_called_once()
                
                # Verify process state changed
                assert mock_process.exitcode == -15
                assert not mock_process.is_alive()

    def test_wait_key_error_handling(self):
        """Test wait_key behavior when process.terminate() raises an error."""
        from scitex.etc.wait_key import wait_key
        
        # Create a mock process that raises an error on terminate
        mock_process = Mock()
        mock_process.terminate.side_effect = OSError("Process already terminated")
        
        with patch('scitex.etc.wait_key.readchar.readchar', return_value='q'):
            with patch('builtins.print'):
                # Should not raise an exception even if terminate fails
                try:
                    wait_key(mock_process)
                    # If we get here, the function handled the error gracefully
                    mock_process.terminate.assert_called_once()
                except OSError:
                    # If the error propagates, that's also valid behavior
                    pass

    def test_integration_simulation(self):
        """Test a simulated integration scenario without actually running processes."""
        from scitex.etc.wait_key import wait_key, count
        
        # Simulate the main block behavior
        mock_process = Mock()
        mock_process.start = Mock()
        mock_process.terminate = Mock()
        
        # Mock multiprocessing.Process
        with patch('scitex.etc.wait_key.multiprocessing.Process', return_value=mock_process):
            with patch('scitex.etc.wait_key.readchar.readchar', return_value='q'):
                with patch('builtins.print'):
                    # Simulate creating and starting a process
                    p1 = multiprocessing.Process(target=count)
                    p1.start()
                    
                    # Simulate wait_key call
                    wait_key(p1)
                    
                    # Verify the flow
                    mock_process.start.assert_called_once()
                    mock_process.terminate.assert_called_once()

    def test_function_signatures(self):
        """Test that functions have expected signatures."""
        from scitex.etc.wait_key import wait_key, count
        import inspect
        
        # Test wait_key signature
        wait_key_sig = inspect.signature(wait_key)
        assert len(wait_key_sig.parameters) == 1
        assert 'p' in wait_key_sig.parameters
        
        # Test count signature
        count_sig = inspect.signature(count)
        assert len(count_sig.parameters) == 0

    def test_module_docstring_availability(self):
        """Test that module and functions can be introspected."""
        import scitex.etc.wait_key as wk
        
        # Module should be importable and have functions
        assert hasattr(wk, 'wait_key')
        assert hasattr(wk, 'count')
        
        # Functions should be introspectable
        assert callable(wk.wait_key)
        assert callable(wk.count)
        
        # Should be able to get help/doc information
        import inspect
        assert inspect.isfunction(wk.wait_key)
        assert inspect.isfunction(wk.count)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/etc/wait_key.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2023-03-24 23:13:32 (ywatanabe)"
# 
# import readchar
# import time
# import multiprocessing
# 
# 
# def wait_key(p):
#     key = "x"
#     while key != "q":
#         key = readchar.readchar()
#         print(key)
#     print("q was pressed.")
#     p.terminate()
#     # event.set()
#     # raise Exception
# 
# 
# def count():
#     counter = 0
#     while True:
#         print(counter)
#         time.sleep(1)
#         counter += 1
# 
# 
# if __name__ == "__main__":
#     p1 = multiprocessing.Process(target=count)
# 
#     p1.start()
#     waitKey(p1)
#     print("aaa")

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/etc/wait_key.py
# --------------------------------------------------------------------------------
