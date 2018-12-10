import os
import secrets
import shutil
import string
import tempfile
from io import BytesIO
from zipfile import ZipFile

import requests
import sh
from django.conf import settings
from django.db.models import (
    CharField,
    URLField
)
from polymorphic.models import PolymorphicModel


class Editor(PolymorphicModel):
    """
    A project editor.

    There will be several classes of editors (e.g. Texture, Google Sheets)
    derived from this base class. Each editor instance is actually an editor
    "session" and will map directly to a document for that editor class
    (e.g. a Google sheet).

    Each editor class will implement a `push` method
    to create that external document, and a `pull` method` to convert it
    back to the project's native format. If necessary the editor will need
    to keep a record of the file names / formats to convert back to.
    """

    url = URLField(
        help_text='URL of the editor session'
    )

    @staticmethod
    def create(type):
        """Create a new editor of the given type."""
        if type == 'native':
            return NativeEditor.objects.create()
        else:
            raise RuntimeError('Unhandled type "{}" when attempting to create editor'.format(type))

    def push(self, archive):
        """
        Push the archive into the editor.

        This method must be implemented by each editor class.
        """
        raise NotImplementedError('Push is not implemented for class {}'.format(self.__class__.__name__))

    def pull(self, archive):
        """
        Pull the archive from the editor.

        This method must be implemented by each editor class.
        """
        raise NotImplementedError('Pull is not implemented for class {}'.format(self.__class__.__name__))


class NativeEditor(Editor):
    """
    Stencila's native editor based on Substance/Texture editor.

    which operates on Reproducible Document Archives (Dar).
    """

    # URL of the editor role (see Node.js `hub/editor` in this
    # repo). Used to push file to editor and
    # redirect browser window to the editor.
    base_url = settings.CALLBACK_URL + '/edit'

    # Key used to identify the Dar in the editor
    key = CharField(
        max_length=32,
        help_text='A secret key to access this checkout'
    )

    def save(self, *args, **kwargs):
        """Override of the Django Model `save` method to create a unique key for the editor instance."""
        if not self.key:
            self.key = ''.join(
                secrets.choice(string.ascii_lowercase + string.digits) for _ in range(32)
            )
        super().save(*args, **kwargs)

    def push(self, archive):
        """
        Push a project archive to the editor.

        :param archive: A zip archive of the project
        """
        # Create some temporary folders
        tmp = tempfile.mkdtemp()
        src = os.path.join(tmp, 'src')
        os.makedirs(src)
        dest = os.path.join(tmp, 'dest.dar')
        os.makedirs(dest)

        # Unzip the src archive
        with ZipFile(archive, 'r') as zipfile:
            zipfile.extractall(src)

        # Convert to Dar
        if os.path.exists(os.path.join(src, 'manifest.xml')):
            # Already a Dar, just copy it over
            sh.cp('-R', src, dest)
        else:
            # Convert to Dar
            sh.stencila.convert(src, dest, '--to', 'dar')

        # Read the Dar files and post them to the editor
        # as a new Dar archive
        files = {}
        for folder, subfolders, filenames in os.walk(dest):
            for filename in filenames:
                path = os.path.join(folder, filename)
                relpath = os.path.relpath(path, folder)
                files[relpath] = (relpath, open(path, 'rb'))
        response = requests.post(
            '{}/storage/{}'.format(self.base_url, self.key),
            files=files
        )
        response.raise_for_status()

        # Set URL for user to access the editor checkout session
        self.url = '{}/?project={}&host={}&checkout={}&key={}'.format(
            self.base_url,
            self.checkout.project.get_name(),
            self.checkout.host.url(),
            self.checkout.get_callback_url(),
            self.key
        )
        self.save()

        # Clean up
        shutil.rmtree(tmp)

    def pull(self):
        """
        Pull the project archive from the editor.

        :return: A zip archive of the project
        """
        # Get the Dar from the editor
        response = requests.get(
            '{}/storage/{}'.format(self.base_url, self.key)
        )
        response.raise_for_status()
        data = response.json()

        # Create some temporary folders
        tmp = tempfile.mkdtemp()
        src = os.path.join(tmp, 'src.dar')
        os.makedirs(src)
        dest = os.path.join(tmp, 'dest')
        os.makedirs(dest)

        # Write the Dar to disk
        for name, details in data['resources'].items():
            path = os.path.join(src, name)
            with open(path, 'w', encoding='utf-8') as file:
                file.write(details['data'])

        # Convert to Dar
        # sh.stencila.convert(src, dest, '--from', 'dar')
        sh.cp('-R', src, dest)

        # Bundle the Dar folder into a zip archive
        archive = BytesIO()
        with ZipFile(archive, 'w') as zipfile:
            for folder, subfolders, filenames in os.walk(dest):
                for filename in filenames:
                    path = os.path.join(folder, filename)
                    relpath = os.path.relpath(path, folder)
                    zipfile.write(path, relpath)
        archive.seek(0)

        # Clean up
        shutil.rmtree(tmp)

        return archive
