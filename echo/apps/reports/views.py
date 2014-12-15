from datetime import timedelta, date, datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext
import pytz
import time
from echo.apps.core import messages
from echo.apps.projects.models import Project, VoiceSlot
import contexts
from echo.apps.activity.models import Action
from django.conf import settings

@login_required
def failed(request, pid):
    if request.method == 'GET':
        if request.GET.get('export', False) == 'csv':
            return contexts.failed_csv(get_object_or_404(Project, pk=pid), HttpResponse(content_type='text/csv'))
        
        #Defective
        defective = []
        project = get_object_or_404(Project, pk=pid)
        failing_slots = project.voiceslots().filter(status=VoiceSlot.FAIL)
        for slot in failing_slots:
            action = Action.objects.filter(scope__voiceslot=slot, type__in=[Action.TESTER_FAIL_SLOT, Action.AUTO_FAIL_SLOT]).latest('time')
            temp = {
                'name': slot.name,
                'language': slot.language.name,
                'path': slot.filepath(),
                'test_time': action.time,
                'fail_note': action.description
            }
            defective.append(temp)

        context = RequestContext(request, {
            'project': project,
            'project_defective': defective
        })

        Action.log(request.user, Action.REPORT_GENERATION, 'Viewed failed report dashboard', project)

        return render(request, "reports/failed.html", context)
    return HttpResponseNotFound()


@login_required
def missing(request, pid):
    if request.method == 'GET':
        if request.GET.get('export', False) == 'csv':
            return contexts.missing_csv(get_object_or_404(Project, pk=pid), HttpResponse(content_type='text/csv'))

        # Missing
        missing = []
        project = get_object_or_404(Project, pk=pid)
        missing_slots = project.voiceslots_missing()
        for item in missing_slots:
            temp = {
                'filepath': item.filepath,
                'language': item.language.name
            }
            missing.append(temp)

        context = RequestContext(request, {
            'project': project,
            'missing_slots': missing
        })

        Action.log(request.user, Action.REPORT_GENERATION, 'Viewed missing report dashboard', project)

        return render(request, "reports/missing.html", context)
    return HttpResponseNotFound()


@login_required
def reports(request):
    if request.method == 'GET':
        sort_types = [
            'project_name',
            '-project_name',
            'passed',
            '-passed',
            'defective',
            '-defective',
            'missing',
            '-missing',
            'total',
            '-total',
            'progress',
            '-progress',
            'testers',
            '-testers'
        ]
        sort = request.GET.get('sort', '')
        sort = sort if sort else 'project_name'
        if sort in sort_types:
            return render(request, "reports/reports.html", contexts.reports_context(sort))
    return HttpResponseNotFound()

@login_required()
def report_project(request, pid):
    if request.method == 'GET':
        project = get_object_or_404(Project, pk=pid)

        if not project.root_path:
            messages.danger(request, 'Please set project root path')
            return redirect('reports:reports')

        vuids = project.vuid_set.all()
        if vuids.count() == 0:
            messages.danger(request, 'Please upload prompt list file')
            return redirect('reports:reports')

        if not project.voiceslots().filter(status__in=[VoiceSlot.READY, VoiceSlot.PASS, VoiceSlot.FAIL, VoiceSlot.MISSING]).exists():
            messages.danger(request, 'Please update file statuses from bravo server')
            return redirect('reports:reports')

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

        # Progress of project
        # First check vuid upload_date
        if vuid_upload_date:
            # Second check Actions type

            outputs = {
                'date': [],
                'fail': [],
                'pass': [],
                'new': [],
                'missing': []
            }

            try:
                end = date.fromtimestamp(float(request.GET.get('end')))
            except (TypeError, ValueError):
                print "Exception raised"
                end = datetime.now(tz=pytz.UTC).date()

            try:
                start = date.fromtimestamp(float(request.GET.get('start')))
            except (TypeError, ValueError):
                start = end - timedelta(days=10)

            while start <= end:
                statuses = project.status_as_of(time.mktime(start.timetuple()))
                print statuses
                outputs['date'].append(start.strftime("%Y-%m-%d"))
                outputs['fail'].append(int(statuses[Action.TESTER_FAIL_SLOT] + statuses[Action.AUTO_FAIL_SLOT]))
                outputs['pass'].append(int(statuses[Action.TESTER_PASS_SLOT] + statuses[Action.AUTO_FAIL_SLOT]))
                outputs['new'].append(int(statuses[Action.AUTO_NEW_SLOT]))
                outputs['missing'].append(int(statuses[Action.AUTO_MISSING_SLOT]))
                start += timedelta(days=1)

        else:
            outputs = None

        context = RequestContext(request, {
            'project': project,
            'project_progress': outputs,
            'start': float(request.GET.get('start', time.mktime(start.timetuple()))),
            'end': float(request.GET.get('end', time.mktime(end.timetuple()))),
            'feed': Action.objects.filter(scope__project=project).order_by('-time')[0:10]
        })
        Action.log(request.user, Action.REPORT_GENERATION, 'Viewed progress report dashboard', project)
        return render(request, "reports/report_project.html", context)


def get_voiceslot_statistics(voiceslots, day, vuid_upload_date, break_flag):
    tmp_statistics = settings.VOICESLOTS_METRICS.copy()
    for vs in voiceslots:
        try:
            action = Action.objects.filter(time__gt=get_midnight_of_day(day),
                                           time__lt=get_midnight_of_day(day)+timedelta(days=1),
                                           scope__voiceslot=vs).latest('time')
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
            if one_day_before < get_midnight_of_day(vuid_upload_date):
                break_flag = True
                break
            found_flag = False
            while found_flag is False:
                try:
                    action = Action.objects.filter(time__gt=get_midnight_of_day(one_day_before),
                                                   time__lt=get_midnight_of_day(one_day_before)+timedelta(days=1),
                                                   scope__voiceslot=vs).latest('time')
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
                    if one_day_before < get_midnight_of_day(vuid_upload_date):
                        break
            if found_flag is True:
                continue

    return {
        'flag': break_flag,
        'statistics': tmp_statistics
    }


def get_midnight_of_day(day):
    return day.replace(hour=0, minute=0, second=0, microsecond=0)