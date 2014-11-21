import json
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render, get_object_or_404
from echo.apps.activity.models import Action
from echo.apps.projects.models import Project
from echo.apps.usage import contexts


def user_is_staff(user):
    return user.is_staff


@user_passes_test(user_is_staff)
def project(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        q = Action.objects.filter(scope__project=p).order_by('-time')[0:20]
        actions = []
        for a in q:
            actions.append(
                {
                    'username': a.actor.username,
                    'description': a.description,
                    'time': a.time.strftime('%c')
                }
            )
        json_data = json.dumps({'project_name': p.name, 'actions': actions})
        return HttpResponse(json_data, content_type="application/json")
    return HttpResponseNotFound()


@user_passes_test(user_is_staff)
def projects(request):
    if request.method == 'GET':
        sort_types = [
            'project_name',
            '-project_name',
            'total',
            '-total',
            'passed',
            '-passed',
            'defective',
            '-defective',
            'auto_total',
            '-auto_total',
            'auto_passed',
            '-auto_passed',
            'auto_defective',
            '-auto_defective',
            'auto_missing',
            '-auto_missing',
            'rework_ratio',
            '-rework_ratio',
            'auto_ratio',
            '-auto_ratio'
        ]
        # if tab and sort are not present, set to empty
        # tab = request.GET.get('tab', '')
        sort = request.GET.get('sort', '')
        # if tab and sort are empty, set to defaults
        # tab = tab if tab else 'my'
        sort = sort if sort else 'project_name'
        # validate tab and sort
        # if tab in tab_types and sort in sort_types:
        if sort in sort_types:
            return render(request, "usage/projects.html", contexts.projects_context(sort))
    return HttpResponseNotFound()


@user_passes_test(user_is_staff)
def usage(request):
    if request.method == 'GET':
        return redirect('usage:users', permanent=True)
    return HttpResponseNotFound()


@user_passes_test(user_is_staff)
def user(request, uid):
    if request.method == 'GET':
        u = get_object_or_404(User, pk=uid)
        q = Action.objects.filter(actor=u).order_by('-time')[0:20]
        actions = []
        for a in q:
            actions.append(
                {
                    'project_name': a.scope.project.name,
                    'description': a.description,
                    'time': a.time.strftime('%c')
                }
            )
        json_data = json.dumps({'username': u.username, 'actions': actions})
        return HttpResponse(json_data, content_type="application/json")
    return HttpResponseNotFound()


@user_passes_test(user_is_staff)
def users(request):
    if request.method == 'GET':
        sort_types = [
            'username',
            '-username',
            'total',
            '-total',
            'passed',
            '-passed',
            'defective',
            '-defective',
            'reports',
            '-reports',
            'uploads',
            '-uploads',
            'projects',
            '-projects'
        ]
        # if tab and sort are not present, set to empty
        # tab = request.GET.get('tab', '')
        sort = request.GET.get('sort', '')
        # if tab and sort are empty, set to defaults
        # tab = tab if tab else 'my'
        sort = sort if sort else 'username'
        # validate tab and sort
        # if tab in tab_types and sort in sort_types:
        if sort in sort_types:
            return render(request, "usage/users.html", contexts.users_context(sort))
    return HttpResponseNotFound()