import json
import re
from . import Storer

class GithubStorer(Storer):
    name = 'github'

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

    def account_info(self, account):
        return dict(
            username=account.extra_data.get('login', None),
            profile_url=account.extra_data.get('html_url', None))
