from forms import ProjectForm, ServerForm, UploadForm
from models import Project, Language, VUID


def home(user):
    return {
        'projects': Project.objects.filter(users__pk=user.pk)
    }


def language(p, language_type='master'):
    return {
        'project': p,
        'language_type': language_type,
        'slots': p.voiceslots() if 'master' in language_type else p.voiceslots(filter_language=language_type)
    }


def new(project_form=ProjectForm()):
    return {'project_form': project_form}


def project(p, upload_form=UploadForm(), server_form=ServerForm(initial={'server': 0})):
    return {
        'project': p,
        'languages': Language.objects.filter(project=p),
        'vuids': VUID.objects.filter(project=p),
        'upload_form': upload_form,
        'server_form': server_form
    }