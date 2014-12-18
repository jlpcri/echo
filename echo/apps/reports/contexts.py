import unicodecsv
from echo.apps.activity.models import Action
from echo.apps.projects.models import Project, VoiceSlot


def failed(project):
    return {'project': project}


def failed_csv(project, response):
    response['Content-Disposition'] = 'attachment; filename="{0}_failed.csv"'.format(project.name)
    writer = unicodecsv.writer(response)
    writer.writerow(["Name", "Path", "Language", "Verbiage", "Test Time", "Failure Cause"])
    for slot in project.voiceslots().filter(status=VoiceSlot.FAIL):
        action = Action.objects.filter(scope__voiceslot=slot, type__in=[Action.TESTER_FAIL_SLOT, Action.AUTO_FAIL_SLOT]).latest('time')
        writer.writerow([slot.name, slot.path, slot.language.name, slot.verbiage, action.time, action.description])
    return response


def missing(project):
    return {'project': project}


def missing_csv(project, response):
    response['Content-Disposition'] = 'attachment; filename="{0}_missing.csv"'.format(project.name)
    writer = unicodecsv.writer(response)
    writer.writerow(["Name", "Full Path"])
    for slot in project.voiceslots_missing():
        writer.writerow([slot.name, "{0}/{1}".format(slot.path, slot.name)])
    return response


def reports_context(sort=None):
    projects = Project.objects.all().exclude(status=Project.CLOSED)
    if sort == 'project_name':
        projects = projects.order_by('name')
    elif sort == '-project_name':
        projects = projects.order_by('-name')
    elif sort == 'passed':
        projects = sorted(projects, key=lambda p: p.slots_passed())
    elif sort == '-passed':
        projects = sorted(projects, key=lambda p: p.slots_passed(), reverse=True)
    elif sort == 'defective':
        projects = sorted(projects, key=lambda p: p.slots_failed())
    elif sort == '-defective':
        projects = sorted(projects, key=lambda p: p.slots_failed(), reverse=True)
    elif sort == 'missing':
        projects = sorted(projects, key=lambda p: p.slots_missing())
    elif sort == '-missing':
        projects = sorted(projects, key=lambda p: p.slots_missing(), reverse=True)
    elif sort == 'total':
        projects = sorted(projects, key=lambda p: p.slots_total())
    elif sort == '-total':
        projects = sorted(projects, key=lambda p: p.slots_total(), reverse=True)
    elif sort == 'progress':
        projects = sorted(projects, key=lambda p: p.slots_tested_percent())
    elif sort == '-progress':
        projects = sorted(projects, key=lambda p: p.slots_tested_percent(), reverse=True)
    elif sort == 'testers':
        projects = sorted(projects, key=lambda p: p.users_total())
    elif sort == '-testers':
        projects = sorted(projects, key=lambda p: p.users_total(), reverse=True)

    return {
        'projects': projects,
        'sort': sort
    }