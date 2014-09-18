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
    return response


def reports():
    return {'projects': Project.objects.all().order_by('name')}