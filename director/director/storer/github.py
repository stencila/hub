import json
import re

from django import forms
import requests

from . import Storer

class GithubStorer(Storer):
    code = 'github'
    name = 'GitHub'
    unit_name = 'public repository'
    unit_name_plural = 'public repositories'

    def parse_path(self, path):
        self.path = path
        m = re.match('^(?P<owner>[^/@]+)\/(?P<repo>[^@/]+)(?P<folder>\/[^@]+)?(?P<ref>@\w+)?$', self.path)
        if not m:
            return False
        self.owner = m.group('owner')
        self.repo = m.group('repo')
        _folder = m.group('folder')
        self.folder = _folder[1:] if _folder else ''
        _ref = m.group('ref')
        self.ref = _ref[1:] if _ref else 'master'

        return True

    def username(self):
        return self.account.extra_data.get('login')

    def profile_url(self):
        return self.account.extra_data.get('profile_url')

    def units(self):
        repos_url = self.account.extra_data.get('repos_url')
        response = requests.get(repos_url)
        if response.status_code != 200:
            return
        repos = json.loads(response.content.decode('utf-8'))
        units = []
        for r in repos:
            form = self.get_form(dict(
                repo=r['full_name'], ref=r.get('default_branch', 'master')))
            units.append(dict(name=r['full_name'], url=r['html_url'], form=form))
        return units

    def get_form(self, initial):
        return GithubStorerAddressForm(initial)

class GithubStorerAddressForm(forms.Form):
    repo = forms.CharField(max_length=255, required=True, widget=forms.HiddenInput())
    subfolder = forms.CharField(max_length=255, required=False)
    ref = forms.CharField(max_length=255, required=False)

    def get_address(self):
        address = "github://{}".format(self.cleaned_data['repo'])
        if self.cleaned_data['subfolder']:
            address += "/" + self.cleaned_data['subfolder']
        if self.cleaned_data['ref']:
            address += "@" + self.cleaned_data['ref']
        return address
