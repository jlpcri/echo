from echo import celery_app

@celery_app.task
def sync_project(project_id):
    raise NotImplementedError