from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render


@login_required
def allprojects(request):
    if request.method == 'GET':
        return render(request, "projects/allprojects.html", {'message': 'Projects'})
    return HttpResponseNotFound()