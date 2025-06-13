#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 06:33:08 (ywatanabe)"
# File: ./scitex_repo/src/scitex/utils/_email.py

import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase as _MIMEBase
from email.mime.multipart import MIMEMultipart as _MIMEMultipart
from email.mime.text import MIMEText as _MIMEText
import mimetypes

from ..reproduce._gen_ID import gen_ID

import re

ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def send_gmail(
    sender_gmail,
    sender_password,
    recipient_email,
    subject,
    message,
    sender_name=None,
    cc=None,
    ID=None,
    attachment_paths=None,
    verbose=True,
):
    if ID == "auto":
        ID = gen_ID()

    if ID:
        if subject:
            subject = f"{subject} (ID: {ID})"
        else:
            subject = f"ID: {ID}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_gmail, sender_password)

        gmail = _MIMEMultipart()
        gmail["Subject"] = subject
        gmail["To"] = recipient_email
        if cc:
            if isinstance(cc, str):
                gmail["Cc"] = cc
            elif isinstance(cc, list):
                gmail["Cc"] = ", ".join(cc)
        if sender_name:
            gmail["From"] = f"{sender_name} <{sender_gmail}>"
        else:
            gmail["From"] = sender_gmail
        gmail_body = _MIMEText(message, "plain")
        gmail.attach(gmail_body)

        # Attachment files
        if attachment_paths:
            for path in attachment_paths:
                _, ext = os.path.splitext(path)
                if ext.lower() == ".log":
                    with open(path, "r", encoding="utf-8") as file:
                        content = file.read()
                        cleaned_content = ansi_escape.sub("", content)
                        part = _MIMEText(cleaned_content, "plain")

                        # part = _MIMEText(file.read(), 'plain')
                else:
                    mime_type, _ = mimetypes.guess_type(path)
                    if mime_type is None:
                        mime_type = "text/plain"
                    main_type, sub_type = mime_type.split("/", 1)
                    with open(path, "rb") as file:
                        part = _MIMEBase(main_type, sub_type)
                        part.set_payload(file.read())
                        encoders.encode_base64(part)

                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(path)}",
                )
                gmail.attach(part)

        recipients = [recipient_email]
        if cc:
            if isinstance(cc, str):
                recipients.append(cc)
            elif isinstance(cc, list):
                recipients.extend(cc)
        server.send_message(gmail, to_addrs=recipients)

        server.quit()

        if verbose:
            cc_info = f" (CC: {cc})" if cc else ""
            message = f"Email was sent:\n"
            message += f"    {sender_gmail} -> {recipient_email}{cc_info}\n"
            message += f"    (ID: {ID})\n"
            if attachment_paths:
                message += f"    Attached:\n"
                for ap in attachment_paths:
                    message += f"        {ap}\n"
            print(message)

            # message = f"\nEmail was sent:\n\t{sender_gmail} -> {recipient_email}{cc_info}\n\t(ID: {ID})"
            # if attachment_paths:
            #     attachment_paths_str = '\n\t\t'.join(attachment_paths)
            #     message += f"\n\tAttached:\n\t{attachment_paths_str}"
            # print(message)

    except Exception as e:
        print(f"Email was not sent: {e}")


# EOF
