import re
from . import Storer

class DropboxStorer(Storer):
    code = 'dropbox'
    name = 'Dropbox'

    def parse_path(self, path):
        self.path = path
        m = re.match('^(?P<path>\w[\w/_-]+)$', self.path)
        return bool(m)
