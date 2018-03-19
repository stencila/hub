import re
from . import Storer

class DropboxStorer(Storer):
    code = 'dropbox'
    name = 'Dropbox'

    def valid_path(self, path):
        self.path = path
        m = re.match('^(?P<path>\w[\w/_-]+)$', self.path)
        return bool(m)
