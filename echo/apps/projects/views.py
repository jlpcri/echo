from datetime import datetime
import os

import pysftp

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings

from echo.apps.core import messages
from echo.apps.settings.models import Server
from echo.apps.projects.forms import ProjectForm, ServerForm, UploadForm
from echo.apps.projects.models import Language, Project, VoiceSlot, VUID
from echo.apps.projects import contexts, helpers


@login_required
def fetch(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        if p.bravo_server:
            try:
                with pysftp.Connection(p.bravo_server.address, username=str(p.bravo_server.account)) as sftp:
                    helpers.fetch_slots_from_server(p, sftp)
            except pysftp.ConnectionException:
                messages.danger(request, "Connection error to server \"{0}\"".format(p.bravo_server.name))
                return redirect("projects:project", pid)
            except pysftp.CredentialException:
                messages.danger(request, "Credentials error to server \"{0}\"".format(p.bravo_server.name))
                return redirect("projects:project", pid)
            except pysftp.AuthenticationException:
                messages.danger(request, "Authentication error to server \"{0}\"".format(p.bravo_server.name))
                return redirect("projects:project", pid)
            except pysftp.SSHException:
                messages.danger(request, "SSH error to server \"{0}\"".format(p.bravo_server.name))
                return redirect("projects:project", pid)
            messages.info(request, "Files from Bravo Server have been fetched")
            return redirect("projects:project", pid)
        messages.danger(request, "No server associated with project")
        return redirect("projects:project", pid)
    return HttpResponseNotFound()


@login_required
def join_project(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        p.users.add(request.user)
        p.save()
        messages.info(request, "You joined the project!")
        return redirect("projects:project", pid=pid)
    return HttpResponseNotFound()


@login_required
def leave_project(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        p.users.remove(request.user)
        p.save()
        messages.info(request, "You left the project")
        return redirect("projects:project", pid=pid)
    return HttpResponseNotFound()


@login_required
def new(request):
    if request.method == 'GET':
        return render(request, "projects/new.html", contexts.context_new())
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
                    return render(request, "projects/new.html", contexts.context_new(form))
            messages.danger(request, "Unable to create project")
            return render(request, "projects/new.html", contexts.context_new(form))
    return HttpResponseNotFound()


@login_required
def project(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        return render(request, "projects/project.html",
                      contexts.context_project(p, server_form=ServerForm(initial={'server': p.current_server_pk()})))
    elif request.method == 'POST':
        if "update_server" in request.POST:
            form = ServerForm(request.POST)
            p = get_object_or_404(Project, pk=pid)
            if form.is_valid():
                server = form.cleaned_data['server']
                if server is None:
                    if p.bravo_server is None:
                        return redirect("projects:project", pid=pid)
                    p.bravo_server = None
                    p.save()
                else:
                    if p.bravo_server is not None:
                        if server == p.bravo_server.name:
                            return redirect("projects:project", pid=pid)
                    p.bravo_server = Server.objects.get(name=server)
                    p.save()
                messages.success(request, "Updated server successfully")
                return redirect("projects:project", pid=pid)
            messages.danger(request, "Unable to update server")
            return render(request, "projects/project.html", contexts.context_project(p, server_form=form))
        elif "upload_file" in request.POST:
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
            return render(request, "projects/project.html", contexts.context_project(p, upload_form=form,
                                                                                     server_form=ServerForm(initial={
                                                                                         'server': p.current_server_pk()})))
        return redirect("projects:project", pid=pid)
    return HttpResponseNotFound()


@login_required
def projects(request):
    if request.method == 'GET':
        return render(request, "projects/projects.html", contexts.context_projects(request.user))
    return HttpResponseNotFound()


@login_required
def queue(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        lang = request.GET.get('language', '').strip().lower()
        if lang in p.language_list():
            slots = p.voiceslots_checked_out_by_user(request.user, filter_language=lang)
            if slots:
                return redirect("projects:testslot", pid=pid, vsid=slots[0].pk)
            else:
                slots = p.voiceslots_queue(checked_out=False, filter_language=lang)
                if slots:
                    return redirect("projects:testslot", pid=pid, vsid=slots[0].pk)
                else:
                    slots = p.voiceslots_queue(checked_out=True, filter_language=lang, older_than_ten=True)
                    if slots:
                        return redirect("projects:testslot", pid=pid, vsid=slots[0].pk)
            messages.info(request, 'No slots available for testing')
            return redirect("projects:project", pid)
        messages.danger(request, "Invalid language type for project {0}".format(p.name))
        return redirect("projects:project", pid)
    return HttpResponseNotFound()


@login_required
def submitslot(request, pid, vsid):
    if request.method == 'POST':
        if "submit_test" in request.POST:
            p = get_object_or_404(Project, pk=pid)
            slot = get_object_or_404(VoiceSlot, pk=vsid)
            test_result = request.POST.get('test_result', False)
            if test_result:
                slot.status = VoiceSlot.PASS
                slot.history = "{0}: Test passed at {1}.\n{2}\n".format(request.user.username, datetime.now(),
                                                                         request.POST['notes']) + slot.history
                slot.check_in(request.user)
                slot.save()
                # do updates to files here and get count for p pass
                count = p.voiceslots_match(slot, request)
            else:
                if not request.POST.get('notes', False):
                    messages.danger(request, "Please provide notes on test failure")
                    return redirect("projects:testslot", pid=pid, vsid=vsid)
                slot.status = VoiceSlot.FAIL
                slot.history = "{0}: Test failed at {1}.\n{2}\n".format(request.user.username, datetime.now(),
                                                                         request.POST['notes']) + slot.history
                slot.check_in(request.user)
                slot.save()
                # do updates to files here and get count for p failure
                count = p.voiceslots_match(slot, request)
                p.failure_count += 1
            p.tests_run += 1
            p.save()
            messages.success(request, "Tested voice slot \"{0}\", {1} matching slots updated".format(slot.name, count))
            return redirect("projects:project", pid=pid)
        elif "cancel_test" in request.POST:
            slot = get_object_or_404(VoiceSlot, pk=vsid)
            slot.check_in(request.user)
            return redirect("projects:project", pid=pid)
    return HttpResponseNotFound()


@login_required
def testslot(request, pid, vsid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        slot = get_object_or_404(VoiceSlot, pk=vsid)
        if p.bravo_server:
            try:
                with pysftp.Connection(p.bravo_server.address, username=str(p.bravo_server.account)) as conn:
                    remote_path = "{0}.wav".format(slot.filepath())
                    local_path = os.path.join(settings.MEDIA_ROOT, "{0}.wav".format(slot.name))
                    conn.get(remote_path, local_path)
                    filepath = "{0}{1}.wav".format(settings.MEDIA_URL, slot.name)
                    last_modified = int(conn.execute('stat -c %Y {0}'.format(remote_path))[0])
                    slot.check_out(request.user)
                    slot.history = "Downloaded file last modified on {0}\n".format(
                        datetime.fromtimestamp(last_modified).strftime("%b %d %Y, %H:%M")) + slot.history
            except IOError as e:
                print e
                messages.danger(request, "File missing on server \"{0}\"".format(p.bravo_server.name))
                slot.status = VoiceSlot.MISSING
                slot.history = "Attempted test, slot missing, {0}\n".format(datetime.now()) + slot.history
                return redirect("projects:project", pid)
            except pysftp.ConnectionException:
                messages.danger(request, "Connection error to server \"{0}\"".format(p.bravo_server.name))
                return redirect("projects:project", pid)
            except pysftp.CredentialException:
                messages.danger(request, "Credentials error to server \"{0}\"".format(p.bravo_server.name))
                return redirect("projects:project", pid)
            except pysftp.AuthenticationException:
                messages.danger(request, "Authentication error to server \"{0}\"".format(p.bravo_server.name))
                return redirect("projects:project", pid)
            except pysftp.SSHException:
                messages.danger(request, "SSH error to server \"{0}\"".format(p.bravo_server.name))
                return redirect("projects:project", pid)
            return render(request, "projects/testslot.html", contexts.context_testslot(p, slot, filepath))
        messages.danger(request, "No server associated with project")
        return redirect("projects:project", pid)
    return HttpResponseNotFound()


@login_required
def voiceslots(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        lang = request.GET.get('language', 'master').strip().lower()
        if lang == 'master' or lang in p.language_list():
            if request.GET.get('export', False) == 'csv':
                return contexts.context_language_csv(p, HttpResponse(content_type='text/csv'), lang)
            return render(request, "projects/language.html", contexts.context_language(p, language_type=lang))
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
                return render(request, "projects/language.html", contexts.context_language(p, language_type=lang))
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
        return render(request, "projects/vuid.html", contexts.context_vuid(VUID.objects.get(pk=vid)))
    return HttpResponseNotFound()


@login_required
def temp(request):
    if request.method == 'GET':
        print request.user_agent.browser
        print request.user_agent.browser.family
        return render(request, "projects/temp.html", {"browser": request.user_agent.browser.family.lower()})
    return HttpResponseNotFound()