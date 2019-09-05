from urllib.parse import urlparse

from django import forms

from lib.converter_facade import is_malicious_host


class UrlForm(forms.Form):
    url = forms.URLField(widget=forms.TextInput(attrs={'placeholder': 'https://...', 'class': 'input'}))

    def clean_url(self):
        url = self.cleaned_data['url']
        url_obj = urlparse(url)
        if url_obj.scheme.lower() not in ('https', 'http'):
            raise forms.ValidationError('URL scheme must be "http" or "https"')

        if is_malicious_host(url_obj.hostname):
            raise forms.ValidationError('{} is not a valid hostname.'.format(url_obj.hostname))
        return url


class FileForm(forms.Form):
    file = forms.FileField()
