import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render
from echo.apps.core import messages
from forms import ProjectForm
import helpers
from models import Project, VUID


@login_required
def new(request):
    if request.method == 'GET':
        return render(request, "projects/new.html", {'project_form': ProjectForm()})
    elif request.method == 'POST':
        if "create_project" in request.POST:
            form = ProjectForm(request.POST, request.FILES)
            if form.is_valid():
                n = form.cleaned_data['name']
                p = Project(name=n)
                try:
                    p.full_clean()
                    p.save()
                    messages.success(request, "Created project")
                    if 'file' in request.FILES and request.FILES['file'].name.endswith('.xlsx'):
                        helpers.upload_VUID(form.cleaned_data['file'], request.user, p)
                    elif 'file' in request.FILES:
                        messages.danger(request, "Invalid file type, must be .xlsx")
                    return redirect("projects:project", pid=p.pk)
                except ValidationError as e:
                    if 'name' in e.message_dict:
                        messages.danger(request, e.message_dict.get('name')[0])
                    return render(request, "projects/new.html", {'project_form': form})
            messages.danger(request, "Unable to create project")
            return render(request, "projects/new.html", {'project_form': form})
    return HttpResponseNotFound()


@login_required
def project(request, pid):
    if request.method == 'GET':
        p = Project.objects.get(pk=pid)
        return render(request, "projects/project.html", {'project': p, 'vuids': VUID.objects.filter(project=p)})
    return HttpResponseNotFound()


@login_required
def projects(request):
    if request.method == 'GET':
        return render(request, "projects/projects.html", {'projects': Project.objects.all()})
    return HttpResponseNotFound()


@login_required
def vuid(request, vid):
    if request.method == 'GET':
        return render(request, "projects/vuid.html", {'vuid': VUID.objects.get(pk=vid)})
    return HttpResponseNotFound()