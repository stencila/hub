import re
from . import StorerPathException, Storer

class GithubStorer(Storer):
    name = 'github'
    host = 'api.github.com'

    def __init__(self, path):
        self.path = path
        m = re.match('^(?P<owner>[^/@]+)\/(?P<repo>[^@/]+)(?P<folder>\/[^@]+)?(?P<ref>@\w+)?$', path)
        if not m:
            raise StorerPathException("Github path match failed")
        self.owner = m.group('owner')
        self.repo = m.group('repo')
        self.folder = m.group('folder')
        self.ref = m.group('ref')
        if not self.ref:
            self.ref = 'master'

        self.url = 'https://{}/repos/{}/{}/contents{}'.format(
            self.host, self.owner, self.repo,
            '' if not self.folder else self.folder)
        # TODO ref

    def get_address(self):
        self.address = '{}://{}/{}{}{}'.format(
            self.name, self.owner, self.repo,
            '' if not self.folder else self.folder,
            '' if not self.ref else self.ref)
        return self.address
