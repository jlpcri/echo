from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render


@login_required
def new(request):
    if request.method == 'GET':
        return render(request, "projects/new.html", {'message': 'New Project'})
    return HttpResponseNotFound()


@login_required
def project(request, pid):
    if request.method == 'GET':
        return render(request, "projects/project.html", {'message': 'Project ' + str(pid)})
    return HttpResponseNotFound()


@login_required
def projects(request):
    if request.method == 'GET':
        return render(request, "projects/projects.html", {'message': 'Projects'})
    return HttpResponseNotFound()