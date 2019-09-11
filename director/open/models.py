from django.db import models
from django.db.models import PROTECT
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
    original_filename = models.TextField(null=True, blank=True,
                                         help_text='If available, the name of the original file.')
    source_format = models.TextField(null=False, blank=False, help_text='Format that was converted from.')
    target_format = models.TextField(null=False, blank=False, help_text='Format that was converted to.')
    is_deleted = models.BooleanField(null=False, default=False,
                                     help_text='Instead of deleting conversions, this flag should be set so a record '
                                               'still exists for feedback/analytics.')

    def __str__(self):
        return 'Conversion {} / {}'.format(self.pk, self.public_id)

    def clean(self) -> None:
        super().clean()
        self.generate_or_get_public_id()

    def generate_or_get_public_id(self) -> str:
        if not self.public_id:
            self.public_id = ShortId().generate()
        return self.public_id


class ConversionFeedback(models.Model):
    conversion = models.ForeignKey(Conversion, related_name='feedback', on_delete=PROTECT)
    rating = models.IntegerField(help_text='What the user has rated the feedback (1-5).')
    comments = models.TextField(blank=True, null=True, help_text='Comments the user had regarding the conversion.')
    email_address = models.EmailField(blank=True, null=True, help_text='Email address provided with feedback.')
    created = models.DateTimeField(auto_now_add=True, help_text='Date/time the feedback was created.')
