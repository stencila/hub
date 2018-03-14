import re
from . import Storer

class DropboxStorer(Storer):
    name = 'dropbox'

    def valid_path(self, path):
        self.path = path
        m = re.match('^(?P<path>\w[\w/_-]+)$', self.path)
        return bool(m)
