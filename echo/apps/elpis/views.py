import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from echo.apps.projects.models import Project
from echo.apps.settings.models import PreprodServer


@login_required
def dashboard(request, pid):
    """Project file transfer verification dashboard"""
    p = get_object_or_404(Project, pk=pid)
    preprod_servers = PreprodServer.objects.all()
    return render(request, 'elpis/elpis.html', {'project': p, 'preprod_servers': preprod_servers})


@login_required
def set_preprod_server(request, pid):
    """Ajax view to associate a preprod server with a project"""
    p = get_object_or_404(Project, pk=pid)
    try:
        p.preprod_server = PreprodServer.objects.get(pk=int(request.POST['preprod-server']))
        p.save()
        paths = p.preprod_server.get_clients()
        if p.name.lower() in paths:
            match = True
        else:
            match = False
        json_data = json.dumps({'success': True, 'type': p.preprod_server.application_type, 'paths': paths,
                                'match': match})
    except Exception as e:
        json_data = json.dumps({'success': False, 'error': str(e)})
    return HttpResponse(json_data, content_type="application/json")


@login_required
def set_preprod_path(request, pid):
    """Ajax view to associate a preprod path with a project"""
    p = get_object_or_404(Project, pk=pid)
    try:
        p.set_preprod_path(request.POST['preprod-path'])
        json_data = json.dumps({'success': True, 'path': p.preprod_path})
    except Exception as e:
        json_data = json.dumps({'success': False, 'error': str(e)})
    return HttpResponse(json_data, content_type="application/json")


@login_required
def verify_file_transfer(request, pid):
    """View to identify potential problems with file transfer from Bravo to Preprod"""
    p = get_object_or_404(Project, pk=pid)
    if request.method == 'GET':
        apps = p.get_applications()
        json_data = json.dumps({'apps': apps})
        return HttpResponse(json_data, content_type="application/json")
    elif request.method == 'POST':
        apps = request.POST.getlist('applications')
        files = p.preprod_server.get_wavs_from_apps(p.preprod_client_id, apps)
        json_data = json.dumps(files)
        return HttpResponse(json_data, content_type="application/json")