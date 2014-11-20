from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render
from echo.apps.projects import contexts


def signin(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            return redirect('core:home')
        return redirect('core:form')
    elif request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            if user.is_active:
                login(request, user)
                if request.GET.get('next'):
                    return redirect(request.GET['next'])
                return redirect('core:home')
            messages.error(request, "This account is inactive.")
            return redirect('core:form')
        messages.error(request, "Invalid username or password.")
        return redirect('core:form')
    return HttpResponseNotFound()


@login_required
def signout(request):
    if request.method == 'GET':
        logout(request)
        return redirect('core:form')
    return HttpResponseNotFound()


@login_required
def home(request):
    if request.method == 'GET':
        sort_types = [
            'project_name',
            '-project_name',
            'total_prompts',
            '-total_prompts',
            'user_count',
            '-user_count'
        ]
        sort = request.GET.get('sort', '')
        sort = sort if sort else 'project_name'
        if sort in sort_types:
            return render(request, "core/home.html", contexts.context_home(request.user, sort))
    return HttpResponseNotFound()


def form(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            return redirect('core:home')
        return render(request, "core/form.html", {})
    return HttpResponseNotFound()