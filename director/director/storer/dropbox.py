import re
from . import Storer

class DropboxStorer(Storer):
    name = 'dropbox'

    def __init__(self, path):
        self.path = path

    def valid_path(self):
        m = re.match('^(?P<path>\w[\w/_-]+)$', self.path)
        return bool(m)
