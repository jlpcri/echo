from datetime import datetime, timedelta
import json
import os
import uuid

import pysftp

from django.core.urlresolvers import reverse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from echo.apps.activity.models import Action
from echo.apps.core import messages
from echo.apps.settings.models import Server
from echo.apps.projects.forms import ProjectForm, ServerForm, UploadForm, ProjectRootPathForm
from echo.apps.projects.models import Language, Project, VoiceSlot, VUID, UpdateStatus
from echo.apps.projects import contexts, helpers
from echo.apps.projects.tasks import update_file_statuses


@login_required
def fetch(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        if p.bravo_server:
            try:
                with pysftp.Connection(p.bravo_server.address, username=p.bravo_server.account,
                                       private_key=settings.PRIVATE_KEY) as sftp:
                    result = helpers.fetch_slots_from_server(p, sftp, request.user)
                    if result['valid']:
                        messages.success(request, result["message"])
                        Action.log(request.user, Action.UPDATE_FILE_STATUSES, 'File status update ran', p)
                    else:
                        messages.danger(request, result['message'])
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
        messages.danger(request, "No server associated with project")
        return redirect("projects:project", pid)
    return HttpResponseNotFound()


@login_required
def join_project(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        page = request.GET.get('page', '')
        p.users.add(request.user)
        p.save()
        Action.log(request.user, Action.TESTER_JOIN_PROJECT, u'Joined project', p)
        messages.info(request, "You joined the project!")
        if page == "home":
            return redirect("core:home")
        elif page == "projects":
            return redirect("projects:projects")
        return redirect("projects:project", pid=pid)
    return HttpResponseNotFound()


@login_required
def leave_project(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        page = request.GET.get('page', '')
        p.users.remove(request.user)
        p.save()
        Action.log(request.user, Action.TESTER_LEAVE_PROJECT, u'Left project', p)
        messages.info(request, "You left the project")
        if page == "home":
            return redirect("core:home")
        elif page == "projects":
            return redirect("projects:projects")
        return redirect("projects:project", pid=pid)
    return HttpResponseNotFound()


@transaction.atomic
@login_required
def new(request):
    if request.method == 'GET':
        return render(request, "projects/new.html", contexts.context_new())
    elif request.method == 'POST':
        if "create_project" in request.POST:
            form = ProjectForm(request.POST, request.FILES)
            if form.is_valid():
                # Check if default Bravo Server exist
                try:
                    bravo_server = Server.objects.get(active=True)
                except Server.DoesNotExist:
                    messages.danger(request, "Please set default Bravo Server first.")
                    return render(request, "projects/new.html", contexts.context_new(form))

                n = form.cleaned_data['name']
                root_path = form.cleaned_data['root_path']
                if root_path and not os.path.isabs(root_path):
                    messages.danger(request, 'Bravo Server Root Path Format Incorrect')
                    return render(request, 'projects/new.html', contexts.context_new(form))

                # remove last slash of root path
                while root_path and root_path[-1] == '/':
                    root_path = root_path[:-1]

                p = Project(name=n)
                try:
                    p.full_clean()
                    p.save()
                    p.users.add(request.user)
                    p.bravo_server = bravo_server  # set default bravo server
                    p.root_path = root_path
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
                    Action.log(request.user, Action.CREATE_PROJECT, '{0} created'.format(p.name), p)
                    return redirect("projects:project", pid=p.pk)
                except ValidationError as e:
                    if 'name' in e.message_dict:
                        messages.danger(request, e.message_dict.get('name')[0])
                    return render(request, "projects/new.html", contexts.context_new(form))
            messages.danger(request, "Unable to create project")
            return render(request, "projects/new.html", contexts.context_new(form))
    return HttpResponseNotFound()


@transaction.atomic
@login_required
def project(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        # status = UpdateStatus.objects.get_or_create(project=p)[0]
        # if status.running:
        #     status.running = False
        #     status.save()
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

                    # force update file status from bravo server
                    old_bravo_server = p.bravo_server
                    p.bravo_server = Server.objects.get(name=server)
                    p.save()
                    if not able_update_file_status(request, p):
                        p.bravo_server = old_bravo_server
                        p.save()
                        messages.warning(request, 'Cannot update file status, set Bravo Server back')
                        return redirect("projects:project", pid=pid)

                Action.log(request.user,
                           Action.UPDATE_BRAVO_SERVER,
                           u'Bravo server updated to ' + unicode(server),
                           p)
                messages.success(request, "Updated server successfully")
                return redirect("projects:project", pid=pid)
            messages.danger(request, "Unable to update server")
            return render(request, "projects/project.html", contexts.context_project(p, server_form=form))
        elif "upload_file" in request.POST:
            form = UploadForm(request.POST, request.FILES)
            p = get_object_or_404(Project, pk=pid)
            if form.is_valid():
                # if user not member in CS, PM, Superuser cannot upload
                if not (request.user.usersettings.creative_services or request.user.usersettings.project_manager or request.user.is_superuser):
                    messages.danger(request, 'You have no authority to upload.')
                elif 'file' in request.FILES and request.FILES['file'].name.endswith('.xlsx'):
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
        elif "update_root_path" in request.POST:
            form = ProjectRootPathForm(request.POST)
            p = get_object_or_404(Project, pk=pid)
            if form.is_valid():
                root_path = form.cleaned_data['root_path']

                if not os.path.isabs(root_path):
                    messages.danger(request, 'Bravo Server Root Path Format Incorrect')
                    return redirect('projects:project', pid=pid)

                #remove last slash of root path
                while root_path and root_path[-1] == '/':
                    root_path = root_path[:-1]

                if p.root_path and not helpers.verify_update_root_path(p, root_path):
                    messages.danger(request, 'New root path not allowed')
                    return redirect('projects:project', pid=pid)

                p.root_path = root_path
                p.save()
                Action.log(request.user,
                           Action.UPDATE_ROOT_PATH,
                           u'Bravo server root path updated to ' + unicode(root_path),
                           p)
                messages.success(request, 'Updated Bravo Server Path Successfully')
                return redirect('projects:project', pid=pid)
        return redirect("projects:project", pid=pid)
    return HttpResponseNotFound()


@login_required
def able_update_file_status(request, p):
    try:
        with pysftp.Connection(p.bravo_server.address, username=p.bravo_server.account,
                               private_key=settings.PRIVATE_KEY) as sftp:
            result = helpers.fetch_slots_from_server(p, sftp, request.user)
            if result['valid']:
                messages.success(request, result["message"])
                Action.log(request.user, Action.UPDATE_FILE_STATUSES, 'File status update ran', p)
                return True
            else:
                messages.danger(request, result['message'])
                return False
    except (pysftp.ConnectionException,
            pysftp.CredentialException,
            pysftp.AuthenticationException,
            pysftp.SSHException):
        messages.danger(request, "Connection error to server \"{0}\"".format(p.bravo_server.name))
        return False


@login_required
def project_progress(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        data = {
            'running': UpdateStatus.objects.get_or_create(project=p)[0].running,
            'passed': p.slots_passed(),
            'passed_percent': p.slots_passed_percent(),
            'failed': p.slots_failed(),
            'failed_percent': p.slots_failed_percent(),
            'missing': p.slots_missing(),
            'missing_percent': p.slots_missing_percent(),
            'ready': p.slots_ready(),
            'ready_percent': p.slots_ready_percent(),
            'new': p.slots_untested(),
            'new_percent': p.slots_untested_percent()
        }
        return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def projects(request):
    if request.method == 'GET':
        tab_types = [
            'my',
            'csp',
            'cep',
            'archive'
        ]
        sort_types = [
            'project_name',
            '-project_name',
            'created_date',
            '-created_date',
            'last_modified',
            '-last_modified',
            'total_prompts',
            '-total_prompts',
            'user_count',
            '-user_count'
        ]
        # if tab and sort are not present, set to empty
        tab = request.GET.get('tab', '')
        sort = request.GET.get('sort', '')

        # if tab empty, set to defaults
        if not tab:
            projects = Project.objects.filter(users__pk=request.user.pk, status=Project.TESTING)
            # if not join any project , navigate to All Projects tab
            if projects.count() == 0:
                tab = 'csp'
            else:
                tab = 'my'

        # if sort empty, set to default
        sort = sort if sort else 'project_name'
        # validate tab and sort
        if tab in tab_types and sort in sort_types:
            return render(request, "projects/projects.html", contexts.context_projects(request.user, tab, sort))
    return HttpResponseNotFound()


@login_required
def queue(request, pid):
    if request.method == 'GET':
        # check if voice slot already listened
        finish_listen = request.GET.get('listened', 'notyet')
        fail_select = request.GET.get('fail_select', False)
        p = get_object_or_404(Project, pk=pid)
        # check if update file status from bravo server
        if not p.voiceslots().filter(status=VoiceSlot.READY).exists():
            messages.danger(request, 'No files are pending test.')
            return redirect('projects:project', pid=pid)
        lang = get_object_or_404(Language, project=p, name=request.GET.get('language', '__malformed').lower())
        slots_out = request.user.voiceslot_set
        # TODO check this block
        if slots_out.count() < 0:
            slot = slots_out.first()
            if slot.language.pk == lang.pk:
                slot_file = slot.download()
                return render(request, "projects/testslot.html", contexts.context_testslot(request.user_agent.browser, p, slot, slot_file, finish_listen, fail_select))
            else:
                for slot in slots_out:
                    slot.check_in()
        slot = lang.voiceslot_set.filter(status=VoiceSlot.READY, checked_out=False).first()
        # check if all voice slots have been tested
        if not slot:
            messages.warning(request, 'No new voice slots available to be tested')
            return redirect('projects:project', pid=pid)
        # check if project has default bravo server
        if not p.bravo_server:
            messages.warning(request, 'Please set default bravo server')
            return redirect('projects:project', pid=pid)

        slot_file = slot.download()
        return render(request, "projects/testslot.html", contexts.context_testslot(request.user_agent.browser, p, slot, slot_file, finish_listen, fail_select))
    elif request.method == 'POST':
        p = get_object_or_404(Project, pk=pid)
        lang = get_object_or_404(Language, project=p, name=request.GET.get('language', '__malformed').lower())
        tested_slot = get_object_or_404(VoiceSlot, pk=request.POST.get('slot-id', -1))
        if "cancel_test" in request.POST:
            tested_slot.check_in(request.user)
            return redirect("projects:project", pid=pid)
        elif "submit_test" in request.POST:
            test_result = request.POST.get('slot_status', False)
            finish_listen_post = request.POST.get('finish_listen', 'notyet')
            already_listen_post = request.GET.get('listened', 'notyet')
            fail_select = request.GET.get('fail_select', False)

            # finish_listen to check if finish listened without Pass/Fail selection
            if not test_result and (finish_listen_post == 'heard' or already_listen_post == 'heard') and fail_select != 'selected':

                messages.danger(request, "Please enter a pass or fail")
                return HttpResponseRedirect(reverse("projects:queue", args=(p.pk, )) + "?language=" + lang.name + '&listened=heard')
            elif test_result == 'pass':
                tested_slot.status = VoiceSlot.PASS
                tested_slot.check_in(request.user)
                tested_slot.save()
                Action.log(request.user,
                           Action.TESTER_PASS_SLOT,
                           '{0} passed in queue testing'.format(tested_slot.name),
                           tested_slot)
                # do updates to files here and get count for p pass
                count = p.voiceslots_match(tested_slot, request)
            else:
                if not request.POST.get('notes', False):
                    messages.danger(request, "Please provide notes on test failure")
                    return HttpResponseRedirect(reverse("projects:queue", args=(p.pk, )) + "?language=" + lang.name + '&listened=heard&fail_select=selected')
                tested_slot.status = VoiceSlot.FAIL
                tested_slot.check_in(request.user)
                tested_slot.save()
                Action.log(request.user, Action.TESTER_FAIL_SLOT, request.POST['notes'], tested_slot)
                # do updates to files here and get count for p failure
                count = p.voiceslots_match(tested_slot, request)
                p.failure_count += 1
            p.tests_run += 1
            p.save()
            if count > 0:
                messages.success(request, "{0} matching slots updated".format(count))

            slot_filter = lang.voiceslot_set.filter(status=VoiceSlot.READY, checked_out=False)
            if slot_filter.count() > 0:
                slot = slot_filter.first()
            else:
                ten_minutes_ago = datetime.now() - timedelta(minutes=10)
                slot_filter = lang.voiceslot_set.filter(status=VoiceSlot.READY, checked_out=True,
                                                        checked_out_time__lte = ten_minutes_ago)
                if slot_filter.count() > 0:
                    slot = slot_filter.first()
                else:
                    messages.success(request, "All slots in this language are tested or recently checked out for testing.")
                    return redirect("projects:project", pid=pid)
            slot_file = slot.download()

            # reset if finish listen to not yet
            #finish_listen = 'notyet'
            #fail_select = False

            #return render(request, "projects/testslot.html", contexts.context_testslot(request.user_agent.browser, p, slot, slot_file, finish_listen, fail_select))
            return HttpResponseRedirect(reverse("projects:queue", args=(p.pk, )) + "?language=" + lang.name)
        else:
            return HttpResponseNotFound()

@login_required
def submitslot(request, vsid):
    if request.method == 'POST':
        if "submit_test" in request.POST:
            slot = get_object_or_404(VoiceSlot, pk=vsid)
            p = slot.language.project
            slot_status = request.POST.get('slot_status', False)

            finish_listen_post = request.POST.get('finish_listen', 'notyet')
            already_listen_post = request.GET.get('listened', 'notyet')
            fail_select = request.GET.get('fail_select', False)

            if not slot_status and (finish_listen_post == 'heard' or already_listen_post == 'heard') and fail_select != 'selected':
                messages.danger(request, "Please enter a pass or fail")
                #return redirect("projects:testslot", pid=p.pk, vsid=vsid)
                response = redirect("projects:testslot", pid=p.pk, vsid=vsid)
                response['Location'] += '?listened=heard'
                return response
            if slot_status == 'pass':
                slot.status = VoiceSlot.PASS
                slot.check_in(request.user)
                slot.save()
                Action.log(request.user, Action.TESTER_PASS_SLOT, '{0} passed by manual testing'.format(slot.name), slot)
                # do updates to files here and get count for p pass
                count = p.voiceslots_match(slot, request)
            else:
                if not request.POST.get('notes', False):
                    messages.danger(request, "Please provide notes on test failure")
                    response = redirect("projects:testslot", pid=p.pk, vsid=vsid)
                    response['Location'] += '?listened=heard&fail_select=selected'
                    return response
                slot.status = VoiceSlot.FAIL
                slot.check_in(request.user)
                slot.save()
                Action.log(request.user, Action.TESTER_FAIL_SLOT, request.POST['notes'], slot)
                # do updates to files here and get count for p failure
                count = p.voiceslots_match(slot, request)
                p.failure_count += 1
            p.tests_run += 1
            p.save()
            messages.success(request, u"Tested voice slot \"{0}\", {1} matching slots updated".format(slot.name, count))
            return redirect("projects:project", pid=p.pk)
        elif "cancel_test" in request.POST:
            slot = get_object_or_404(VoiceSlot, pk=vsid)
            slot.check_in(request.user)
            return redirect("projects:project", pid=slot.language.project.pk)
    return HttpResponseNotFound()


@login_required
def testslot(request, pid, vsid):
    if request.method == 'GET':
        finish_listen = request.GET.get('listened', 'notyet')
        fail_select = request.GET.get('fail_select', False)
        p = get_object_or_404(Project, pk=pid)
        slot = get_object_or_404(VoiceSlot, pk=vsid)
        if p.bravo_server:
            try:
                with pysftp.Connection(p.bravo_server.address, username=p.bravo_server.account,
                                       private_key=settings.PRIVATE_KEY) as conn:
                    remote_path = slot.filepath()
                    filename = "{0}.wav".format(str(uuid.uuid4()))
                    local_path = os.path.join(settings.MEDIA_ROOT, filename)
                    conn.get(remote_path, local_path)
                    filepath = settings.MEDIA_URL + filename
                    slot.check_out(request.user)
            except IOError as e:
                messages.danger(request, "File missing on server \"{0}\"".format(p.bravo_server.name))
                slot.status = VoiceSlot.MISSING
                slot.save()
                Action.log(request.user, Action.AUTO_MISSING_SLOT, 'Slot found missing by individual slot test', slot)
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
            return render(request, "projects/testslot.html", contexts.context_testslot(request.user_agent.browser, p, slot, filepath, finish_listen, fail_select))
        messages.danger(request, "No server associated with project")
        return redirect("projects:project", pid)
    return submitslot(request, vsid)


@login_required
def voiceslots(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        # check if update file status from bravo server
        if not p.voiceslots().filter(status__in=[VoiceSlot.READY, VoiceSlot.PASS, VoiceSlot.FAIL, VoiceSlot.MISSING]).exists():
            messages.danger(request, 'Please update file statuses from bravo server')
            return redirect('projects:project', pid=pid)

        lang = request.GET.get('language', 'master').strip().lower()
        if lang == 'master' or lang in p.language_list():
            if request.GET.get('export', False) == 'csv':
                return contexts.context_language_csv(p, HttpResponse(content_type='text/csv'), lang)
            return render(request, "projects/language.html", contexts.context_language(request.user, p, language_type=lang))
    if request.method == 'POST':
        p = get_object_or_404(Project, pk=pid)
        lang = request.GET.get('language', 'master').strip().lower()
        if lang == 'master' or lang in p.language_list():
            vsid = request.POST.get('vsid', "")

            if "update_slot" in request.POST:
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
                if vsid:
                    slot = get_object_or_404(VoiceSlot, pk=vsid)
                    return redirect("projects:testslot", pid, vsid)
                messages.danger(request, "Unable to find voice slot")
                response = redirect("projects:voiceslots", pid=pid)
                return response

            elif "delete_slot" in request.POST:
                if vsid:
                    slot = get_object_or_404(VoiceSlot, pk=vsid)
                    slot.delete()
                    return render(request, "projects/language.html", contexts.context_language(request.user, p, language_type=lang))
                messages.danger(request, "Unable to find voice slot")
                return redirect("projects:voiceslots", pik=pid)

    return HttpResponseNotFound()


@login_required
def vuid(request, pid, vid):
    if request.method == 'GET':
        return render(request, "projects/vuid.html", contexts.context_vuid(VUID.objects.get(pk=vid)))
    return HttpResponseNotFound()


@login_required
def temp(request):
    if request.method == 'GET':
        return render(request, "projects/temp.html", contexts.context_temp(request.user_agent.browser))
    return HttpResponseNotFound()

@login_required
def archive_project(request, pid):
    if request.method == 'GET':
        p = get_object_or_404(Project, pk=pid)
        action = Action.ARCHIVE_PROJECT
        note = 'Archive Project.'
        if p.status == Project.TESTING:
            p.status = Project.CLOSED
        elif p.status == Project.CLOSED:
            p.status = Project.TESTING
            action = Action.UN_ARCHIVE_PROJECT
            note = 'Un Archive Project.'
        p.save()
        Action.log(request.user, action, note, p)

    return redirect("projects:project", pid)

@login_required
@csrf_exempt
def initiate_status_update(request, pid):
    """
    Kicks off the request from "Update File Statuses"
    """
    if not request.method == "POST":
        raise Http404
    project = Project.objects.get(pk=pid)
    status = UpdateStatus.objects.get_or_create(project=project)[0]
    if status.running:
            return HttpResponse(json.dumps({'success': False, 'message': 'Task already running'}),
                                content_type="application/json")
    query_item = update_file_statuses.delay(project_id=pid, user_id=request.user.pk)
    status.query_id = query_item
    status.running = True
    status.save()
    Action.log(request.user, Action.UPDATE_FILE_STATUSES, 'Updated file statuses', Project.objects.get(pk=pid))
    return HttpResponse(json.dumps({'success': True}), content_type="application/json")


@login_required
@csrf_exempt
def delete_slot(request, slot_id):
    if request.method == 'GET':
        raise Http404
    if request.method == 'POST':
        if request.user.usersettings.creative_services or request.user.usersettings.project_manager or request.user.is_superuser:
            try:
                slot = get_object_or_404(VoiceSlot, pk=slot_id)
                slot.delete()
                messages.success(request, 'Voice Slot \"{0}\" has been deleted.'.format(slot.name))
                return HttpResponse(json.dumps({
                    'success': True
                }))
            except Exception as e:
                return HttpResponse(json.dumps({
                    'success': False,
                    'error': e.message
                }))
        else:
            return HttpResponse(json.dumps({
                'success': False,
                'error': 'You have no authority to perform this operation.'
            }))
