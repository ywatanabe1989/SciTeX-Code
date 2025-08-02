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
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/utils/_notify.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-06-15 20:25:22 (ywatanabe)"
# # File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/SciTeX-Code/src/scitex/utils/_notify.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/utils/_notify.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# # Time-stamp: "2024-11-24 17:54:38 (ywatanabe)"
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/utils/_notify.py"
# 
# # Time-stamp: "2024-11-07 05:38:14 (ywatanabe)"
# 
# """This script does XYZ."""
# 
# import inspect
# import pwd
# import socket
# import subprocess
# import sys
# import warnings
# 
# from ._email import send_gmail
# 
# 
# def get_username():
#     try:
#         return pwd.getpwuid(os.getuid()).pw_name
#     except:
#         return os.getenv("USER") or os.getenv("LOGNAME") or "unknown"
# 
# 
# def get_hostname():
#     return socket.gethostname()
# 
# 
# def get_git_branch(scitex):
#     try:
#         branch = (
#             subprocess.check_output(
#                 ["git", "rev-parse", "--abbrev-ref", "HEAD"],
#                 cwd=scitex.__path__[0],
#                 stderr=subprocess.DEVNULL,
#             )
#             .decode()
#             .strip()
#         )
#         return branch
# 
#     except Exception as e:
#         print(e)
#         return "main"
# 
# 
# def gen_footer(sender, script_name, scitex, branch):
#     return f"""
# 
# {'-'*30}
# Sent via
# - Host: {sender}
# - Script: {script_name}
# - Source: scitex v{scitex.__version__} (github.com/ywatanabe1989/scitex/blob/{branch}/src/scitex/gen/system_ops/_notify.py)
# {'-'*30}"""
# 
# 
# # This is an automated system notification. If received outside working hours, please disregard.
# 
# 
# def notify(
#     subject="",
#     message=":)",
#     file=None,
#     ID="auto",
#     sender_name=None,
#     recipient_email=None,
#     cc=None,
#     attachment_paths=None,
#     verbose=False,
# ):
#     import scitex
# 
#     try:
#         message = str(message)
#     except Exception as e:
#         warnings.warn(str(e))
# 
#     FAKE_PYTHON_SCRIPT_NAME = "$ python -c ..."
#     sender_gmail = os.getenv("SCITEX_SENDER_GMAIL")
#     sender_password = os.getenv("SCITEX_SENDER_GMAIL_PASSWORD")
#     recipient_email = recipient_email or os.getenv("SCITEX_RECIPIENT_GMAIL")
# 
#     if file is not None:
#         script_name = str(file)
#     else:
#         if sys.argv[0]:
#             script_name = os.path.basename(sys.argv[0])
#         else:
#             frames = inspect.stack()
#             script_name = (
#                 os.path.basename(frames[-1].filename)
#                 if frames
#                 else "(Not found)"
#             )
#         if (script_name == "-c") or (not script_name.endswith(".py")):
#             script_name = FAKE_PYTHON_SCRIPT_NAME
# 
#     sender = f"{get_username()}@{get_hostname()}"
#     branch = get_git_branch(scitex)
#     footer = gen_footer(sender, script_name, scitex, branch)
# 
#     full_message = script_name + "\n\n" + message + "\n\n" + footer
#     full_subject = (
#         f"{script_name}—{subject}"
#         if subject and (script_name != FAKE_PYTHON_SCRIPT_NAME)
#         else f"{subject}"
#     )
# 
#     if sender_gmail is None or sender_password is None:
#         print(
#             f"""
#         Please set environmental variables to use this function (f"{inspect.stack()[0][3]}"):\n\n
#         $ export SciTeX_SENDER_GMAIL="scitex.notification@gmail.com"
#         $ export SciTeX_SENDER_GMAIL_PASSWORD="YOUR_APP_PASSWORD"
#         $ export SciTeX_RECIPIENT_GMAIL="YOUR_GMAIL_ADDRESS"
#         """
#         )
# 
#     send_gmail(
#         sender_gmail,
#         sender_password,
#         recipient_email,
#         full_subject,
#         full_message,
#         sender_name=sender_name,
#         cc=cc,
#         ID=ID,
#         attachment_paths=attachment_paths,
#         verbose=verbose,
#     )
# 
# 
# if __name__ == "__main__":
#     notify(verbose=True)
# 
#     # python -c "; scitex.gen.notify()"
# 
# 
# # # Example in shell
# # #!/bin/bash
# # # /home/ywatanabe/.dotfiles/.bin/notify
# # # Author: ywatanabe (ywatanabe@alumni.u-tokyo.ac.jp)
# # # Date: $(date +"%Y-%m-%d-%H-%M")
# 
# # # LOG_FILE="${0%.sh}.log"
# 
# # usage() {
# #     echo "Usage: $0 [-s|--subject <subject>] [-m|--message <message>] [-r|--recipient-name <name>] [-t|--to <email>] [-c|--cc <email>] [-h|--help]"
# #     echo "Options:"
# #     echo "  -s, --subject   Subject of the notification (default: 'Subject')"
# #     echo "  -m, --message   Message body of the notification (default: 'Message')"
# #     echo "  -t, --to        The email address of the recipient"
# #     echo "  -c, --cc        CC email address(es) (can be used multiple times)"
# #     echo "  -h, --help      Display this help message"
# #     echo
# #     echo "Example:"
# #     echo "  $0 -s \"About the Project A\" -m \"Hi, ...\" -r \"John\" -t \"john@example.com\" -c \"cc1@example.com\" -c \"cc2@example.com\""
# #     echo "  $0 -s \"Notification\" -m \"This is a notification from ...\" -r \"Team\" -t \"team@example.com\""
# #     exit 1
# # }
# 
# # main() {
# #     subject="Subject"
# #     message="Message"
# #     recipient_email=""
# #     cc_addresses=()
# 
# #     while [[ $# -gt 0 ]]; do
# #         case $1 in
# #             -s|--subject)
# #                 shift
# #                 subject=""
# #                 while [[ $# -gt 0 && ! $1 =~ ^- ]]; do
# #                     subject+="$1 "
# #                     shift
# #                 done
# #                 subject=${subject% }
# #                 ;;
# #             -m|--message)
# #                 shift
# #                 message=""
# #                 while [[ $# -gt 0 && ! $1 =~ ^- ]]; do
# #                     message+="$1 "
# #                     shift
# #                 done
# #                 message=${message% }
# #                 ;;
# #             -t|--to)
# #                 shift
# #                 recipient_email="$1"
# #                 shift
# #                 ;;
# #             -c|--cc)
# #                 shift
# #                 cc_addresses+=("$1")
# #                 shift
# #                 ;;
# #             -h|--help)
# #                 usage
# #                 ;;
# #             *)
# #                 echo "Unknown option: $1"
# #                 usage
# #                 ;;
# #         esac
# #     done
# 
# #     subject=$(echo "$subject" | sed "s/'/'\\\\''/g")
# #     message=$(echo "$message" | sed "s/'/'\\\\''/g")
# #     recipient_email=$(echo "$recipient_email" | sed "s/'/'\\\\''/g")
# #     cc_string=$(IFS=,; echo "${cc_addresses[*]}" | sed "s/'/'\\\\''/g")
# 
# #     python -c "
# #
# 
# # cc_list = [$(printf "'%s', " "${cc_addresses[@]}")]
# # cc_list = [addr.strip() for addr in cc_list if addr.strip()]
# 
# # scitex.gen.notify(
# #     subject='$subject',
# #     message='$message',
# #     ID=None,
# #     recipient_email='$recipient_email',
# #     cc=cc_list
# # )
# # "
# # }
# 
# # main "$@"
# # # { main "$@"; } 2>&1 | tee "$LOG_FILE"
# 
# #
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/utils/_notify.py
# --------------------------------------------------------------------------------
