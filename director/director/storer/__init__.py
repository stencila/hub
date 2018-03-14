class Storer(object):

    def __init__(self):
        self.url = None

    def __unicode__(self):
        return "Storer {}".format(self.name)

from .github import GithubStorer
from .dropbox import DropboxStorer
from .stencila import StencilaStorer

storers = {s.name: s for s in (GithubStorer, DropboxStorer, StencilaStorer)}
