from lib.forms import ModelFormWithSubmit
from .models import Project


class ProjectCreateForm(ModelFormWithSubmit):

    class Meta:
        model = Project
        fields = ['account', 'name']
