from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from echo.apps.projects.models import Project
import contexts
from echo.apps.activity.models import Action

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
        missing = []
        defective = []

        missing_slots = project.voiceslots_missing()
        for item in missing_slots:
            temp = {
                'filepath': item.filepath,
                'language': item.language.name
            }
            missing.append(temp)

        failed_actions = project.actions_failed()
        for item in failed_actions:
            temp = {
                'name': item.scope.voiceslot.name,
                'test_time': item.time,
                'fail_note': item.description
            }
            defective.append(temp)

        start = request.GET.get('start_time')
        end = request.GET.get('end_time')

        context = RequestContext(request, {
            'project': project,
            'missing_slots': missing,
            'project_defective': defective,
            'project_progress': '',
            'user_usage': ''
        })

        return render(request, "reports/report_project.html", context)