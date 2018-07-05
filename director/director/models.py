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
    public = models.BooleanField(default=False)
    creator = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, related_name='projects_owned',
        null=True, blank=True)
    viewers = models.ManyToManyField('auth.User', related_name='projects_viewed')
    name = models.SlugField(max_length=255)
    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)

    base_project_name = 'project'

    class Meta:
        app_label = 'director'
        unique_together = ('creator', 'name')

    @classmethod
    def generate_name(cls, creator, prefix=None):
        if prefix is None:
            prefix = cls.base_project_name
        existing_names = [
            p.name for p in Project.objects.filter(
                creator=creator, name__startswith=prefix)]
        i = 1
        name = "%s-%d" % (prefix, i)
        while name in existing_names:
            i += 1
            name = "%s-%d" % (prefix, i)
        return name

    @classmethod
    def get_or_create_by_address(cls, address, user):
        try:
            project = cls.objects.get(address=address)
            project.viewers.add(user)
            return (project, False)
        except cls.DoesNotExist:
            pass

        name = cls.generate_name(user, prefix=address.split('/')[-1])
        project = cls(address=address, creator=user, name=name)
        project.save()
        project_permission = ProjectPermission(project=project, user=user, type='admin')
        project_permission.save()
        project.viewers.add(user)
        return (project, True)

    @classmethod
    def _get_address(cls, owner, name):
        return 'stencila://%s/%s' % (owner, name)

    def get_address(self):
        return self._get_address(self.creator, self.name)

    @classmethod
    def add(cls, creator):
        name = cls.generate_name(creator)
        address = cls._get_address(creator, name)
        project = cls(address=address, creator=creator, name=name)
        project.save()
        project_permission = ProjectPermission(project=project, user=creator, type='admin')
        project_permission.save()
        project.viewers.add(creator)
        return project

    def can_edit(self, user):
        return len(self.permissions.filter(user=user, type__in=('write', 'admin'))) > 0

    def is_admin(self, user):
        return len(self.permissions.filter(user=user, type__in=('admin',))) > 0

    def delete(self):
        try:
            default_storage.delete(self.prefix())
        except:
            pass
        super().delete()

    def prefix(self):
        return "projects/%s" % str(self.uuid)

    def path(self, filename):
        return "%s/%s" % (self.prefix(), filename)

    def save(self, *args, **kwargs):
        # Do we still need this?
        address = self.get_address()
        if self.address != address:
            self.address = address
        super(Project, self).save(*args, **kwargs)

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

class ProjectPermission(models.Model):
    TYPES = (('read', 'Read'), ('write', 'Write'), ('admin', 'Admin'))
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    project = models.ForeignKey(
        'Project', on_delete=models.CASCADE, related_name='permissions')
    type = models.CharField(max_length=10, choices=TYPES)

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
        if self.project.address.startswith('stencila://'):
            return self.project.list_files()
        storer = self.get_storer()
        return storer.get_folder_contents(remote_folder)

    def log(self, message, level=2):
        Message(message=message, level=level, checkout=self).save()

    def copy_file(self, filename, to):
        to = self.workdir_path(to)
        outfile = open(to, 'wb')
        if self.project.address.startswith('stencila://'):
            self.project.get_file(filename, outfile)
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

    def commit(self):
        if self.project.address.startswith('stencila://'):
            dar_folder = self.workdir_path(os.path.join(self.key, 'source'))
            for file in os.listdir(dar_folder):
                path = self.project.path(file)
                with open(os.path.join(dar_folder, file)) as fh:
                    obj = default_storage.open(path, 'w')
                    obj.write(fh.read())
                    obj.close()

    def convert(self):
        source_folder = os.path.join(self.key, 'source')
        self.makedirs(source_folder)
        copied = self.copy_files(source_folder)

        # Create an EDF which will be used as the canonical
        # source for all conversions
        # edf_folder = os.path.join(self.key, '.edf')
        # cmd = [
        #     "stencila", "convert",
        #     self.workdir_path(source_folder),
        #     self.workdir_path(edf_folder)]
        # p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # stdout, stderr = p.communicate()

        # Convert the source directory to a DAR for the editor to work on
        cmd = [
            "stencila", "convert", "--to=dar",
            self.workdir_path(source_folder),
            self.workdir_path(source_folder)
        ]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        if p.returncode != 0 or 'error' in stderr.decode(): # Currently CLI does not return exit code 1 if it fails
            self.log("Conversion failed: %s" % stderr)
        else:
            self.log("Conversion suceeded")

        # Create a symlink from `storage` to the project's `.dar`
        # This is necessary because the `dar-server` in `editor` does not
        # seem to accept subdirectories
        dar_link = self.key + '.dar'
        dar_link_path = self.workdir_path(dar_link)
        if not os.path.exists(dar_link_path):
            os.symlink(source_folder, dar_link_path)

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
            return Host(url='http://cloud-test.stenci.la')

    class Meta:
        app_label = 'director'
