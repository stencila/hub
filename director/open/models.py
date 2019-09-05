from django.db import models
from shortid import ShortId


class Conversion(models.Model):
    public_id = models.TextField(unique=True,
                                 help_text='A unique id used when sharing this Conversion.')
    input_url = models.URLField(null=True, blank=True,
                                help_text='The original URL this content was converted from. Mutually exclusive with '
                                          'source_file.')
    input_file = models.TextField(null=True, blank=True,
                                  help_text='The path to the file this content was converted from. Mutually exclusive '
                                            'with source_url')
    output_file = models.TextField(null=True, blank=True,
                                   help_text='The path to the converted file.')
    stderr = models.TextField(null=True, blank=True, help_text='Stderr output from the conversion process.')
    stdout = models.TextField(null=True, blank=True, help_text='Stdout output from the conversion process.')
    has_warnings = models.BooleanField(null=False,
                                       help_text='If the conversion generated warnings then this should be True')
    created = models.DateTimeField(auto_now_add=True, help_text='Date/time the conversion was performed.')
    meta = models.TextField(null=True, blank=True,
                            help_text='Any extra arbitrary metadata about the conversion that might be useful. Should '
                                      'be JSON encoded.')

    def clean(self) -> None:
        super().clean()
        self.generate_or_get_public_id()

    def generate_or_get_public_id(self) -> str:
        if not self.public_id:
            self.public_id = ShortId().generate()
        return self.public_id
