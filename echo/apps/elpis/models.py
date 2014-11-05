from django.db import models

class Status(models.model):
    project = models.ForeignKey('projects.Project')
    response = models.TextField(default='')
    last_run = models.DateTimeField(auto_now=True)
    running = models.BooleanField(default=False)
    query_id = models.TextField(default='')