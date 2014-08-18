from django.http import HttpResponseNotFound
from django.shortcuts import render


def index(request):
    if request.method == 'GET':
        return render(request, "core/index.html", {"message": "Core"})
    return HttpResponseNotFound