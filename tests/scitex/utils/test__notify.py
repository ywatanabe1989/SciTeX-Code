#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:15:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/utils/test__notify.py

"""Tests for notification utility functions."""

import os
import pytest
import subprocess
from unittest.mock import patch, MagicMock, call
import tempfile


def test_get_username():
    """Test username retrieval."""
    from scitex.utils import get_username
    
    username = get_username()
    assert isinstance(username, str)
    assert len(username) > 0
    assert username != "unknown"  # Should get real username


def test_get_username_fallback():
    """Test username fallback when pwd fails."""
    from scitex.utils import get_username
    
    with patch('pwd.getpwuid', side_effect=Exception("No user")):
        with patch.dict(os.environ, {'USER': 'testuser'}, clear=True):
            username = get_username()
            assert username == "testuser"


def test_get_username_logname_fallback():
    """Test username fallback to LOGNAME."""
    from scitex.utils import get_username
    
    with patch('pwd.getpwuid', side_effect=Exception("No user")):
        with patch.dict(os.environ, {'LOGNAME': 'loguser'}, clear=False):
            if 'USER' in os.environ:
                del os.environ['USER']
            username = get_username()
            assert username == "loguser"


def test_get_username_unknown_fallback():
    """Test username fallback to unknown."""
    from scitex.utils import get_username
    
    with patch('pwd.getpwuid', side_effect=Exception("No user")):
        with patch.dict(os.environ, {}, clear=True):
            username = get_username()
            assert username == "unknown"


def test_get_hostname():
    """Test hostname retrieval."""
    from scitex.utils import get_hostname
    
    hostname = get_hostname()
    assert isinstance(hostname, str)
    assert len(hostname) > 0


def test_get_git_branch_success():
    """Test successful git branch retrieval."""
    from scitex.utils import get_git_branch
    
    mock_scitex = MagicMock()
    mock_scitex.__path__ = ['/fake/path']
    
    with patch('subprocess.check_output', return_value=b'feature-branch\n'):
        branch = get_git_branch(mock_scitex)
        assert branch == "feature-branch"


def test_get_git_branch_failure():
    """Test git branch retrieval failure fallback."""
    from scitex.utils import get_git_branch
    
    mock_scitex = MagicMock()
    mock_scitex.__path__ = ['/fake/path']
    
    with patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(1, 'git')):
        with patch('builtins.print'):  # Suppress error print
            branch = get_git_branch(mock_scitex)
            assert branch == "main"


def test_gen_footer():
    """Test footer generation."""
    from scitex.utils import gen_footer
    
    mock_scitex = MagicMock()
    mock_scitex.__version__ = "1.0.0"
    
    footer = gen_footer("user@host", "script.py", mock_scitex, "main")
    
    assert "user@host" in footer
    assert "script.py" in footer
    assert "1.0.0" in footer
    assert "main" in footer
    assert "scitex" in footer
    assert "-" * 30 in footer


def test_notify_missing_credentials():
    """Test notify with missing credentials."""
    from scitex.utils import notify
    
    with patch.dict(os.environ, {}, clear=True):
        with patch('builtins.print') as mock_print:
            with patch('scitex.utils._notify.send_gmail') as mock_send:
                notify(subject="Test", message="Test message")
                
                # Should print credential instructions
                mock_print.assert_called()
                printed_text = mock_print.call_args[0][0]
                assert "SciTeX_SENDER_GMAIL" in printed_text
                assert "SciTeX_SENDER_GMAIL_PASSWORD" in printed_text
                assert "SciTeX_RECIPIENT_GMAIL" in printed_text


def test_notify_with_credentials():
    """Test notify with proper credentials."""
    from scitex.utils import notify
    
    env_vars = {
        'SciTeX_SENDER_GMAIL': 'sender@gmail.com',
        'SciTeX_SENDER_GMAIL_PASSWORD': 'password123',
        'SciTeX_RECIPIENT_GMAIL': 'recipient@gmail.com'
    }
    
    with patch.dict(os.environ, env_vars):
        with patch('scitex.utils._notify.send_gmail') as mock_send:
            with patch('scitex.utils._notify.get_username', return_value='testuser'):
                with patch('scitex.utils._notify.get_hostname', return_value='testhost'):
                    with patch('scitex.utils._notify.get_git_branch', return_value='main'):
                        notify(subject="Test Subject", message="Test message")
                        
                        mock_send.assert_called_once()
                        args = mock_send.call_args[0]
                        kwargs = mock_send.call_args[1]
                        
                        assert args[0] == 'sender@gmail.com'
                        assert args[1] == 'password123'
                        assert args[2] == 'recipient@gmail.com'
                        assert "Test Subject" in args[3]
                        assert "Test message" in args[4]


def test_notify_script_name_detection():
    """Test script name detection."""
    from scitex.utils import notify
    
    env_vars = {
        'SciTeX_SENDER_GMAIL': 'sender@gmail.com',
        'SciTeX_SENDER_GMAIL_PASSWORD': 'password123',
        'SciTeX_RECIPIENT_GMAIL': 'recipient@gmail.com'
    }
    
    with patch.dict(os.environ, env_vars):
        with patch('scitex.utils._notify.send_gmail') as mock_send:
            with patch('sys.argv', ['test_script.py']):
                with patch('scitex.utils._notify.get_username', return_value='testuser'):
                    with patch('scitex.utils._notify.get_hostname', return_value='testhost'):
                        with patch('scitex.utils._notify.get_git_branch', return_value='main'):
                            notify(subject="Test", message="Test")
                            
                            args = mock_send.call_args[0]
                            assert "test_script.py" in args[4]  # message content
                            assert "test_script.py" in args[3]  # subject


def test_notify_with_file_parameter():
    """Test notify with explicit file parameter."""
    from scitex.utils import notify
    
    env_vars = {
        'SciTeX_SENDER_GMAIL': 'sender@gmail.com',
        'SciTeX_SENDER_GMAIL_PASSWORD': 'password123',
        'SciTeX_RECIPIENT_GMAIL': 'recipient@gmail.com'
    }
    
    with patch.dict(os.environ, env_vars):
        with patch('scitex.utils._notify.send_gmail') as mock_send:
            with patch('scitex.utils._notify.get_username', return_value='testuser'):
                with patch('scitex.utils._notify.get_hostname', return_value='testhost'):
                    with patch('scitex.utils._notify.get_git_branch', return_value='main'):
                        notify(subject="Test", message="Test", file="custom_script.py")
                        
                        args = mock_send.call_args[0]
                        assert "custom_script.py" in args[4]


def test_notify_command_line_detection():
    """Test notify with command line script detection."""
    from scitex.utils import notify
    
    env_vars = {
        'SciTeX_SENDER_GMAIL': 'sender@gmail.com',
        'SciTeX_SENDER_GMAIL_PASSWORD': 'password123',
        'SciTeX_RECIPIENT_GMAIL': 'recipient@gmail.com'
    }
    
    with patch.dict(os.environ, env_vars):
        with patch('scitex.utils._notify.send_gmail') as mock_send:
            with patch('sys.argv', ['-c']):  # Command line execution
                with patch('scitex.utils._notify.get_username', return_value='testuser'):
                    with patch('scitex.utils._notify.get_hostname', return_value='testhost'):
                        with patch('scitex.utils._notify.get_git_branch', return_value='main'):
                            notify(subject="Test", message="Test")
                            
                            args = mock_send.call_args[0]
                            assert "$ python -c ..." in args[4]


def test_notify_message_conversion():
    """Test message conversion to string."""
    from scitex.utils import notify
    
    env_vars = {
        'SciTeX_SENDER_GMAIL': 'sender@gmail.com',
        'SciTeX_SENDER_GMAIL_PASSWORD': 'password123',
        'SciTeX_RECIPIENT_GMAIL': 'recipient@gmail.com'
    }
    
    with patch.dict(os.environ, env_vars):
        with patch('scitex.utils._notify.send_gmail') as mock_send:
            with patch('scitex.utils._notify.get_username', return_value='testuser'):
                with patch('scitex.utils._notify.get_hostname', return_value='testhost'):
                    with patch('scitex.utils._notify.get_git_branch', return_value='main'):
                        # Test with non-string message
                        notify(subject="Test", message=12345)
                        
                        args = mock_send.call_args[0]
                        assert "12345" in args[4]


def test_notify_additional_parameters():
    """Test notify with additional parameters."""
    from scitex.utils import notify
    
    env_vars = {
        'SciTeX_SENDER_GMAIL': 'sender@gmail.com',
        'SciTeX_SENDER_GMAIL_PASSWORD': 'password123',
        'SciTeX_RECIPIENT_GMAIL': 'recipient@gmail.com'
    }
    
    with patch.dict(os.environ, env_vars):
        with patch('scitex.utils._notify.send_gmail') as mock_send:
            with patch('scitex.utils._notify.get_username', return_value='testuser'):
                with patch('scitex.utils._notify.get_hostname', return_value='testhost'):
                    with patch('scitex.utils._notify.get_git_branch', return_value='main'):
                        notify(
                            subject="Test",
                            message="Test",
                            ID="custom_id",
                            sender_name="Custom Sender",
                            cc=["cc@example.com"],
                            attachment_paths=["/path/to/file"],
                            verbose=True
                        )
                        
                        kwargs = mock_send.call_args[1]
                        assert kwargs['ID'] == "custom_id"
                        assert kwargs['sender_name'] == "Custom Sender"
                        assert kwargs['cc'] == ["cc@example.com"]
                        assert kwargs['attachment_paths'] == ["/path/to/file"]
                        assert kwargs['verbose'] is True


def test_notify_subject_formatting():
    """Test subject formatting logic."""
    from scitex.utils import notify
    
    env_vars = {
        'SciTeX_SENDER_GMAIL': 'sender@gmail.com',
        'SciTeX_SENDER_GMAIL_PASSWORD': 'password123',
        'SciTeX_RECIPIENT_GMAIL': 'recipient@gmail.com'
    }
    
    with patch.dict(os.environ, env_vars):
        with patch('scitex.utils._notify.send_gmail') as mock_send:
            with patch('sys.argv', ['test_script.py']):
                with patch('scitex.utils._notify.get_username', return_value='testuser'):
                    with patch('scitex.utils._notify.get_hostname', return_value='testhost'):
                        with patch('scitex.utils._notify.get_git_branch', return_value='main'):
                            # Test with both script and subject
                            notify(subject="Important", message="Test")
                            
                            args = mock_send.call_args[0]
                            subject = args[3]
                            assert "test_script.py" in subject
                            assert "Important" in subject
                            assert "—" in subject  # em dash separator


def test_notify_empty_subject():
    """Test notify with empty subject."""
    from scitex.utils import notify
    
    env_vars = {
        'SciTeX_SENDER_GMAIL': 'sender@gmail.com',
        'SciTeX_SENDER_GMAIL_PASSWORD': 'password123',
        'SciTeX_RECIPIENT_GMAIL': 'recipient@gmail.com'
    }
    
    with patch.dict(os.environ, env_vars):
        with patch('scitex.utils._notify.send_gmail') as mock_send:
            with patch('sys.argv', ['-c']):  # Command line - no script name in subject
                with patch('scitex.utils._notify.get_username', return_value='testuser'):
                    with patch('scitex.utils._notify.get_hostname', return_value='testhost'):
                        with patch('scitex.utils._notify.get_git_branch', return_value='main'):
                            notify(subject="", message="Test")
                            
                            args = mock_send.call_args[0]
                            subject = args[3]
                            assert subject == ""


def test_message_conversion_exception():
    """Test message conversion with exception handling."""
    from scitex.utils import notify
    
    # Create an object that raises exception when converted to string
    class BadObject:
        def __str__(self):
            raise ValueError("Cannot convert to string")
    
    env_vars = {
        'SciTeX_SENDER_GMAIL': 'sender@gmail.com',
        'SciTeX_SENDER_GMAIL_PASSWORD': 'password123',
        'SciTeX_RECIPIENT_GMAIL': 'recipient@gmail.com'
    }
    
    with patch.dict(os.environ, env_vars):
        with patch('scitex.utils._notify.send_gmail') as mock_send:
            with patch('warnings.warn') as mock_warn:
                with patch('scitex.utils._notify.get_username', return_value='testuser'):
                    with patch('scitex.utils._notify.get_hostname', return_value='testhost'):
                        with patch('scitex.utils._notify.get_git_branch', return_value='main'):
                            notify(subject="Test", message=BadObject())
                            
                            # Should have warned about conversion error
                            mock_warn.assert_called()


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
