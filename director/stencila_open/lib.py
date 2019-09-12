import logging
import os
import re
import typing
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from stencila_open.models import Conversion

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
        if not re.match(r'^([a-z0-9_\-]{7,14})', public_id, re.I):
            raise ValueError('ID should not contain any bad characters.')

        return os.path.join(self.root, CONVERSION_STORAGE_SUBDIR, *list(public_id[:2]))

    def create_save_directory(self, public_id: str) -> None:
        os.makedirs(self.generate_save_directory(public_id), exist_ok=True)

    def generate_save_path(self, public_id, filename: typing.Optional[str] = None) -> str:
        filename = filename or public_id
        return os.path.join(self.generate_save_directory(public_id), filename)

    def move_file_to_public_id(self, source: str, public_id: str, filename: typing.Optional[str] = None) -> str:
        """
        Move a file to its permanent conversion results location.

        Encoda does the file writing itself to a temp file. After that is complete, this should be called to do the
        move. This is why the file has an `open` (read) but no `write` method.
        """
        self.create_save_directory(public_id)
        save_path = self.generate_save_path(public_id, filename)
        os.rename(source, save_path)
        return save_path


def cleanup_old_conversions():
    old_conversions = Conversion.objects.filter(created__lte=timezone.now() - MAX_AGE)

    with transaction.atomic():
        for conversion in old_conversions:
            if conversion.input_file:
                exception_handling_unlink(conversion.input_file, 'conversion input')

            if conversion.output_file:
                exception_handling_unlink(conversion.output_file, 'conversion output')
                exception_handling_unlink(conversion.output_file + '.json', 'conversion intermediary')

            conversion.is_deleted = True
            conversion.save()
