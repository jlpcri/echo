import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from echo.apps.projects.models import Project, VoiceSlot
from echo.apps.jira.tasks import sync_jira_to_ticket_status

def sync_tickets(request):
    """View to kick off process of opening and closing Jira tickets"""
    p = get_object_or_404(Project, pk=request.POST['project_id'])
    voiceslots = VoiceSlot.objects.filter(language__project=p)
    for voiceslot in voiceslots:
        sync_jira_to_ticket_status.delay(voiceslot_id=voiceslot.id)
    return HttpResponse(json.dumps({'success': True}), content_type="application/json")