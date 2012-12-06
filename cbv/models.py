from django.db import models


class User(models.Model):
    email = models.EmailField(unique=True)

    def __unicode__(self):
        return self.email