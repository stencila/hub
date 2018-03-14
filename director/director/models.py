from django.db import models
from django.conf import settings

import jwt
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
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    base_project_name = 'project'

    @classmethod
    def create_for_user(cls, owner):
        existing_names = [
            p.name for p in cls.objects.filter(
                owner=owner, name__startswith=cls.base_project_name)]
        i = 1
        name = "%s-%d" % (cls.base_project_name, i)
        while name in existing_names:
            i += 1
            name = "%s-%d" % (cls.base_project_name, i)
        address = 'stencila://%s/%s' % (owner, name)
        project = Project(address=address)
        project.save()
        stencila_project = cls(name=name, owner=owner, project=project)
        stencila_project.save()
        return project

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
            pass

    class Meta:
        app_label = 'director'
