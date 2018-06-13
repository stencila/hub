import json
import os
import re

from django import forms
from django.conf import settings
import requests

from allauth.socialaccount.models import SocialApp
from . import Storer

class GithubStorer(Storer):
    code = 'github'
    name = 'GitHub'
    unit_name = 'public repository'
    unit_name_plural = 'public repositories'

    def parse_path(self, path):
        self.path = path
        m = re.match('^(?P<owner>[^/@]+)\/(?P<repo>[^@/]+)(?P<folder>\/[^@]+)?(?P<ref>@[-\w]+)?$', self.path)
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

    def add_site_oauth_params(self, url, censored=False):
        if censored:
            client_id = "xxxx"
            client_secret = "yyyy"
        else:
            gh = SocialApp.objects.get_current('github')
            client_id = gh.client_id
            client_secret = gh.secret
        sep = '&' if '?' in url else '?'
        return url + sep + "client_id={}&client_secret={}".format(client_id, client_secret)

    def api_get(self, url, authenticate=True):
        if authenticate:
            request_url = self.add_site_oauth_params(url)
            display_url = self.add_site_oauth_params(url, censored=True)
        else:
            request_url = url
            display_url = url
        response = requests.get(request_url)
        if response.status_code != 200:
            self.log_json(dict(
                message="Request failed",
                url=display_url, status_code=response.status_code))
        return response

    def units(self):
        repos_url = self.account.extra_data.get('repos_url')
        response = self.api_get(repos_url)
        if response.status_code != 200:
            return
        repos = json.loads(response.content.decode('utf-8'))
        units = []
        for r in repos:
            open_form = self.get_open_form(dict(
                repo=r['full_name'], ref=r.get('default_branch', 'master')))
            browse_form = self.get_browse_form(dict(
                repo=r['full_name'], ref=r.get('default_branch', 'master')))
            units.append(dict(
                name=r['full_name'], url=r['html_url'],
                open_form=open_form, browse_form=browse_form))
        return units

    def refs(self):
        if not self.repo or not self.owner:
            return
        branches_url = "https://api.github.com/repos/{}/{}/branches".format(
            self.owner, self.repo)
        response = self.api_get(branches_url)
        if response.status_code != 200:
            return
        branches = json.loads(response.content.decode('utf-8'))
        ref_choices = [(b['name'], b['name']) for b in branches]
        return dict(form=self.get_refs_form(ref_choices, initial=dict(
            repo="{}/{}".format(self.owner, self.repo),
            subfolder=self.folder, ref=self.ref, ref_changed=True)))

    def folder_address(self, folder):
        folder = "/" + folder if len(folder) else ""
        return "github://{}/{}".format(self.owner, self.repo) \
          + folder + "@" + self.ref

    def get_folder_contents(self, subfolder=None):
        folder = self.folder if subfolder is None else subfolder
        contents_url = "https://api.github.com/repos/{}/{}/contents/{}?ref={}".format(
            self.owner, self.repo, folder, self.ref)
        response = self.api_get(contents_url)
        if response.status_code != 200:
            return
        return json.loads(response.content.decode('utf-8'))

    def folder_contents(self):
        contents = self.get_folder_contents()
        result = []
        keys = ('name', 'type', 'size')

        if len(self.folder):
            parent = "/".join(self.folder.split("/")[:-1])
            result.append(dict(
                name="..", address=self.folder_address(parent), type="dir", size=0))

        for item in contents:
            filedata = {k: item[k] for k in keys}
            if item['type'] == "dir":
                filedata['browse_form'] = self.get_browse_form(dict(
                    repo="{}/{}".format(self.owner, self.repo),
                    subfolder=item['path'], ref=self.ref))
                filedata['open_form'] = self.get_browse_form(dict(
                    repo="{}/{}".format(self.owner, self.repo),
                    subfolder=item['path'], ref=self.ref))
                filedata['address'] = self.folder_address(item['path'])
            result.append(filedata)
        return result

    def get_open_form(self, initial):
        return GithubStorerAddressForm(initial)

    def get_browse_form(self, initial):
        return GithubStorerAddressForm(initial)

    def get_refs_form(self, refs, initial):
        return GithubStorerRefsForm(refs, initial)

    def file_contents(self, filename):
        contents_url = "https://raw.githubusercontent.com/{}/{}/{}/{}".format(
            self.owner, self.repo, self.ref, filename)
        response = self.api_get(contents_url, authenticate=False)
        if response.status_code != 200:
            return
        return response.content

class GithubStorerAddressForm(forms.Form):
    ref_changed = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    repo = forms.CharField(max_length=255, required=True, widget=forms.HiddenInput())
    subfolder = forms.CharField(max_length=255, required=False, widget=forms.HiddenInput())
    ref = forms.CharField(max_length=255, required=True, widget=forms.HiddenInput())

    def get_address(self):
        address = "github://{}".format(self.cleaned_data['repo'])
        if self.cleaned_data['subfolder']:
            address += "/" + self.cleaned_data['subfolder']
        if self.cleaned_data['ref']:
            address += "@" + self.cleaned_data['ref']
        return address

class GithubStorerRefsForm(GithubStorerAddressForm):

    def __init__(self, refs, *args, **kwargs):
        super(GithubStorerRefsForm, self).__init__(*args, **kwargs)
        self.fields['ref'] = forms.ChoiceField(choices=refs)
