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
        if sort[0] == '-':
            reverse = True
            sort = sort[1:]
        else:
            reverse = False
        try:
            sorted_projects = sorted(projects, key=lambda p: p[sort], reverse=reverse)
            projects = sorted_projects
        except Exception:
            pass

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
    actions = Action.objects.filter(time__gte=start, time__lt=end)
    for u in user_list:
        users.append(
            {
                'user': u,
                'total': actions.filter(actor=u, type=Action.TESTER_PASS_SLOT).count() + Action.objects.filter(actor=u, type=Action.TESTER_FAIL_SLOT).count(),
                'passed': actions.filter(actor=u, type=Action.TESTER_PASS_SLOT).count(),
                'defective': actions.filter(actor=u, type=Action.TESTER_FAIL_SLOT).count(),
                'reports': actions.filter(actor=u, type=Action.REPORT_GENERATION).count(),
                'uploads': actions.filter(actor=u, type=Action.UPLOAD_VUID).count(),
                'projects': actions.filter(actor=u, type=Action.CREATE_PROJECT).count()
            }
        )

    if sort:
        if sort[0] == '-':
            reverse = True
            sort = sort[1:]
        else:
            reverse = False
        try:
            sorted_users = sorted(users, key=lambda p: p[sort], reverse=reverse)
            users = sorted_users
        except Exception:
            pass

    return {
        'overall': overall(),
        'users': users,
        'start': time.mktime(start.astimezone(tz=pytz.timezone('America/Chicago')).timetuple()),
        'end': time.mktime(end.astimezone(tz=pytz.timezone('America/Chicago')).timetuple()),
        'sort': sort
    }