from forms import ProjectForm, ServerForm, UploadForm
from models import Language, VUID


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