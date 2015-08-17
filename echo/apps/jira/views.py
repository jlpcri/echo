from django.shortcuts import get_object_or_404
from echo.apps.projects.models import Project

def sync_tickets(request):
    """View to kick off process of opening and closing Jira tickets"""
    p = get_object_or_404(Project, pk=request.POST['project_id'])
    e