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
            print("{} {}".format(response.status_code, repos_url))
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
        return [] # TODO Send authenticated request to branch url to avoid rate limiting
        if not self.repo or not self.owner:
            return
        branches_url = "https://api.github.com/repos/{}/{}/branches".format(
            self.owner, self.repo)
        response = requests.get(branches_url)
        if response.status_code != 200:
            print("{} {}".format(response.status_code, branches_url))
            return
        branches = json.loads(response.content.decode('utf-8'))
        return [{'ref': b['name']} for b in branches]

    def folder_address(self, folder):
        folder = "/" + folder if len(folder) else ""
        return "github://{}/{}".format(self.owner, self.repo) \
          + folder + "@" + self.ref

    def folder_contents(self):
        contents_url = "https://api.github.com/repos/{}/{}/contents/{}?ref={}".format(
            self.owner, self.repo, self.folder, self.ref)
        response = requests.get(contents_url)
        if response.status_code != 200:
            print("{} {}".format(response.status_code, contents_url))
            return

        contents = json.loads(response.content.decode('utf-8'))
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

class GithubStorerAddressForm(forms.Form):
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
