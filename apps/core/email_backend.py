import os
import resend
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMultiAlternatives


class ResendEmailBackend(BaseEmailBackend):
    """
    Custom email backend for sending emails via Resend API.
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = os.getenv('RESEND_API_KEY')
        if self.api_key:
            resend.api_key = self.api_key

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not self.api_key:
            if not self.fail_silently:
                raise ValueError("RESEND_API_KEY environment variable is not set")
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                # Prepare email data for Resend
                email_data = {
                    "from": message.from_email,
                    "to": message.to,
                    "subject": message.subject,
                }

                # Handle HTML and plain text content
                if isinstance(message, EmailMultiAlternatives) and message.alternatives:
                    # Use HTML content if available
                    for content, mimetype in message.alternatives:
                        if mimetype == "text/html":
                            email_data["html"] = content
                            break
                    # Also include plain text
                    if message.body:
                        email_data["text"] = message.body
                else:
                    # Plain text only
                    email_data["text"] = message.body

                # Add CC if present
                if message.cc:
                    email_data["cc"] = message.cc

                # Add BCC if present
                if message.bcc:
                    email_data["bcc"] = message.bcc

                # Add reply-to if present
                if message.reply_to:
                    email_data["reply_to"] = message.reply_to

                # Send via Resend
                resend.Emails.send(email_data)
                num_sent += 1

            except Exception as e:
                if not self.fail_silently:
                    raise e

        return num_sent
