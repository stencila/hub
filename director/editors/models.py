from io import BytesIO
import os
import requests
import sh
import tempfile
from zipfile import ZipFile

from django.db.models import (
    Model,

    CharField,
    ForeignKey,
    FileField,
    TextField,

    CASCADE
)
from polymorphic.models import PolymorphicModel


class Editor(PolymorphicModel):
    """
    An editor
    """

    def push(self, archive):
        """
        Push the archive into the editor
        """
        pass

    def pull(self, archive):
        """
        Pull the archive from the editor
        """
        pass


class NativeEditor(Editor):
    """
    Stencila's native editor
    """

    url = 'http://localhost:4000/edit/storage'

    def push(self, archive):
        """
        Import the archive into the editor by
        extracting it, converting it to Dar, pushing
        it to the editor
        """

        # Create some temporary folders
        src = tempfile.mkdtemp()
        dest = tempfile.mkdtemp()

        # Unzip the src archive
        with ZipFile(archive, mode='r') as zipfile:
            zipfile.extractall(src)

        # Convert to Dar
        sh.stencila.convert(src, dest, to='dar')

        # Read the Dar files and post them to the editor
        # as a new Dar archive
        files = {}
        for folder, subfolders, filenames in os.walk(dest):
            for filename in filenames:
                path = os.path.join(folder, filename)
                relpath = os.path.relpath(path, folder)
                files[relpath] = (relpath, open(path, 'rb'))
        response = requests.post('{}/{}'.format(self.url, self.id), files=files)
        response.raise_for_status()
