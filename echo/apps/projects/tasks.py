import pysftp

from django.conf import settings

from echo import celery_app
from echo.apps.projects.models import Project, UpdateStatus

@celery_app.task
def update_file_statuses(project_id):
    """Background process to update file statuses from Bravo server"""
    project = Project.objects.get(pk=int(project_id))
    status = UpdateStatus(project__pk=project_id)
    # Connect to Bravo server and get filenames and md5sums
    with pysftp.Connection(project.bravo_server.address, username=project.bravo_server.account,
                           private_key=settings.PRIVATE_KEY) as sftp:
        result = sftp.execute('find {0}/ -name "*.wav"'.format(project.root_path) +
                              ' -exec md5sum {} \; -exec stat -c"%Y" {} \;')
        print result
    status.running = False
    status.save()