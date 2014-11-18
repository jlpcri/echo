from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render, get_object_or_404
from echo.apps.projects.models import Project


def user_is_staff(user):
    return user.is_staff


@user_passes_test(user_is_staff)
def project(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        return render(request, "usage/projects.html", {})
    return HttpResponseNotFound()


@user_passes_test(user_is_staff)
def projects(request):
    if request.method == 'GET':
        return render(request, "usage/projects.html", {'projects': Project.objects.all()})
    return HttpResponseNotFound()


@user_passes_test(user_is_staff)
def usage(request):
    if request.method == 'GET':
        return redirect('usage:users', permanent=True)
    return HttpResponseNotFound()


@user_passes_test(user_is_staff)
def user(request, uid):
    if request.method == 'GET':
        user = get_object_or_404(User, pk=uid)
        return render(request, "usage/users.html", {})
    return HttpResponseNotFound()


@user_passes_test(user_is_staff)
def users(request):
    if request.method == 'GET':
        return render(request, "usage/users.html", {'users': User.objects.all()})
    return HttpResponseNotFound()