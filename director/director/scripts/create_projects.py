from director.models import Project


def run(*args):
    Project.objects.create(
        address='github://michael/documents/welcome-to-stencila',
        gallery=True, public=True
    )
