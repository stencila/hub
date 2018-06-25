import binascii
import datetime
import jwt
import os
import subprocess
import sys
import time
from contextlib import redirect_stdout
from uuid import uuid4

from django.db import models
from django.conf import settings
from django.core.files.storage import default_storage
from django.urls import reverse
from django.utils.timezone import now

from .storer import Storer

class Project(models.Model):
    address = models.TextField(unique=True)
    gallery = models.BooleanField(default=False)
    users = models.ManyToManyField('auth.User', related_name='projects')

    class Meta:
        app_label = 'director'

def new_checkout_key():
    return binascii.hexlify(os.urandom(32)).decode()

class Message(models.Model):
    checkout = models.ForeignKey('checkout', on_delete=models.CASCADE)
    time = models.DateTimeField(default=now)
    level = models.IntegerField(default=2)
    message = models.TextField()

class Checkout(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    key = models.TextField(unique=True, default=new_checkout_key)
    dirty = models.BooleanField(default=False)

    def workdir_path(self, f):
        return os.path.join(settings.STORAGE_DIR, f)

    def makedirs(self, folder):
        folder = self.workdir_path(folder)
        if os.path.exists(folder):
            return
        try:
            os.makedirs(folder)
        except FileExistsError:
            pass

    def get_storer(self):
        return Storer.get_instance_by_address(self.project.address)

    def get_folder_contents(self, remote_folder):
        if hasattr(self.project, 'stencilaproject'):
            return self.project.stencilaproject.list_files()
        storer = self.get_storer()
        return storer.get_folder_contents(remote_folder)

    def log(self, message, level=2):
        Message(message=message, level=level, checkout=self).save()

    def copy_file(self, filename, to):
        to = self.workdir_path(to)
        outfile = open(to, 'wb')
        if hasattr(self.project, 'stencilaproject'):
            self.project.stencilaproject.get_file(filename, outfile)
        else:
            storer = self.get_storer()
            contents = storer.file_contents(filename)
            outfile.write(contents)
        outfile.close()

    def copy_files(self, local_folder, remote_folder=''):
        filelist = self.get_folder_contents(remote_folder)
        copied = []

        for f in filelist:
            if f['type'] != "file":
                continue
            for ext in settings.UNCONVERTIBLE_FILE_TYPES:
                if f['name'].endswith(ext):
                    continue
            if f['size'] > settings.CONVERT_MAX_SIZE:
                continue
            self.makedirs(local_folder)
            local_filename = os.path.join(local_folder, f['name'])
            remote_filename = os.path.join(remote_folder, f['name'])
            self.copy_file(remote_filename, local_filename)
            copied.append(remote_filename)
        self.log("Copied %d files from /%s" % (len(copied), remote_folder))

        for f in filelist:
            if f['type'] != "dir":
                continue
            remote_subfolder = os.path.join(remote_folder, f['name'])
            local_subfolder = os.path.join(local_folder, f['name'])
            copied += self.copy_files(local_subfolder, remote_subfolder)

        return copied

    def convert(self):
        source_folder = os.path.join(self.key, 'source')
        self.makedirs(source_folder)
        copied = self.copy_files(source_folder)

        # Create an EDF which will be used as the canonical
        # source for all conversions
        edf_folder = os.path.join(self.key, '.edf')
        cmd = [
            "stencila", "convert",
            self.workdir_path(source_folder),
            self.workdir_path(edf_folder)]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        # Create a DAR for the editor to work on
        dar_folder = os.path.join(self.key, '.dar')
        cmd = [
            "stencila", "convert",
            self.workdir_path(source_folder),
            self.workdir_path(dar_folder)]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        # Create a symlink from `storage` to the project's `.dar`
        # This is necessary because the `dar-server` in `editor` does not
        # seem to accept subdirectories
        dar_link = self.key + '.dar'
        dar_link_path = self.workdir_path(dar_link)
        if not os.path.exists(dar_link_path):
            os.symlink(dar_folder, dar_link_path)

        self.log("Convert returned %d" % p.returncode)

class StencilaProject(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.SlugField(max_length=255)
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)

    base_project_name = 'project'

    @classmethod
    def get_or_create_for_user(cls, owner, uuid):
        if uuid is None:
            uuid = uuid4()
        try:
            return StencilaProject.objects.get(owner=owner, uuid=uuid)
        except StencilaProject.DoesNotExist:
            pass

        name = cls.generate_name(owner)
        address = cls._get_address(owner, name)
        project, created = Project.objects.get_or_create(address=address)
        if not created and hasattr(project, 'stencilaproject'):
            return # TODO fail
        stencila_project = cls(name=name, owner=owner, project=project, uuid=uuid)
        stencila_project.save()
        return stencila_project

    @classmethod
    def _get_address(cls, owner, name):
        return 'stencila://%s/%s' % (owner, name)

    def get_address(self):
        return self._get_address(self.owner, self.name)

    @classmethod
    def generate_name(cls, owner):
        address_prefix = cls._get_address(owner, cls.base_project_name)
        existing_addresses = [
            p.address for p in Project.objects.filter(
                stencilaproject__isnull=False,
                stencilaproject__owner=owner,
                address__startswith=address_prefix)]
        i = 1
        name = "%s-%d" % (cls.base_project_name, i)
        while cls._get_address(owner, name) in existing_addresses:
            i += 1
            name = "%s-%d" % (cls.base_project_name, i)
        return name

    def delete(self):
        try:
            default_storage.delete(self.prefix())
        except:
            pass
        self.project.delete()
        super(StencilaProject, self).delete()

    def prefix(self):
        return "projects/%s" % str(self.uuid)

    def path(self, filename):
        return "%s/%s" % (self.prefix(), filename)

    def save(self, *args, **kwargs):
        address = self.get_address()
        if self.project and self.project.address != address:
            self.project.address = address
            self.project.save()
        super().save(*args, **kwargs)

    def upload(self, files):
        for f in files:
            obj = default_storage.open(self.path(f.name), 'w')
            obj.write(f.read())
            obj.close()
            f.close()

    def list_files(self):
        _, filenames = default_storage.listdir(self.prefix())
        files = []
        for f in filenames:
            name = self.path(f)
            files.append(dict(
                type="file",
                name=f,
                size=default_storage.size(name),
                last_modified=default_storage.get_modified_time(name)))
        return files

    def get_file(self, filename, to):
        f = default_storage.open(self.path(filename), 'rb')
        to.write(f.read())
        f.close()

    def delete_file(self, filename):
        default_storage.delete(self.path(filename))

    class Meta:
        unique_together = ('name', 'owner')



class Host(models.Model):
    url = models.URLField(unique=True)

    def token(self, user):
        payload = dict(iat=time.time(), user=user.username)
        return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256').decode("utf-8")

    @classmethod
    def choose(cls, user, project):
        try:
            return cls.objects.all()[0]
        except IndexError:
            return Host(url='http://localhost:2000')

    class Meta:
        app_label = 'director'
