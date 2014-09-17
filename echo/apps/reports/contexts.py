from echo.apps.projects.models import Project


def failed(project):
    return {'project': project}


def missing(project):
    return {'project': project}


def reports():
    return {'projects': Project.objects.all().order_by('name')}