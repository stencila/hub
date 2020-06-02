from rest_framework.routers import SimpleRouter


class OptionalSlashRouter(SimpleRouter):
    """
    A router that allows for an optional trailing slash.

    HT to https://stackoverflow.com/questions/46163838.
    """

    def __init__(self):
        super().__init__()
        self.trailing_slash = "/?"
