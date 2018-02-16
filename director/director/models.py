from django.db import models

import jwt
import requests
import time

class Project(models.Model):
    address = models.TextField(unique=True)
    gallery = models.BooleanField(default=False)
    users = models.ManyToManyField('auth.User', related_name='projects')

    class Meta:
        app_label = 'director'

class Cluster(models.Model):
    host = models.TextField(unique=True)
    secret = models.TextField()

    def get_jwt(self, user):
        payload = dict(iat=time.time(), user=user.username)
        return jwt.encode(payload, self.secret, algorithm='HS256')

    def open(self, user, project):
        jwt = self.get_jwt(user)
        url = '{}/open/{}'.format(self.host, project.address)
        headers = {'Authorization': 'Bearer {}'.format(jwt.decode('utf-8'))}
        response = requests.get(url, headers=headers)
        print(url)
        print(response.status_code)
        if response.status_code == 200:
            print(response.json())

    @classmethod
    def choose_cluster(cls, user, project):
        try:
            return cls.objects.all()[0]
        except IndexError:
            pass

    class Meta:
        app_label = 'director'
