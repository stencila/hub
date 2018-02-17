from django.db import models
from django.conf import settings

import jwt
import time


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
