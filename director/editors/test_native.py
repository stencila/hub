import os.path
from django.test import TestCase

from editors.models import NativeEditor

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')


class NativeEditorTestCase(TestCase):
    def setUp(self):
        self.editor = NativeEditor.objects.create()

    def test_push(self):
        with open(os.path.join(FIXTURES, 'archive1.zip'), 'rb') as archive:
            self.editor.push(archive)
