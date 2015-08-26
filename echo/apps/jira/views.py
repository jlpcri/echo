import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from echo.apps.projects.models import Project, VoiceSlot
from echo.apps.jira.tasks import sync_jira_to_ticket_status
from echo.apps.jira.utils import open_jira_connection


def sync_tickets(request):
    """View to kick off process of opening and closing Jira tickets"""
    p = get_object_or_404(Project, pk=request.POST['project_id'])
    version = request.POST['version']
    voiceslots = VoiceSlot.objects.filter(language__project=p)
    for voiceslot in voiceslots:
        sync_jira_to_ticket_status.delay(voiceslot_id=voiceslot.id)
    return HttpResponse(json.dumps({'success': True}), content_type="application/json")


def get_versions_by_project(request, project_id):
    """Return version names for a given Jira project (not Pheme) in JSON array"""
    j = open_jira_connection()
    project = j.project(project_id)
    return HttpResponse(json.dumps([version.name for version in project.versions]), content_type="application/json")


def set_jira_key(request):
    """Set project's Jira key via Ajax call"""
    p = get_object_or_404(Project, pk=request.POST['project_id'])
    p.jira_key = request.POST['jira-key']
    p.save()
    return HttpResponse(json.dumps({'success': True, 'jira-key': p.jira_key}), content_type="application/json")


def get_project_list(request):
    j = open_jira_connection()
    results = []
    for project in j.projects():
        results.append({'key': project.key, 'name': project.name, 'avatar': project.avatarUrls.__dict__['24x24']})
    return HttpResponse(json.dumps(results), content_type='application/json')