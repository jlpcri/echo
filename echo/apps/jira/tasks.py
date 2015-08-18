from echo import celery_app

@celery_app.task
def sync_jira_to_ticket_status(voiceslot_id):
    raise NotImplementedError