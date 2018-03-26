from django.db import models
from django.conf import settings
from django.urls import reverse

from .filestore import Client as FilestoreClient
import jwt
import sys
import time
import uuid

class Project(models.Model):
    address = models.TextField(unique=True)
    gallery = models.BooleanField(default=False)
    users = models.ManyToManyField('auth.User', related_name='projects')

    @classmethod
    def open(cls, user, address):
        project, _ = Project.objects.get_or_create(address=address)
        project.users.add(user)
        cluster = Cluster.choose(user=user, project=project)
        return cluster.host, cluster.jwt(user)

    class Meta:
        app_label = 'director'

class StencilaProject(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.SlugField(max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    base_project_name = 'project'

    @classmethod
    def get_or_create_for_user(cls, owner, uuid):
        try:
            return StencilaProject.objects.get(owner=owner, uuid=uuid)
        except StencilaProject.DoesNotExist:
            pass

        name = cls.generate_name(owner)
        address = 'stencila://%s/%s' % (owner, name)
        project = Project(address=address)
        project.save()
        stencila_project = cls(name=name, owner=owner, project=project, uuid=uuid)
        stencila_project.save()
        return stencila_project

    @classmethod
    def generate_name(cls, owner):
        existing_names = [
            p.name for p in cls.objects.filter(
                owner=owner, name__startswith=cls.base_project_name)]
        i = 1
        name = "%s-%d" % (cls.base_project_name, i)
        while name in existing_names:
            i += 1
            name = "%s-%d" % (cls.base_project_name, i)
        return name

    def save(self, *args, **kwargs):
        address = 'stencila://%s/%s' % (self.owner, self.name)
        if self.project and self.project.address != address:
            self.project.address = address
            self.project.save()
        super().save(*args, **kwargs)

    def upload(self, files):
        fsclient = FilestoreClient()
        fsclient.upload(self.uuid, files)

    def list_files(self):
        fsclient = FilestoreClient()
        prefix = str(self.uuid)
        files = []
        for c in fsclient.list(prefix):
            files.append(dict(
                name=c.get('Key', None)[len(prefix)+1:],
                size=c.get('Size', None),
                last_modified=c.get('LastModified', None)))
        return files

    def get_file(self, filename, to):
        prefix = str(self.uuid)
        fsclient = FilestoreClient()
        fsclient.download(prefix, filename, to)

    def delete_file(self, filename):
        prefix = str(self.uuid)
        fsclient = FilestoreClient()
        fsclient.delete(prefix, filename)

    class Meta:
        unique_together = ('name', 'owner')

class Cluster(models.Model):
    host = models.TextField(unique=True)

    def jwt(self, user):
        payload = dict(iat=time.time(), user=user.username)
        return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256').decode("utf-8")

    @classmethod
    def choose(cls, user, project):
        try:
            return cls.objects.all()[0]
        except IndexError:
            sys.stderr.write("No clusters\n")

    class Meta:
        app_label = 'director'
