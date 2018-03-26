import json
import re

import requests

from . import Storer

class GithubStorer(Storer):
    code = 'github'
    name = 'GitHub'
    unit_name = 'public repository'
    unit_name_plural = 'public repositories'

    def valid_path(self, path):
        self.path = path
        m = re.match('^(?P<owner>[^/@]+)\/(?P<repo>[^@/]+)(?P<folder>\/[^@]+)?(?P<ref>@\w+)?$', self.path)
        if not m:
            return False
        self.owner = m.group('owner')
        self.repo = m.group('repo')
        self.folder = m.group('folder')
        self.ref = m.group('ref')
        if not self.ref:
            self.ref = 'master'

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
        units = [dict(name=r['full_name'], url=r['html_url']) for r in repos]
        return units
