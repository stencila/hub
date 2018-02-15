from django.db import models

class Project(models.Model):
    address = models.TextField()
    gallery = models.BooleanField(default=False)
    users = models.ManyToManyField('auth.User', related_name='projects')

    class Meta:
        app_label = 'director'
