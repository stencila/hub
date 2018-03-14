import re
from . import Storer

class HubStorer(Storer):
    name = 'hub'

    def __init__(self, path):
        self.path = path

    def valid_path(self):
        m = re.match('^(?P<owner>[a-z0-9-]+)/(?P<project_name>[a-z0-9-]+)$', self.path)
        if not m:
            return False
        self.owner = m.group('owner')
        self.project_name = m.group('project_name')
        return True
