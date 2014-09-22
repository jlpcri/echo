from django.db import models


class Server(models.Model):
    name = models.TextField(unique=True, blank=False)
    address = models.TextField(blank=False)
    account = models.TextField(blank=False)

    @classmethod
    def choices(cls):
        items = [(i.pk, i.name) for i in Server.objects.all()]
        items.insert(0, (0, '---------'))
        return items