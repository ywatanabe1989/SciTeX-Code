#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-15 20:25:22 (ywatanabe)"
# File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/SciTeX-Code/src/scitex/utils/_notify.py
# ----------------------------------------
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Time-stamp: "2024-11-24 17:54:38 (ywatanabe)"

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/utils/_notify.py"

# Time-stamp: "2024-11-07 05:38:14 (ywatanabe)"

"""This script does XYZ."""

import inspect
import pwd
import socket
import subprocess
import sys
import warnings

from ._email import send_gmail


def get_username():
    try:
        return pwd.getpwuid(os.getuid()).pw_name
    except:
        return os.getenv("USER") or os.getenv("LOGNAME") or "unknown"


def get_hostname():
    return socket.gethostname()


def get_git_branch(scitex):
    try:
        branch = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=scitex.__path__[0],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
        return branch

    except Exception as e:
        print(e)
        return "main"


def gen_footer(sender, script_name, scitex, branch):
    return f"""

{'-'*30}
Sent via
- Host: {sender}
- Script: {script_name}
- Source: scitex v{scitex.__version__} (github.com/ywatanabe1989/scitex/blob/{branch}/src/scitex/gen/system_ops/_notify.py)
{'-'*30}"""


# This is an automated system notification. If received outside working hours, please disregard.


def notify(
    subject="",
    message=":)",
    file=None,
    ID="auto",
    sender_name=None,
    recipient_email=None,
    cc=None,
    attachment_paths=None,
    verbose=False,
):
    import scitex

    try:
        message = str(message)
    except Exception as e:
        warnings.warn(str(e))

    FAKE_PYTHON_SCRIPT_NAME = "$ python -c ..."
    sender_gmail = os.getenv("SCITEX_SENDER_GMAIL")
    sender_password = os.getenv("SCITEX_SENDER_GMAIL_PASSWORD")
    recipient_email = recipient_email or os.getenv("SCITEX_RECIPIENT_GMAIL")

    if file is not None:
        script_name = str(file)
    else:
        if sys.argv[0]:
            script_name = os.path.basename(sys.argv[0])
        else:
            frames = inspect.stack()
            script_name = (
                os.path.basename(frames[-1].filename)
                if frames
                else "(Not found)"
            )
        if (script_name == "-c") or (not script_name.endswith(".py")):
            script_name = FAKE_PYTHON_SCRIPT_NAME

    sender = f"{get_username()}@{get_hostname()}"
    branch = get_git_branch(scitex)
    footer = gen_footer(sender, script_name, scitex, branch)

    full_message = script_name + "\n\n" + message + "\n\n" + footer
    full_subject = (
        f"{script_name}—{subject}"
        if subject and (script_name != FAKE_PYTHON_SCRIPT_NAME)
        else f"{subject}"
    )

    if sender_gmail is None or sender_password is None:
        print(
            f"""
        Please set environmental variables to use this function (f"{inspect.stack()[0][3]}"):\n\n
        $ export SciTeX_SENDER_GMAIL="scitex.notification@gmail.com"
        $ export SciTeX_SENDER_GMAIL_PASSWORD="YOUR_APP_PASSWORD"
        $ export SciTeX_RECIPIENT_GMAIL="YOUR_GMAIL_ADDRESS"
        """
        )

    send_gmail(
        sender_gmail,
        sender_password,
        recipient_email,
        full_subject,
        full_message,
        sender_name=sender_name,
        cc=cc,
        ID=ID,
        attachment_paths=attachment_paths,
        verbose=verbose,
    )


if __name__ == "__main__":
    notify(verbose=True)

    # python -c "; scitex.gen.notify()"


# # Example in shell
# #!/bin/bash
# # /home/ywatanabe/.dotfiles/.bin/notify
# # Author: ywatanabe (ywatanabe@scitex.ai)
# # Date: $(date +"%Y-%m-%d-%H-%M")

# # LOG_FILE="${0%.sh}.log"

# usage() {
#     echo "Usage: $0 [-s|--subject <subject>] [-m|--message <message>] [-r|--recipient-name <name>] [-t|--to <email>] [-c|--cc <email>] [-h|--help]"
#     echo "Options:"
#     echo "  -s, --subject   Subject of the notification (default: 'Subject')"
#     echo "  -m, --message   Message body of the notification (default: 'Message')"
#     echo "  -t, --to        The email address of the recipient"
#     echo "  -c, --cc        CC email address(es) (can be used multiple times)"
#     echo "  -h, --help      Display this help message"
#     echo
#     echo "Example:"
#     echo "  $0 -s \"About the Project A\" -m \"Hi, ...\" -r \"John\" -t \"john@example.com\" -c \"cc1@example.com\" -c \"cc2@example.com\""
#     echo "  $0 -s \"Notification\" -m \"This is a notification from ...\" -r \"Team\" -t \"team@example.com\""
#     exit 1
# }

# main() {
#     subject="Subject"
#     message="Message"
#     recipient_email=""
#     cc_addresses=()

#     while [[ $# -gt 0 ]]; do
#         case $1 in
#             -s|--subject)
#                 shift
#                 subject=""
#                 while [[ $# -gt 0 && ! $1 =~ ^- ]]; do
#                     subject+="$1 "
#                     shift
#                 done
#                 subject=${subject% }
#                 ;;
#             -m|--message)
#                 shift
#                 message=""
#                 while [[ $# -gt 0 && ! $1 =~ ^- ]]; do
#                     message+="$1 "
#                     shift
#                 done
#                 message=${message% }
#                 ;;
#             -t|--to)
#                 shift
#                 recipient_email="$1"
#                 shift
#                 ;;
#             -c|--cc)
#                 shift
#                 cc_addresses+=("$1")
#                 shift
#                 ;;
#             -h|--help)
#                 usage
#                 ;;
#             *)
#                 echo "Unknown option: $1"
#                 usage
#                 ;;
#         esac
#     done

#     subject=$(echo "$subject" | sed "s/'/'\\\\''/g")
#     message=$(echo "$message" | sed "s/'/'\\\\''/g")
#     recipient_email=$(echo "$recipient_email" | sed "s/'/'\\\\''/g")
#     cc_string=$(IFS=,; echo "${cc_addresses[*]}" | sed "s/'/'\\\\''/g")

#     python -c "
#

# cc_list = [$(printf "'%s', " "${cc_addresses[@]}")]
# cc_list = [addr.strip() for addr in cc_list if addr.strip()]

# scitex.gen.notify(
#     subject='$subject',
#     message='$message',
#     ID=None,
#     recipient_email='$recipient_email',
#     cc=cc_list
# )
# "
# }

# main "$@"
# # { main "$@"; } 2>&1 | tee "$LOG_FILE"

#

# EOF
