import typing

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms


def form_add_submit_button(form: typing.Any) -> None:
    form.helper = FormHelper()
    form.helper.add_input(
        Submit('submit', getattr(form, 'submit_button_label', 'Submit'), css_class='button is-primary')
    )


class FormWithSubmit(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        super(FormWithSubmit, self).__init__(*args, **kwargs)
        form_add_submit_button(self)


class ModelFormWithSubmit(forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super(ModelFormWithSubmit, self).__init__(*args, **kwargs)
        form_add_submit_button(self)
