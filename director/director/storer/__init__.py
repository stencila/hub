import os
from django.conf import settings

class Storer(object):
    code = None
    name = '?'

    def __init__(self, account=None):
        self.url = None
        self.account = account

    def __unicode__(self):
        return "Storer {}".format(self.name)

    def username(self):
        pass

    def profile_url(self):
        pass

    def refs(self):
        return []

    @classmethod
    def get_instance_by_provider(cls, provider, **kwargs):
        for subclass in cls.__subclasses__():
            if provider == subclass.code:
                return subclass(**kwargs)
        raise RuntimeError("Storer for {} not found".format(provider))

    @classmethod
    def get_instance_by_address(cls, address):
        try:
            proto, path = address.split("://")
        except ValueError:
            raise RuntimeError("Bad address {}".format(address))
        instance = cls.get_instance_by_provider(proto)
        if not instance.parse_path(path):
            raise RuntimeError("Bad address {}".format(address))
        return instance

    @classmethod
    def get_instance_by_account(cls, account):
        return cls.get_instance_by_provider(account.provider, account=account)

    def file_type(self, f):
        return f['type']

    def file_name(self, f):
        return f['name']

    def file_size(self, f):
        return f['size']

    def copy_file(self, filename, to):
        contents = self.file_contents(filename)
        outfile = open(to, 'wb')
        outfile.write(contents)
        outfile.close()

    def copy_files(self, local_folder, remote_folder=''):
        filelist = self.get_folder_contents(remote_folder)
        copied = []

        for f in filelist:
            if self.file_type(f) != "file":
                continue
            for ext in settings.UNCONVERTIBLE_FILE_TYPES:
                if self.file_name(f).endswith(ext):
                    continue
            if self.file_size(f) > settings.CONVERT_MAX_SIZE:
                continue
            if not os.path.exists(local_folder):
                try:
                    os.makedirs(local_folder)
                except FileExistsError:
                    pass
            local_filename = os.path.join(local_folder, self.file_name(f))
            remote_filename = os.path.join(remote_folder, self.file_name(f))
            self.copy_file(remote_filename, local_filename)
            copied.append(remote_filename)

        for f in filelist:
            if self.file_type(f) != "dir":
                continue
            remote_subfolder = os.path.join(remote_folder, self.file_name(f))
            local_subfolder = os.path.join(local_folder, self.file_name(f))
            copied += self.copy_files(local_subfolder, remote_subfolder)

        return copied

    def ui_convert(self, key):
        source_folder = os.path.join(settings.CONVERT_WORKDIR, key, 'source')
        os.makedirs(source_folder)
        copied = self.copy_files(source_folder)
        # convert files

from .github import GithubStorer
from .dropbox import DropboxStorer
from .google import GoogleStorer
from .stencila import StencilaStorer
