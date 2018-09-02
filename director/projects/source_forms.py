from lib.forms import ModelFormWithSubmit
from .source_models import FilesSource


class FilesSourceForm(ModelFormWithSubmit):
    class Meta:
        model = FilesSource
        fields = ["project"]

FilesSourceUpdateForm = FilesSourceForm
FilesSourceCreateForm = FilesSourceForm
