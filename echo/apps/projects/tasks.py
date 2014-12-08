import time

from echo import celery_app
from echo.apps.projects.models import Project, UpdateStatus

@celery_app.task
def update_file_statuses(project_id):
    project = Project.objects.get(pk=int(project_id))
    status = UpdateStatus(project__pk=project_id)
    time.sleep(6)
    status.running = False
    status.save()