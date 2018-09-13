import os.path
from unittest import skip

from django.test import TestCase

from editors.models import NativeEditor

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')


class NativeEditorTestCase(TestCase):
    def setUp(self):
        self.editor = NativeEditor.objects.create()

    @skip
    def test_push(self):
        with open(os.path.join(FIXTURES, 'archive1.zip'), 'rb') as archive:
            self.editor.push(archive)

    @skip
    def test_pull(self):
        archive = self.editor.pull()
        with open(os.path.join(FIXTURES, 'archive1-got.zip'), 'wb') as file:
            file.write(archive.read())
