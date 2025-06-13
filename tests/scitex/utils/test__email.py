#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:15:00 (ywatanabe)"
# File: ./tests/scitex/utils/test__email.py

"""
Functionality:
    * Tests email sending functionality with Gmail SMTP
    * Validates attachment handling and message formatting
    * Tests ID generation and error handling
Input:
    * Mock SMTP configurations and test files
Output:
    * Test results
Prerequisites:
    * pytest
    * unittest.mock
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from scitex.utils import send_gmail, ansi_escape


class TestEmailFunctionality:
    """Test cases for email sending functionality."""

    @pytest.fixture
    def mock_smtp_server(self):
        """Create a mock SMTP server."""
        mock_server = Mock()
        mock_server.starttls = Mock()
        mock_server.login = Mock()
        mock_server.send_message = Mock()
        mock_server.quit = Mock()
        return mock_server

    @pytest.fixture
    def test_log_file(self):
        """Create a test log file with ANSI escape codes."""
        content = "This is a test log\n\x1b[31mError message\x1b[0m\nNormal text"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(content)
            filename = f.name
        
        yield filename
        os.unlink(filename)

    @pytest.fixture
    def test_text_file(self):
        """Create a test text file."""
        content = "This is a test file content"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            filename = f.name
        
        yield filename
        os.unlink(filename)

    @patch('scitex.utils._email.smtplib.SMTP')
    @patch('builtins.print')
    def test_send_gmail_basic(self, mock_print, mock_smtp, mock_smtp_server):
        """Test basic email sending functionality."""
        mock_smtp.return_value = mock_smtp_server
        
        send_gmail(
            sender_gmail="test@gmail.com",
            sender_password="password",
            recipient_email="recipient@example.com",
            subject="Test Subject",
            message="Test message"
        )
        
        # Verify SMTP server calls
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_smtp_server.starttls.assert_called_once()
        mock_smtp_server.login.assert_called_once_with("test@gmail.com", "password")
        mock_smtp_server.send_message.assert_called_once()
        mock_smtp_server.quit.assert_called_once()
        
        # Verify print was called for verbose output
        mock_print.assert_called_once()
        printed_message = mock_print.call_args[0][0]
        assert "Email was sent:" in printed_message
        assert "test@gmail.com -> recipient@example.com" in printed_message

    @patch('scitex.utils._email.smtplib.SMTP')
    @patch('scitex.utils._email.gen_ID')
    def test_send_gmail_auto_id(self, mock_gen_id, mock_smtp, mock_smtp_server):
        """Test email sending with auto-generated ID."""
        mock_smtp.return_value = mock_smtp_server
        mock_gen_id.return_value = "TEST123"
        
        send_gmail(
            sender_gmail="test@gmail.com",
            sender_password="password",
            recipient_email="recipient@example.com",
            subject="Test Subject",
            message="Test message",
            ID="auto",
            verbose=False
        )
        
        mock_gen_id.assert_called_once()
        
        # Verify message construction included ID
        call_args = mock_smtp_server.send_message.call_args[0][0]
        assert "Test Subject (ID: TEST123)" == call_args["Subject"]

    @patch('scitex.utils._email.smtplib.SMTP')
    def test_send_gmail_with_sender_name(self, mock_smtp, mock_smtp_server):
        """Test email sending with sender name."""
        mock_smtp.return_value = mock_smtp_server
        
        send_gmail(
            sender_gmail="test@gmail.com",
            sender_password="password",
            recipient_email="recipient@example.com",
            subject="Test Subject",
            message="Test message",
            sender_name="Test Sender",
            verbose=False
        )
        
        # Check that From field includes sender name
        call_args = mock_smtp_server.send_message.call_args[0][0]
        assert call_args["From"] == "Test Sender <test@gmail.com>"

    @patch('scitex.utils._email.smtplib.SMTP')
    def test_send_gmail_with_cc_string(self, mock_smtp, mock_smtp_server):
        """Test email sending with CC as string."""
        mock_smtp.return_value = mock_smtp_server
        
        send_gmail(
            sender_gmail="test@gmail.com",
            sender_password="password",
            recipient_email="recipient@example.com",
            subject="Test Subject",
            message="Test message",
            cc="cc@example.com",
            verbose=False
        )
        
        # Verify CC was set and recipients include CC
        call_args = mock_smtp_server.send_message.call_args
        email_obj = call_args[0][0]
        recipients = call_args[1]['to_addrs']
        
        assert email_obj["Cc"] == "cc@example.com"
        assert "cc@example.com" in recipients

    @patch('scitex.utils._email.smtplib.SMTP')
    def test_send_gmail_with_cc_list(self, mock_smtp, mock_smtp_server):
        """Test email sending with CC as list."""
        mock_smtp.return_value = mock_smtp_server
        
        cc_list = ["cc1@example.com", "cc2@example.com"]
        send_gmail(
            sender_gmail="test@gmail.com",
            sender_password="password",
            recipient_email="recipient@example.com",
            subject="Test Subject",
            message="Test message",
            cc=cc_list,
            verbose=False
        )
        
        # Verify CC was set properly and recipients include all CCs
        call_args = mock_smtp_server.send_message.call_args
        email_obj = call_args[0][0]
        recipients = call_args[1]['to_addrs']
        
        assert email_obj["Cc"] == "cc1@example.com, cc2@example.com"
        assert "cc1@example.com" in recipients
        assert "cc2@example.com" in recipients

    @patch('scitex.utils._email.smtplib.SMTP')
    def test_send_gmail_with_log_attachment(self, mock_smtp, mock_smtp_server, test_log_file):
        """Test email sending with log file attachment."""
        mock_smtp.return_value = mock_smtp_server
        
        send_gmail(
            sender_gmail="test@gmail.com",
            sender_password="password",
            recipient_email="recipient@example.com",
            subject="Test Subject",
            message="Test message",
            attachment_paths=[test_log_file],
            verbose=False
        )
        
        # Verify attachment was processed
        call_args = mock_smtp_server.send_message.call_args[0][0]
        assert len(call_args.get_payload()) > 1  # Body + attachment

    @patch('scitex.utils._email.smtplib.SMTP')
    def test_send_gmail_with_text_attachment(self, mock_smtp, mock_smtp_server, test_text_file):
        """Test email sending with text file attachment."""
        mock_smtp.return_value = mock_smtp_server
        
        send_gmail(
            sender_gmail="test@gmail.com",
            sender_password="password",
            recipient_email="recipient@example.com",
            subject="Test Subject",
            message="Test message",
            attachment_paths=[test_text_file],
            verbose=False
        )
        
        # Verify attachment was processed
        call_args = mock_smtp_server.send_message.call_args[0][0]
        assert len(call_args.get_payload()) > 1  # Body + attachment

    @patch('scitex.utils._email.smtplib.SMTP')
    @patch('builtins.print')
    def test_send_gmail_exception_handling(self, mock_print, mock_smtp):
        """Test error handling when email sending fails."""
        mock_smtp.side_effect = Exception("SMTP connection failed")
        
        send_gmail(
            sender_gmail="test@gmail.com",
            sender_password="password",
            recipient_email="recipient@example.com",
            subject="Test Subject",
            message="Test message"
        )
        
        # Verify error message was printed
        mock_print.assert_called_once()
        printed_message = mock_print.call_args[0][0]
        assert "Email was not sent:" in printed_message
        assert "SMTP connection failed" in printed_message

    def test_ansi_escape_regex(self):
        """Test ANSI escape code removal regex."""
        test_string = "Normal text \x1b[31mRed text\x1b[0m More normal text"
        cleaned = ansi_escape.sub("", test_string)
        assert cleaned == "Normal text Red text More normal text"
        
        # Test with multiple escape codes
        complex_string = "\x1b[1m\x1b[31mBold red\x1b[0m\x1b[32mGreen\x1b[0m"
        cleaned_complex = ansi_escape.sub("", complex_string)
        assert cleaned_complex == "Bold redGreen"

    @patch('scitex.utils._email.smtplib.SMTP')
    def test_send_gmail_no_subject_with_id(self, mock_smtp, mock_smtp_server):
        """Test email sending with ID but no subject."""
        mock_smtp.return_value = mock_smtp_server
        
        send_gmail(
            sender_gmail="test@gmail.com",
            sender_password="password",
            recipient_email="recipient@example.com",
            subject="",
            message="Test message",
            ID="TEST123",
            verbose=False
        )
        
        # Verify subject was set to just the ID
        call_args = mock_smtp_server.send_message.call_args[0][0]
        assert call_args["Subject"] == "ID: TEST123"

    @patch('scitex.utils._email.smtplib.SMTP')
    @patch('builtins.print')
    def test_send_gmail_verbose_with_attachments(self, mock_print, mock_smtp, mock_smtp_server, test_text_file):
        """Test verbose output with attachments."""
        mock_smtp.return_value = mock_smtp_server
        
        send_gmail(
            sender_gmail="test@gmail.com",
            sender_password="password",
            recipient_email="recipient@example.com",
            subject="Test Subject",
            message="Test message",
            attachment_paths=[test_text_file],
            ID="TEST123",
            verbose=True
        )
        
        # Verify verbose output includes attachment info
        printed_message = mock_print.call_args[0][0]
        assert "Attached:" in printed_message
        assert test_text_file in printed_message

    @patch('scitex.utils._email.smtplib.SMTP')
    def test_send_gmail_multiple_attachments(self, mock_smtp, mock_smtp_server, test_text_file, test_log_file):
        """Test email sending with multiple attachments."""
        mock_smtp.return_value = mock_smtp_server
        
        send_gmail(
            sender_gmail="test@gmail.com",
            sender_password="password",
            recipient_email="recipient@example.com",
            subject="Test Subject",
            message="Test message",
            attachment_paths=[test_text_file, test_log_file],
            verbose=False
        )
        
        # Verify multiple attachments were processed
        call_args = mock_smtp_server.send_message.call_args[0][0]
        payload = call_args.get_payload()
        assert len(payload) == 3  # Body + 2 attachments


if __name__ == "__main__":
    import os
    import pytest
    pytest.main([os.path.abspath(__file__)])
