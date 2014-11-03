from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from echo.apps.projects.models import Project
import contexts


@login_required
def failed(request, pid):
    if request.method == 'GET':
        if request.GET.get('export', False) == 'csv':
            return contexts.failed_csv(get_object_or_404(Project, pk=pid), HttpResponse(content_type='text/csv'))
        return render(request, "reports/failed.html", contexts.failed(get_object_or_404(Project, pk=pid)))
    return HttpResponseNotFound()


@login_required
def missing(request, pid):
    if request.method == 'GET':
        if request.GET.get('export', False) == 'csv':
            return contexts.missing_csv(get_object_or_404(Project, pk=pid), HttpResponse(content_type='text/csv'))
        return render(request, "reports/missing.html", contexts.missing(get_object_or_404(Project, pk=pid)))
    return HttpResponseNotFound()


@login_required
def reports(request):
    if request.method == 'GET':
        return render(request, "reports/reports.html", contexts.reports())
    return HttpResponseNotFound()

@login_required()
def report_project(request, pid):
    if request.method == 'GET':
        project = get_object_or_404(Project, pk=pid)
        missing = contexts.missing(project)

        context = RequestContext(request, {
            'project': project,
            'missing_slots': missing,
            'project_defective': '',
            'project_progress': '',
            'user_usage': ''
        })

        return render(request, "reports/report_project.html", context)