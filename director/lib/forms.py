import typing

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms


def form_add_submit_button(form: typing.Any) -> None:
    form.helper = FormHelper()
    form.helper.add_input(
        Submit('submit', getattr(form, 'submit_button_label', 'Submit'), css_class='button is-primary')
    )


def form_add_create_button(form: typing.Any) -> None:
    form.helper = FormHelper()
    form.helper.add_input(
        Submit('create', getattr(form, 'create_button_label', 'Create'), css_class='button is-primary')
    )


class FormWithSubmit(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        super(FormWithSubmit, self).__init__(*args, **kwargs)
        form_add_submit_button(self)


class ModelFormWithSubmit(forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super(ModelFormWithSubmit, self).__init__(*args, **kwargs)
        form_add_submit_button(self)


class FormWithCreate(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        super(FormWithCreate, self).__init__(*args, **kwargs)
        form_add_create_button(self)


class ModelFormWithCreate(forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super(ModelFormWithCreate, self).__init__(*args, **kwargs)
        form_add_create_button(self)
