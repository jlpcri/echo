import datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from echo.apps.core import messages
from echo.apps.settings.models import Server
from forms import ProjectForm, ServerForm, UploadForm
from models import Language, Project, VoiceSlot, VUID
import contexts
import helpers


@login_required
def join_project(request, pid):
    if request.method == 'GET':
        if pid:
            project = get_object_or_404(Project, pk=pid)
        project.users.add(request.user)
        project.save()
        messages.info(request, "You joined the project!")
        return redirect("projects:project", pid=pid)
    return HttpResponseNotFound()


@login_required
def leave_project(request, pid):
    if request.method == 'GET':
        if pid:
            project = get_object_or_404(Project, pk=pid)
        project.users.remove(request.user)
        project.save()
        messages.info(request, "You left the project")
        return redirect("projects:project", pid=pid)
    return HttpResponseNotFound()


@login_required
def new(request):
    if request.method == 'GET':
        return render(request, "projects/new.html", contexts.new())
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
                    return render(request, "projects/new.html", contexts.new(form))
            messages.danger(request, "Unable to create project")
            return render(request, "projects/new.html", contexts.new(form))
    return HttpResponseNotFound()


@login_required
def project(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        return render(request, "projects/project.html",
                      contexts.project(p, server_form=ServerForm(initial={'server': p.current_server_pk()})))
    elif request.method == 'POST':
        if "update_server" in request.POST:
            form = ServerForm(request.POST)
            p = get_object_or_404(Project, pk=pid)
            if form.is_valid():
                sid = int(form.cleaned_data['server'])
                if sid == 0:
                    if p.bravo_server is None:
                        return redirect("projects:project", pid=pid)
                    p.bravo_server = None
                    p.save()
                else:
                    if p.bravo_server is not None:
                        if sid == p.bravo_server.pk:
                            return redirect("projects:project", pid=pid)
                    p.bravo_server = Server.objects.get(pk=sid)
                    p.save()
                messages.success(request, "Updated server successfully")
                return redirect("projects:project", pid=pid)
            messages.danger(request, "Unable to update server")
            return render(request, "projects/project.html", contexts.project(p, server_form=form))
        if "upload_file" in request.POST:
            form = UploadForm(request.POST, request.FILES)
            p = get_object_or_404(Project, pk=pid)
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
            return render(request, "projects/project.html", contexts.project(p, upload_form=form,
                                                                             server_form=ServerForm(initial={
                                                                             'server': p.current_server_pk()})))
        return redirect("projects:project", pid=pid)
    return HttpResponseNotFound()


@login_required
def projects(request):
    if request.method == 'GET':
        return render(request, "projects/projects.html", {'projects': Project.objects.all()})
    return HttpResponseNotFound()


@login_required
def submitslot(request, pid, vsid):
    if request.method == 'POST':
        if "submit_test" in request.POST:
            if pid:
                project = get_object_or_404(Project, pk=pid)
            if vsid:
                slot = get_object_or_404(VoiceSlot, pk=vsid)
            test_result = request.POST.get('test_result', False)
            if test_result:
                slot.status = VoiceSlot.PASS
                slot.history = u"{0}: Test passed at {1}.\n{2}\n".format(request.user.username, datetime.datetime.now(),
                                                                         request.POST['notes']) + slot.history
            else:
                if not request.POST.get('notes', False):
                    messages.danger(request, "Please provide notes on test failure")
                    return redirect("projects:testslot", pid=pid, vsid=vsid)
                slot.status = VoiceSlot.FAIL
                slot.history = u"{0}: Test failed at {1}.\n{2}\n".format(request.user.username, datetime.datetime.now(),
                                                                         request.POST['notes']) + slot.history
                project.failure_count += 1
            slot.check_in(request.user)
            slot.save()
            project.tests_run += 1
            project.save()
            messages.success(request, "Tested voice slot \"{0}\"".format(slot.name))
            return redirect("projects:project", pid=pid)
        elif "cancel_test" in request.POST:
            if vsid:
                slot = get_object_or_404(VoiceSlot, pk=vsid)
            slot.check_in(request.user)
            return redirect("projects:project", pid=pid)
    return HttpResponseNotFound()


@login_required
def testslot(request, pid, vsid):
    if request.method == 'GET':
        if pid:
            project = get_object_or_404(Project, pk=pid)
        if vsid:
            slot = get_object_or_404(VoiceSlot, pk=vsid)
        slot.check_out(request.user)
        return render(request, "projects/testslot.html", helpers.get_testslot_context(project, slot))
    return HttpResponseNotFound()


@login_required
def voiceslots(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        lang = request.GET.get('language', 'master').strip().lower()
        if lang == 'master' or lang in p.language_list():
            return render(request, "projects/language.html", contexts.language(p, language_type=lang))
    if request.method == 'POST':
        p = get_object_or_404(Project, pk=pid)
        lang = request.GET.get('language', 'master').strip().lower()
        if lang == 'master' or lang in p.language_list():
            if "update_slot" in request.POST:
                vsid = request.POST.get('vsid', "")
                if vsid:
                    slot = get_object_or_404(VoiceSlot, pk=vsid)
                    is_checkedout = request.POST.get('is_checkedout', False)
                    if is_checkedout == slot.checked_out:
                        messages.info(request, "Nothing to update for slot \"{0}\"".format(slot.name))
                        response = redirect("projects:voiceslots", pid=pid)
                        response['Location'] += '?language={0}'.format(lang)
                        return response
                    if request.POST.get('is_checkedout', False):
                        slot.check_out(request.user, forced=True)
                    else:
                        slot.check_in(request.user, forced=True)
                    messages.success(request, "Updated voice slot \"{0}\"".format(slot.name))
                    response = redirect("projects:voiceslots", pid=pid)
                    response['Location'] += '?language={0}'.format(lang)
                    return response
                messages.danger(request, "Unable to update voice slot")
                return render(request, "projects/language.html",  contexts.language(p, language_type=lang))
            elif "retest_slot" in request.POST:
                vsid = request.POST.get('vsid', "")
                if vsid:
                    slot = get_object_or_404(VoiceSlot, pk=vsid)
                    return redirect("projects:testslot", pid, vsid)
                messages.danger(request, "Unable to find voice slot")
                response = redirect("projects:voiceslots", pid=pid)
                return response
    return HttpResponseNotFound()


@login_required
def vuid(request, pid, vid):
    if request.method == 'GET':
        return render(request, "projects/vuid.html", helpers.get_vuid_context(VUID.objects.get(pk=vid)))
    return HttpResponseNotFound()