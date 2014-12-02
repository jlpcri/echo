import unicodecsv
from echo.apps.projects.models import Project


def failed(project):
    return {'project': project}


def failed_csv(project, response):
    response['Content-Disposition'] = 'attachment; filename="{0}_failed.csv"'.format(project.name)
    writer = unicodecsv.writer(response)
    writer.writerow(["Name", "Path", "Language", "Verbiage", "History"])
    for slot in project.voiceslots_failed():
        writer.writerow([slot.name, slot.path, slot.language.name, slot.verbiage, slot.history])
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
    projects = Project.objects.all()
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
        projects = sorted(projects, key=lambda p: p.slots_passed())
    elif sort == '-missing':
        projects = sorted(projects, key=lambda p: p.slots_passed(), reverse=True)
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