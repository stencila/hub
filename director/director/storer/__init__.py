import requests

class StorerException(Exception):
    pass

class StorerPathException(StorerException):
    pass

class Storer(object):
    def __init__(self):
        self.url = None

    def __unicode__(self):
        return "Storer {}/{}".format(self.name, self.path)

from .github import GithubStorer
storers = {s.name: s for s in (GithubStorer,)}
