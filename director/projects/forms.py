from django import forms


class ProjectCreateForm(forms.Form):
    files_field = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True})
    )
