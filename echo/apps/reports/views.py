from datetime import timedelta, date, datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.utils import timezone
import pytz
from echo.apps.projects.models import Project, VoiceSlot
import contexts
from echo.apps.activity.models import Action
from django.conf import settings

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
            vuid_upload_date = vuid_upload_date.date()

            outputs = []

            if request.GET.get('start'):
                start = request.GET.get('start')
            else:
                start = (timezone.now() - timedelta(days=10)).date()

            if request.GET.get('end'):
                end = request.GET.get('end')
            else:
                end = (timezone.now() + timedelta(days=1)).date()

            days = (end - start).days
            if days == 0:
                voiceslots = project.voiceslots()
                tmp_statistics = get_voiceslot_statistics(voiceslots,
                                                          start,
                                                          vuid_upload_date)
                outputs.append({
                    'date': start,
                    'statistics': tmp_statistics
                })

            else:
                date_range = [end - timedelta(days=x) for x in range(0, days + 1)]

                for day in date_range:
                    break_flag = False  # flag to check if current day less than vuid upload date
                    #tmp_statistics = voiceslots_statistics.copy()
                    voiceslots = project.voiceslots()
                    tmp_statistics = get_voiceslot_statistics(voiceslots,
                                                              day,
                                                              vuid_upload_date,)
                    outputs.append({
                        'date': day,
                        'statistics': tmp_statistics
                    })
                    if break_flag:
                        break
        else:
            outputs = None

        context = RequestContext(request, {
            'project': project,
            'missing_slots': missing,
            'project_defective': defective,
            'project_progress': outputs,
        })
        Action.log(request.user, Action.REPORT_GENERATION, 'Viewed report dashboard', project)
        return render(request, "reports/report_project.html", context)


def get_voiceslot_statistics(voiceslots, day, vuid_upload_date):
    tmp_statistics = settings.VOICESLOTS_METRICS.copy()
    for vs in voiceslots:
        try:
            action = Action.objects.get(time__gt=day,
                                        time__lt=day+timedelta(days=1),
                                        scope__voiceslot=vs)
            if action.type in (Action.TESTER_FAIL_SLOT, Action.AUTO_FAIL_SLOT):
                tmp_statistics['fail'] += 1
            elif action.type in (Action.TESTER_PASS_SLOT, Action.AUTO_PASS_SLOT):
                tmp_statistics['pass'] += 1
            elif action.type == Action.AUTO_NEW_SLOT:
                tmp_statistics['new'] += 1
            elif action.type == Action.AUTO_MISSING_SLOT:
                tmp_statistics['missing'] += 1

        except ObjectDoesNotExist:
            one_day_before = day - timedelta(days=1)
            if one_day_before < vuid_upload_date:
                break_flag = True
                break
            found_flag = False
            while found_flag is False:
                try:
                    action = Action.objects.get(time__gt=one_day_before,
                                                time__lt=one_day_before+timedelta(days=1),
                                                scope__voiceslot=vs)
                    if action.type in (Action.TESTER_FAIL_SLOT, Action.AUTO_FAIL_SLOT):
                        tmp_statistics['fail'] += 1
                    elif action.type in (Action.TESTER_PASS_SLOT, Action.AUTO_PASS_SLOT):
                        tmp_statistics['pass'] += 1
                    elif action.type == Action.AUTO_NEW_SLOT:
                        tmp_statistics['new'] += 1
                    elif action.type == Action.AUTO_MISSING_SLOT:
                        tmp_statistics['missing'] += 1
                    found_flag = True
                except ObjectDoesNotExist:
                    one_day_before -= timedelta(days=1)
                    if one_day_before < vuid_upload_date:
                        break
            if found_flag is True:
                continue

    return tmp_statistics