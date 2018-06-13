import re
from . import Storer
from director.models import StencilaProject

class StencilaStorer(Storer):
    code = 'stencila'
    name = 'Stencila'

    def parse_path(self, path):
        self.path = path
        m = re.match('^(?P<owner>[a-z0-9-]+)/(?P<project_name>[a-z0-9-]+)$', self.path)
        if not m:
            return False
        self.owner = m.group('owner')
        self.project_name = m.group('project_name')
        return True

    def file_type(self, f):
        return "file"

    def get_stencila_project(self):
        return StencilaProject.objects.get(owner__username=self.owner, name=self.project_name)

    def get_folder_contents(self, subfolder=None):
        return self.get_stencila_project().list_files()

    def copy_file(self, filename, to):
        outfile = open(to, 'wb')
        self.get_stencila_project().get_file(filename, outfile)
        outfile.close()
