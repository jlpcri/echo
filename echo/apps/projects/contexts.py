from forms import ProjectForm, ServerForm, UploadForm
from models import Project, Language, VUID
from openpyxl import load_workbook
import unicodecsv


def context_home(user):
    return {
        'projects': Project.objects.filter(users__pk=user.pk).order_by('name')
    }


def context_language(project, language_type='master'):
    return {
        'project': project,
        'language_type': language_type,
        'slots': project.voiceslots() if 'master' in language_type else project.voiceslots(
            filter_language=language_type)
    }


def context_language_csv(project, response, language_type='master'):
    response['Content-Disposition'] = 'attachment; filename="{0}_{1}.csv"'.format(project.name, language_type)
    writer = unicodecsv.writer(response)
    writer.writerow(["Name", "Path", "Language", "Verbiage", "History", "Status", "VUID Name", "VUID Date", "User"])
    if language_type == 'master':
        for slot in project.voiceslots().order_by('name'):
            writer.writerow(
                [slot.name, slot.path, slot.language.name, slot.verbiage, slot.history, slot.status, slot.vuid.filename,
                 slot.vuid.upload_date, slot.vuid.upload_by.username])
    else:
        for slot in project.voiceslots(filter_language=language_type).order_by('name'):
            writer.writerow(
                [slot.name, slot.path, slot.language.name, slot.verbiage, slot.history, slot.status, slot.vuid.filename,
                 slot.vuid.upload_date, slot.vuid.upload_by.username])
    return response


def context_new(project_form=ProjectForm()):
    return {'project_form': project_form}


def context_project(project, upload_form=UploadForm(), server_form=ServerForm(initial={'server': 0})):
    return {
        'project': project,
        'languages': Language.objects.filter(project=project),
        'vuids': VUID.objects.filter(project=project),
        'upload_form': upload_form,
        'server_form': server_form
    }


def context_projects(user):
    projects = Project.objects.filter(users__pk=user.pk).order_by('name') | Project.objects.all().exclude(users__pk=user.pk).order_by('name')
    return {
        'projects': projects
    }


def context_testslot(project, slot, filepath):
    return {
        'project': project,
        'slot': slot,
        'file': filepath
    }


def context_vuid(vuid):
    wb = load_workbook(vuid.file.url)
    ws = wb.active
    return {
        'vuid': vuid,
        'headers': [i.value for i in ws.rows[0]],
        'path': ws['A2'].value,
        'records': [r for r in ws.rows[2:]]
    }