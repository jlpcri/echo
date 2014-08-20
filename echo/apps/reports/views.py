from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render


@login_required
def report(request, rid):
    if request.method == 'GET':
        return render(request, "reports/report.html", {'message': 'Report ' + str(rid)})
    return HttpResponseNotFound()


@login_required
def reports(request):
    if request.method == 'GET':
        return render(request, "reports/reports.html", {'message': 'Reports'})
    return HttpResponseNotFound()