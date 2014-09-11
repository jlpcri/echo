from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from echo.apps.core import messages
from forms import ProjectForm, UploadForm
import helpers
from models import Language, Project, VoiceSlot, VUID


@login_required
def language(request, pid, lid):
    if request.method == 'GET':
        return render(request, "projects/language.html", helpers.get_language_context(Language.objects.get(pk=lid)))
    if request.method == 'POST':
        if "update_slot" in request.POST:
            vsid = request.POST.get('vsid', "")
            if vsid:
                slot = get_object_or_404(VoiceSlot, pk=vsid)
                if request.POST.get('is_checkedout', False):
                    slot.check_out(request.user)
                else:
                    slot.check_in(request.user)
                messages.success(request, "Updated voice slot \"{0}\"".format(slot.name))
                return redirect("projects:language", pid=pid, lid=lid)
            messages.danger(request, "Unable to update voice slot")
            return render(request, "projects/language.html",  helpers.get_language_context(Language.objects.get(pk=lid)))
        elif "retest_slot" in request.POST:
            messages.success(request, "Retest slot")
            return redirect("projects:language", pid=pid, lid=lid)
    return HttpResponseNotFound()


@login_required
def master(request, pid):
    if request.method == 'GET':
        return render(request, "projects/master.html", helpers.get_master_context(Project.objects.get(pk=pid)))
    if request.method == 'POST':
        if "update_slot" in request.POST:
            vsid = request.POST.get('vsid', "")
            if vsid:
                slot = get_object_or_404(VoiceSlot, pk=vsid)
                if request.POST.get('is_checkedout', False):
                    slot.check_out(request.user)
                else:
                    slot.check_in(request.user)
                messages.success(request, "Updated voice slot \"{0}\"".format(slot.name))
                return redirect("projects:master", pid=pid)
            messages.danger(request, "Unable to update voice slot")
            return render(request, "projects/master.html",  helpers.get_master_context(Language.objects.get(pk=pid)))
        elif "retest_slot" in request.POST:
            messages.success(request, "Retest slot")
            return redirect("projects:master", pid=pid)
    return HttpResponseNotFound()


@login_required
def new(request):
    if request.method == 'GET':
        return render(request, "projects/new.html", {'project_form': ProjectForm()})
    elif request.method == 'POST':
        if "create_project" in request.POST:
            form = ProjectForm(request.POST, request.FILES)
            if form.is_valid():
                n = form.cleaned_data['name']
                p = Project(name=n)
                try:
                    p.full_clean()
                    p.save()
                    p.users.add(request.user)
                    p.save()
                    messages.success(request, "Created project")
                    if 'file' in request.FILES and request.FILES['file'].name.endswith('.xlsx'):
                        result = helpers.upload_vuid(form.cleaned_data['file'], request.user, p)
                        if result['valid']:
                            messages.success(request, result["message"])
                        else:
                            messages.danger(request, result['message'])
                    elif 'file' in request.FILES:
                        messages.danger(request, "Invalid file type, unable to upload (must be .xlsx)")
                    return redirect("projects:project", pid=p.pk)
                except ValidationError as e:
                    if 'name' in e.message_dict:
                        messages.danger(request, e.message_dict.get('name')[0])
                    return render(request, "projects/new.html", {'project_form': form})
            messages.danger(request, "Unable to create project")
            return render(request, "projects/new.html", {'project_form': form})
    return HttpResponseNotFound()


@login_required
def project(request, pid):
    if request.method == 'GET':
        p = Project.objects.get(pk=pid)
        languages = Language.objects.filter(project=p)
        vuids = VUID.objects.filter(project=p)
        return render(request, "projects/project.html",
                      {'project': p, 'languages': languages, 'vuids': vuids, 'upload_form': UploadForm()})
    elif request.method == 'POST':
        if "upload_file" in request.POST:
            form = UploadForm(request.POST, request.FILES)
            p = Project.objects.get(pk=pid)
            if form.is_valid():
                if 'file' in request.FILES and request.FILES['file'].name.endswith('.xlsx'):
                    result = helpers.upload_vuid(form.cleaned_data['file'], request.user, p)
                    if result['valid']:
                        messages.success(request, result["message"])
                    else:
                        messages.danger(request, result['message'])
                elif 'file' in request.FILES:
                    messages.danger(request, "Invalid file type, unable to upload (must be .xlsx)")
                return redirect("projects:project", pid=pid)
            messages.danger(request, "Unable to upload file")
            return render(request, "projects/project.html",
                          {'project': p, 'vuids': VUID.objects.filter(project=p), 'upload_form': form})
        return redirect("projects:project", pid=pid)
    return HttpResponseNotFound()


@login_required
def projects(request):
    if request.method == 'GET':
        return render(request, "projects/projects.html", {'projects': Project.objects.all()})
    return HttpResponseNotFound()


@login_required
def vuid(request, pid, vid):
    if request.method == 'GET':
        return render(request, "projects/vuid.html", helpers.get_vuid_context(VUID.objects.get(pk=vid)))
    return HttpResponseNotFound()