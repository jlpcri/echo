from echo import celery_app
from echo.apps.projects.models import VoiceSlot
from echo.apps.jira.models import Ticket


@celery_app.task
def sync_jira_to_ticket_status(voiceslot_id, version_name):
    v = VoiceSlot.objects.get(id=voiceslot_id)
    if v.ticket_set.count() > 0:
        if v.status == VoiceSlot.PASS:
            v.ticket_set.first().close()
        if v.status == VoiceSlot.FAIL or v.status == VoiceSlot.MISSING:
            v.ticket_set.first().reopen(version_name)
        return
    if v.status == VoiceSlot.MISSING or v.status == VoiceSlot.FAIL:
        t = Ticket.objects.create(voiceslot=v)
        t.save()
        t.open(version_name)
