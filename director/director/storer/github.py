import re
from . import Storer

class GithubStorer(Storer):
    name = 'github'

    def __init__(self, path):
        self.path = path

    def valid_path(self):
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
