from django.dispatch import Signal

"""
A signal sent when an email is POSTed to /api/emails.

The `email` argument is a dictionary with keys created by SendGrid
by parsing the raw email.
See https://sendgrid.com/docs/for-developers/parsing-email/setting-up-the-inbound-parse-webhook/#default-parameters

Use it like this:

    from django.dispatch import receiver
    from manager.signals import email_received

    @receiver(email_received)
    def my_email_processing_function(sender, email):
        print(f"Email received from {email['from']}")
"""
email_received = Signal()
