import re
from . import Storer

class HubStorer(Storer):
    name = 'hub'

    def valid_path(self, path):
        self.path = path
        m = re.match('^(?P<owner>[a-z0-9-]+)/(?P<project_name>[a-z0-9-]+)$', self.path)
        if not m:
            return False
        self.owner = m.group('owner')
        self.project_name = m.group('project_name')
        return True

    def prefix(self, owner, project_name):
        return "%s/%s" % (owner.username, project_name)

    def address(self, owner, project_name):
        prefix = self.prefix(owner, project_name)
        return "%s://%s" % (self.name, prefix)
