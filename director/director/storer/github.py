import json
import re
from . import Storer

class GithubStorer(Storer):
    code = 'github'
    name = 'GitHub'

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
