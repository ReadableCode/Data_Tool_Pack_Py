# %%
# Imports #
"""
This has been tested working in a org environment, not tested with this gmail configuration
"""
import os
import sys

# append grandparent
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config_utils  # noqa: F401
import win32com.client as win32
from utils.display_tools import print_logger  # noqa: F401

# %%
# Variables #


def send_email(
    to_address,
    subject,
    body,
    cc_address=None,
    bcc_address=None,
    attachments=None,
):
    """
    Send an email using Outlook.

    Parameters:
    - to_address (str): Recipient email address.
    - subject (str): Subject of the email.
    - body (str): Body content of the email.
    - cc_address (str, optional): CC email address.
    - bcc_address (str, optional): BCC email address.
    - attachments (list of str, optional): List of file paths to attach.

    Returns:
    None
    """
    # Create Outlook COM object
    outlook = win32.Dispatch("Outlook.Application")

    # Create a new mail item
    mail = outlook.CreateItem(0)
    mail.To = to_address
    mail.Subject = subject
    mail.Body = body

    if cc_address:
        mail.CC = cc_address
    if bcc_address:
        mail.BCC = bcc_address
    if attachments:
        for attachment in attachments:
            mail.Attachments.Add(attachment)

    # Send it
    mail.Send()
    print(f"Email sent to {to_address} with subject '{subject}'")


# %%

if __name__ == "__main__":
    # Test / Examples #
    # Create Outlook COM object
    outlook = win32.Dispatch("Outlook.Application")

    # Create a new mail item
    mail = outlook.CreateItem(0)
    mail.To = "test_email@test.com"
    mail.Subject = "Test Email from Python"
    mail.Body = "Hello, this email was sent using Outlook on your computer."

    # Optional: add CC, BCC, attachments
    # mail.CC = "someone_else@example.com"
    # mail.Attachments.Add(r"C:\path\to\file.txt")

    # Send it
    mail.Send()

    print("Email sent!")

# %%
