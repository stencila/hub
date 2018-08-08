import unittest

from director.scripts.anonymize_test_emails import anonymize_email


class AnonymizeTestEmailsTest(unittest.TestCase):
    def test_anonymize_email(self):
        """Test that an email address has the @ replaced and domain set to example.com"""
        self.assertEqual("user.host.com@example.com", anonymize_email("user@host.com"))
