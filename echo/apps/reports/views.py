from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render


@login_required
def allreports(request):
    if request.method == 'GET':
        return render(request, "reports/allreports.html", {'message': 'Reports'})
    return HttpResponseNotFound()