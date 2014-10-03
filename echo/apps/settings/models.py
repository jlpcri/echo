from django.db import models


class Server(models.Model):
    name = models.TextField(unique=True, blank=False)
    address = models.TextField(blank=False)
    account = models.TextField(blank=False)

    def __unicode__(self):
        return self.name