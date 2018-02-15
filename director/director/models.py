from django.db import models

class Project(models.Model):
    address = models.TextField()
    creator = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    class Meta:
        app_label = 'director'
