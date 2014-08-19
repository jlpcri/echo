from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render


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
        return render(request, "core/home.html", {'message': 'Home'})
    return HttpResponseNotFound()


def form(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            return redirect('core:home')
        return render(request, "core/form.html", {})
    return HttpResponseNotFound()