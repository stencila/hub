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

    def fetch_url(self):
        return requests.get(self.url)

    def is_accessible(self):
        return self.fetch_url().status_code == 200

from .github import GithubStorer
storers = {s.name: s for s in (GithubStorer,)}
