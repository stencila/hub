import re
from . import Storer

class DropboxStorer(Storer):
    code = 'dropbox'
    name = 'Dropbox'
    unit_name = 'public folder'
    unit_name_plural = 'public folders'

    def parse_path(self, path):
        self.path = path
        m = re.match('^(?P<path>\w[\w/_-]+)$', self.path)
        return bool(m)
