import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from echo.apps.projects.models import Project

def dashboard(request, pid):
    """Project file transfer verification dashboard"""
    p = get_object_or_404(Project, pk=pid)
    return render(request, 'elpis/elpis.html', {'project': p})

def set_preprod_path(request, pid):
    """View to associate a preprod path with a server"""
    p = get_object_or_404(Project, pk=pid)
    json_data = json.dumps({})
    return HttpResponse(json_data, content_type="application/json")

def verify_file_transfer(request, pid):
    """View to identify potential problems with file transfer from Bravo to Preprod"""
    p = get_object_or_404(Project, pk=pid)
    json_data = json.dumps({})
    return HttpResponse(json_data, content_type="application/json")