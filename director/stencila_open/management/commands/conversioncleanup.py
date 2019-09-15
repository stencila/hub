from django.core.management.base import BaseCommand

from stencila_open.lib import cleanup_old_conversions


class Command(BaseCommand):
    help = 'Run the stencila_open.lib.cleanup_old_conversions function to delete data for conversions over 24 hours old'

    def handle(self, *args, **options):
        cleanup_old_conversions()
