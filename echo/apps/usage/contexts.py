import pytz
import time
from django.contrib.auth.models import User
from echo.apps.activity.models import Action
from echo.apps.projects.models import Project, VoiceSlot


def overall():
    overall_pass = Action.objects.filter(type=Action.TESTER_PASS_SLOT).count()
    overall_fail = Action.objects.filter(type=Action.TESTER_FAIL_SLOT).count()
    overall_total = overall_pass + overall_fail
    overall_auto_pass = Action.objects.filter(type=Action.AUTO_PASS_SLOT).count()
    overall_auto_fail = Action.objects.filter(type=Action.AUTO_FAIL_SLOT).count()
    overall_auto_missing = Action.objects.filter(type=Action.AUTO_MISSING_SLOT).count()
    overall_auto_new = Action.objects.filter(type=Action.AUTO_NEW_SLOT).count()
    overall_auto_total = overall_auto_pass + overall_auto_fail + overall_auto_missing + overall_auto_new
    voiceslot_pass_fail_total = VoiceSlot.objects.filter(status__in=[VoiceSlot.PASS, VoiceSlot.FAIL]).count()
    overall_rework_ratio = float(overall_total) / voiceslot_pass_fail_total if voiceslot_pass_fail_total else 0
    overall_auto_ratio = float(overall_auto_total) / overall_total if overall_total else 0
    return {
        'total': overall_pass + overall_fail,
        'passed': overall_pass,
        'defective': overall_fail,
        'auto_total': overall_auto_pass + overall_auto_fail,
        'auto_passed': overall_auto_pass,
        'auto_defective': overall_auto_fail,
        'auto_missing': overall_auto_missing,
        'rework_ratio': overall_rework_ratio,
        'auto_ratio': overall_auto_ratio
    }


def projects_context(start, end, sort=None):
    if sort == 'project_name':
        project_list = Project.objects.all().order_by('name')
    elif sort == '-project_name':
        project_list = Project.objects.all().order_by('-name')
    else:
        project_list = Project.objects.all()

    projects = []
    actions = Action.objects.filter(time__gte=start, time__lt=end)
    for p in project_list:
        project_pass = actions.filter(scope__project=p, type=Action.TESTER_PASS_SLOT).count()
        project_fail = actions.filter(scope__project=p, type=Action.TESTER_FAIL_SLOT).count()
        project_total = project_pass + project_fail
        project_auto_pass = actions.filter(scope__project=p, type=Action.AUTO_PASS_SLOT).count()
        project_auto_fail = actions.filter(scope__project=p, type=Action.AUTO_FAIL_SLOT).count()
        project_auto_missing = actions.filter(scope__project=p, type=Action.AUTO_MISSING_SLOT).count()
        project_auto_new = actions.filter(scope__project=p, type=Action.AUTO_NEW_SLOT).count()
        project_auto_total = project_auto_pass + project_auto_fail + project_auto_missing + project_auto_new
        project_rework_ratio = float(project_total) / p.slots_passed_and_failed() if p.slots_passed_and_failed() else 0
        project_auto_ratio = float(project_auto_total) / project_total if project_total else 0
        projects.append(
            {
                'project': p,
                'total': project_pass + project_fail,
                'passed': project_pass,
                'defective': project_fail,
                'auto_total': project_auto_pass + project_auto_fail,
                'auto_passed': project_auto_pass,
                'auto_defective': project_auto_fail,
                'auto_missing': project_auto_missing,
                'rework_ratio': project_rework_ratio,
                'auto_ratio': project_auto_ratio
            }
        )

    if sort:
        if sort == 'total':
            projects = sorted(projects, key=lambda p: p['total'])
        elif sort == '-total':
            projects = sorted(projects, key=lambda p: p['total'], reverse=True)
        elif sort == 'passed':
            projects = sorted(projects, key=lambda p: p['passed'])
        elif sort == '-passed':
            projects = sorted(projects, key=lambda p: p['passed'], reverse=True)
        elif sort == 'defective':
            projects = sorted(projects, key=lambda p: p['defective'])
        elif sort == '-defective':
            projects = sorted(projects, key=lambda p: p['defective'], reverse=True)
        elif sort == 'auto_total':
            projects = sorted(projects, key=lambda p: p['auto_total'])
        elif sort == '-auto_total':
            projects = sorted(projects, key=lambda p: p['auto_total'], reverse=True)
        elif sort == 'auto_passed':
            projects = sorted(projects, key=lambda p: p['auto_passed'])
        elif sort == '-auto_passed':
            projects = sorted(projects, key=lambda p: p['auto_passed'], reverse=True)
        elif sort == 'auto_defective':
            projects = sorted(projects, key=lambda p: p['auto_defective'])
        elif sort == '-auto_defective':
            projects = sorted(projects, key=lambda p: p['auto_defective'], reverse=True)
        elif sort == 'auto_missing':
            projects = sorted(projects, key=lambda p: p['auto_missing'])
        elif sort == '-auto_missing':
            projects = sorted(projects, key=lambda p: p['auto_missing'], reverse=True)
        elif sort == 'rework_ratio':
            projects = sorted(projects, key=lambda p: p['rework_ratio'])
        elif sort == '-rework_ratio':
            projects = sorted(projects, key=lambda p: p['rework_ratio'], reverse=True)
        elif sort == 'auto_ratio':
            projects = sorted(projects, key=lambda p: p['auto_ratio'])
        elif sort == '-auto_ratio':
            projects = sorted(projects, key=lambda p: p['auto_ratio'], reverse=True)

    return {
        'overall': overall(),
        'projects': projects,
        'start': time.mktime(start.astimezone(tz=pytz.timezone('America/Chicago')).timetuple()),
        'end': time.mktime(end.astimezone(tz=pytz.timezone('America/Chicago')).timetuple()),
        'sort': sort
    }


def users_context(start, end, sort=None):
    if sort == 'username':
        user_list = User.objects.all().order_by('username')
    elif sort == '-username':
        user_list = User.objects.all().order_by('-username')
    else:
        user_list = User.objects.all()

    users = []
    # print start
    # print type(start)
    # print end
    # print type(end)
    actions = Action.objects.filter(time__gte=start, time__lt=end)
    # print actions
    for u in user_list:
        users.append(
            {
                'user': u,
                'total': actions.filter(actor=u, type=Action.TESTER_PASS_SLOT).count() + actions.filter(actor=u, type=Action.TESTER_FAIL_SLOT).count(),
                'passed': actions.filter(actor=u, type=Action.TESTER_PASS_SLOT).count(),
                'defective': actions.filter(actor=u, type=Action.TESTER_FAIL_SLOT).count(),
                'reports': actions.filter(actor=u, type=Action.REPORT_GENERATION).count(),
                'uploads': actions.filter(actor=u, type=Action.UPLOAD_VUID).count(),
                'projects': actions.filter(actor=u, type=Action.CREATE_PROJECT).count()
            }
        )

    if sort:
        if sort == 'total':
            users = sorted(users, key=lambda u: u['total'])
        elif sort == '-total':
            users = sorted(users, key=lambda u: u['total'], reverse=True)
        elif sort == 'passed':
            users = sorted(users, key=lambda u: u['passed'])
        elif sort == '-passed':
            users = sorted(users, key=lambda u: u['passed'], reverse=True)
        elif sort == 'defective':
            users = sorted(users, key=lambda u: u['defective'])
        elif sort == '-defective':
            users = sorted(users, key=lambda u: u['defective'], reverse=True)
        elif sort == 'reports':
            users = sorted(users, key=lambda u: u['reports'])
        elif sort == '-reports':
            users = sorted(users, key=lambda u: u['reports'], reverse=True)
        elif sort == 'uploads':
            users = sorted(users, key=lambda u: u['uploads'])
        elif sort == '-uploads':
            users = sorted(users, key=lambda u: u['uploads'], reverse=True)
        elif sort == 'projects':
            users = sorted(users, key=lambda u: u['projects'])
        elif sort == '-projects':
            users = sorted(users, key=lambda u: u['projects'], reverse=True)

    return {
        'overall': overall(),
        'users': users,
        'start': time.mktime(start.astimezone(tz=pytz.timezone('America/Chicago')).timetuple()),
        'end': time.mktime(end.astimezone(tz=pytz.timezone('America/Chicago')).timetuple()),
        'sort': sort
    }