from django.db import models

import jwt

class Project(models.Model):
    address = models.TextField(unique=True)
    gallery = models.BooleanField(default=False)
    users = models.ManyToManyField('auth.User', related_name='projects')

    class Meta:
        app_label = 'director'

class Cluster(models.Model):
    host = models.TextField(unique=True)
    secret = models.TextField()

    def get_jwt(self, payload):
        return jwt.encode(payload, self.secret, algorithm='HS256')

    class Meta:
        app_label = 'director'
