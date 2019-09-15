import logging
import os
import re
import shutil
from datetime import timedelta
from os.path import dirname, basename

from django.db import transaction
from django.utils import timezone

from stencila_open.models import Conversion, PUBLIC_ID_LENGTH

MAX_AGE = timedelta(days=1)

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

CONVERSION_STORAGE_SUBDIR = 'conversions'


def exception_handling_unlink(path: str, file_description: str) -> None:
    if os.path.exists(path):
        try:
            os.unlink(path)
        except OSError:
            LOGGER.exception('Error unlinking %s %s', file_description, path)


class ConversionFileStorage:
    root: str

    def __init__(self, root: str):
        self.root = root

    def generate_save_directory(self, public_id: str) -> str:
        if not re.match(r'^([a-z0-9]{' + str(PUBLIC_ID_LENGTH) + '})', public_id, re.I):
            raise ValueError(
                'ID should not contain any bad characters and must be of length {}.'.format(PUBLIC_ID_LENGTH))

        return os.path.join(self.root, CONVERSION_STORAGE_SUBDIR, public_id[0], public_id[1], public_id)

    def create_save_directory(self, public_id: str) -> None:
        os.makedirs(self.generate_save_directory(public_id), exist_ok=True)

    def generate_save_path(self, public_id, filename: str) -> str:
        return os.path.join(self.generate_save_directory(public_id), filename)

    def copy_file_to_public_id(self, source: str, public_id: str, filename: str) -> str:
        """
        Copy a file or directory to its permanent conversion results location.

        Encoda does the file writing itself to a temp file. After that is complete, this should be called to do the
        copy. This is why the file has an `open` (read) but no `write` method.
        """
        self.create_save_directory(public_id)
        save_path = self.generate_save_path(public_id, filename)
        if os.path.isdir(source):
            shutil.copytree(source, save_path)
        else:
            shutil.copy(source, save_path)
        return save_path


def cleanup_old_conversions() -> None:
    old_conversions = Conversion.objects.filter(created__lte=timezone.now() - MAX_AGE, is_example=False)

    with transaction.atomic():
        for conversion in old_conversions:
            if not conversion.output_file:
                continue

            conversion_dir = dirname(conversion.output_file)
            if basename(conversion_dir) == conversion.public_id:
                # new style where everything is stored in a single directory, so just delete it
                shutil.rmtree(conversion_dir)
            else:
                # unlink all the pieces
                if conversion.input_file:
                    exception_handling_unlink(conversion.input_file, 'conversion input')

                if conversion.output_file:
                    exception_handling_unlink(conversion.output_file, 'conversion output')
                    exception_handling_unlink(conversion.output_file + '.json', 'conversion intermediary')

            conversion.is_deleted = True
            conversion.save()
