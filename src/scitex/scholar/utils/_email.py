#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 14:43:05 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/utils/_email.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/utils/_email.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Scholar-specific email functionality for independent operation."""

import asyncio
import mimetypes
import re
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional, Union

from scitex.logging import getLogger

from ..config import ScholarConfig

logger = getLogger(__name__)

# ANSI escape sequence regex for cleaning log files
ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


class ScholarEmailError(Exception):
    """Raised when Scholar email operations fail."""

    pass


async def send_email_async(
    from_email: str,
    to_email: str,
    subject: str,
    message: str,
    password: Optional[str] = None,
    smtp_server: str = "mail1030.onamae.ne.jp",
    smtp_port: int = 587,
    cc: Optional[Union[str, List[str]]] = None,
    attachment_paths: Optional[List[str]] = None,
    sender_name: Optional[str] = None,
    config: Optional[ScholarConfig] = None,
) -> bool:
    """Send email asynchronously using Scholar email configuration.

    Args:
        from_email: Sender email address
        to_email: Recipient email address
        subject: Email subject
        message: Email body
        password: Email password (defaults to SCITEX_EMAIL_PASSWORD env var)
        smtp_server: SMTP server hostname
        smtp_port: SMTP server port
        cc: CC recipients (string or list of strings)
        attachment_paths: List of file paths to attach
        sender_name: Display name for sender

    Returns:
        True if email sent successfully, False otherwise
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        send_email,
        from_email,
        to_email,
        subject,
        message,
        password,
        smtp_server,
        smtp_port,
        cc,
        attachment_paths,
        sender_name,
        config,
    )


def send_email(
    from_email: str = None,
    to_email: str = None,
    subject: str = None,
    message: str = None,
    password: str = None,
    smtp_server: str = None,
    smtp_port: int = None,
    cc: Optional[Union[str, List[str]]] = None,
    attachment_paths: Optional[List[str]] = None,
    sender_name: Optional[str] = None,
    config: Optional[ScholarConfig] = None,
) -> bool:
    """Send email using Scholar email configuration.

    Args:
        from_email: Sender email address
        to_email: Recipient email address
        subject: Email subject
        message: Email body
        password: Email password (defaults to SCITEX_EMAIL_PASSWORD env var)
        smtp_server: SMTP server hostname (defaults to SciTeX onamae.ne.jp server)
        smtp_port: SMTP server port (587 for TLS)
        cc: CC recipients (string or list of strings)
        attachment_paths: List of file paths to attach
        sender_name: Display name for sender

    Returns:
        True if email sent successfully, False otherwise
    """
    config = config or ScholarConfig()
    from_email = config.resolve("from_email_address", from_email, default=None)
    to_email = config.resolve("to_email_address", to_email, default=None)
    password = config.resolve("from_email_password", password, default=None)
    smtp_server = config.resolve(
        "from_email_smtp_server", smtp_server, default=None
    )
    smtp_port = config.resolve("from_email_smtp_port", smtp_port, default=587)

    try:
        # Get password from environment if not provided
        if password is None:
            raise ScholarEmailError(
                "No email password provided. Set SCITEX_EMAIL_PASSWORD environment variable."
            )

        # Create SMTP connection
        logger.debug(f"Connecting to SMTP server: {smtp_server}:{smtp_port}")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, password)

        # Create email message
        email_msg = MIMEMultipart()
        email_msg["Subject"] = subject
        email_msg["To"] = to_email

        # Handle CC recipients
        if cc:
            if isinstance(cc, str):
                email_msg["Cc"] = cc
            elif isinstance(cc, list):
                email_msg["Cc"] = ", ".join(cc)

        # Set sender
        if sender_name:
            email_msg["From"] = f"{sender_name} <{from_email}>"
        else:
            email_msg["From"] = from_email

        # Add message body
        email_body = MIMEText(message, "plain")
        email_msg.attach(email_body)

        # Handle attachments
        if attachment_paths:
            for path in attachment_paths:
                if not os.path.exists(path):
                    logger.warning(f"Attachment file not found: {path}")
                    continue

                _, ext = os.path.splitext(path)

                if ext.lower() == ".log":
                    # Special handling for log files (clean ANSI escape sequences)
                    try:
                        with open(path, "r", encoding="utf-8") as file:
                            content = file.read()
                            cleaned_content = ansi_escape.sub("", content)
                            part = MIMEText(cleaned_content, "plain")
                    except UnicodeDecodeError:
                        # If UTF-8 fails, try binary mode
                        with open(path, "rb") as file:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(file.read())
                            encoders.encode_base64(part)
                else:
                    # Handle other file types
                    mime_type, _ = mimetypes.guess_type(path)
                    if mime_type is None:
                        mime_type = "application/octet-stream"
                    main_type, sub_type = mime_type.split("/", 1)

                    with open(path, "rb") as file:
                        part = MIMEBase(main_type, sub_type)
                        part.set_payload(file.read())
                        encoders.encode_base64(part)

                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(path)}",
                )
                email_msg.attach(part)

        # Determine all recipients
        recipients = [to_email]
        if cc:
            if isinstance(cc, str):
                recipients.append(cc)
            elif isinstance(cc, list):
                recipients.extend(cc)

        # Send email
        server.send_message(email_msg, to_addrs=recipients)
        server.quit()

        # Log success
        cc_info = f" (CC: {cc})" if cc else ""
        attachment_info = (
            f" with {len(attachment_paths)} attachments"
            if attachment_paths
            else ""
        )
        logger.success(
            f"Email sent: {from_email} -> {to_email}{cc_info}{attachment_info}"
        )

        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        logger.debug(
            f"Email details: {from_email} -> {to_email}, Subject: {subject}"
        )
        return False


def get_default_from_email() -> str:
    """Get default from email address from environment variables."""
    return os.environ.get("SCITEX_EMAIL_AGENT", "agent@scitex.ai")


def get_default_to_email() -> str:
    """Get default to email address from environment variables."""
    return os.environ.get("SCITEX_EMAIL_YWATANABE", "ywatanabe@scitex.ai")


def get_scitex_email_config() -> dict:
    """Get SciTeX email configuration from environment variables.

    Returns:
        Dictionary with email configuration
    """
    return {
        "admin": os.environ.get("SCITEX_EMAIL_ADMIN", "admin@scitex.ai"),
        "agent": os.environ.get("SCITEX_EMAIL_AGENT", "agent@scitex.ai"),
        "support": os.environ.get("SCITEX_EMAIL_SUPPORT", "support@scitex.ai"),
        "ywatanabe": os.environ.get(
            "SCITEX_EMAIL_YWATANABE", "ywatanabe@scitex.ai"
        ),
        "password": os.environ.get("SCITEX_EMAIL_PASSWORD"),
    }

# EOF
