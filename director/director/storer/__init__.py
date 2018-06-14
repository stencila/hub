import datetime
import json
import os
import subprocess
import sys
from contextlib import redirect_stdout
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

    def workdir_path(self, f):
        return os.path.join(settings.CONVERT_WORKDIR, f)

    def copy_file(self, filename, to):
        to = self.workdir_path(to)
        contents = self.file_contents(filename)
        outfile = open(to, 'wb')
        outfile.write(contents)
        outfile.close()

    def makedirs(self, folder):
        folder = self.workdir_path(folder)
        if os.path.exists(folder):
            return
        try:
            os.makedirs(folder)
        except FileExistsError:
            pass

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
            self.makedirs(local_folder)
            local_filename = os.path.join(local_folder, self.file_name(f))
            remote_filename = os.path.join(remote_folder, self.file_name(f))
            self.copy_file(remote_filename, local_filename)
            copied.append(remote_filename)
        self.log_json(dict(message="Copied %d files from /%s" % (len(copied), remote_folder)))

        for f in filelist:
            if self.file_type(f) != "dir":
                continue
            remote_subfolder = os.path.join(remote_folder, self.file_name(f))
            local_subfolder = os.path.join(local_folder, self.file_name(f))
            copied += self.copy_files(local_subfolder, remote_subfolder)

        return copied

    def log_json(self, data, file=None):
        data['time'] = datetime.datetime.now().isoformat()
        print(json.dumps(data), file=file)

    def ui_convert(self, key):
        source_folder = os.path.join(key, 'source')
        self.makedirs(source_folder)
        log_file = self.workdir_path(os.path.join(key, 'log.json'))
        with open(log_file, 'w', 1) as stdout, redirect_stdout(stdout):
            copied = self.copy_files(source_folder)

        # Create an EDF which will be used as the canonical
        # source for all conversions
        edf_folder = os.path.join(key, '.edf')
        cmd = [
            "stencila", "convert",
            self.workdir_path(source_folder),
            self.workdir_path(edf_folder)]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        # Create a DAR for the editor to work on
        dar_folder = os.path.join(key, '.dar')
        cmd = [
            "stencila", "convert",
            self.workdir_path(edf_folder),
            self.workdir_path(dar_folder)]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        #print(stdout, file=sys.stdout)
        #print(stderr, file=sys.stderr)

        # Create a symlink from `storage` to the project's `.dar`
        # This is necessary because the editor does not accept subdirectories
        dar_link = key + '.dar'
        dar_link_path = self.workdir_path(dar_link)
        if not os.path.exists(dar_link_path):
            os.symlink(self.workdir_path(dar_folder), dar_link_path)

        log_data = dict(
            return_code=p.returncode,
            message="Convert returned")
        f = open(log_file, 'a', 1)
        self.log_json(log_data, file=f)
        f.close()

from .github import GithubStorer
from .dropbox import DropboxStorer
from .google import GoogleStorer
from .stencila import StencilaStorer
