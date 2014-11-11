from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.utils import timezone
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
        vuids = project.vuid_set.all()
        # Get VUID upload_date
        vuid_upload_date = None
        if vuids.count() == 1:
            vuid_upload_date = project.vuid_set.all()[0].upload_date
        elif vuids.count() > 1:
            # find least vuid upload date
            vuid_upload_date = project.vuid_set.all()[0].upload_date
            for vuid in project.vuid_set.all():
                if vuid.upload_date < vuid_upload_date:
                    vuid_upload_date = vuid.upload_date

        missing = []
        defective = []

        # Missing
        missing_slots = project.voiceslots_missing()
        for item in missing_slots:
            temp = {
                'filepath': item.filepath,
                'language': item.language.name
            }
            missing.append(temp)

        #Defective
        failed_actions = project.actions_failed()
        for item in failed_actions:
            temp = {
                'name': item.scope.voiceslot.name,
                'test_time': item.time,
                'fail_note': item.description
            }
            defective.append(temp)

        # Progress of porject
        # First check vuid upload_date
        if vuid_upload_date:
            # Second check Actions type
            voiceslot_fail = 0
            voiceslot_pass = 0
            voiceslot_new = 0
            voiceslot_missing = 0
            start = timezone.now() - timedelta(days=10)
            end = timezone.now()
            days = (end - start).days
            date_range = [end - timedelta(days=x) for x in range(0, days)]
            for day in date_range:
                actions = Action.objects.filter(time=day, scope__project=project)

                if actions.count() == 0:
                    one_day_before = day - timedelta(days=1)

                    # if one_day_before less than vuid upload_date then continue
                    if one_day_before < vuid_upload_date:
                        break

                    results = []
                    found = False
                    while found is False:
                        actions = Action.objects.filter(time=one_day_before, scope__project=project)
                        if actions.count() > 0:
                            results = actions
                            found = True
                        else:
                            one_day_before -= timedelta(days=1)
                            if one_day_before < vuid_upload_date:
                                break

                    if found is False:  # reached vuid upload_date
                        continue
                    action = results[0]
                else:
                    action = actions[0]

                if action.type in (Action.TESTER_FAIL_SLOT, Action.AUTO_FAIL_SLOT):
                    voiceslot_fail += 1
                elif action.type in (Action.TESTER_PASS_SLOT, Action.AUTO_PASS_SLOT):
                    voiceslot_pass += 1
                elif action.type == Action.AUTO_NEW_SLOT:
                    voiceslot_new += 1
                elif action.type == Action.AUTO_MISSING_SLOT:
                    voiceslot_missing += 1

            progress = {
                'start': start.date(),
                'end': end.date(),
                'pass': voiceslot_pass,
                'fail': voiceslot_fail,
                'missing': voiceslot_missing,
                'new': voiceslot_new
            }
        else:
            progress = None

        #print progress

        context = RequestContext(request, {
            'project': project,
            'missing_slots': missing,
            'project_defective': defective,
            'project_progress': progress,
        })
        Action.log(request.user, Action.REPORT_GENERATION, 'Viewed report dashboard', project)
        return render(request, "reports/report_project.html", context)