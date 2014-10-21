from collections import Counter
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from echo.apps.elpis.utils.directory_tree import DirectoryTreeWithPayload
from echo.apps.projects.models import Project, Language
from echo.apps.settings.models import PreprodServer


@login_required
def dashboard(request, pid):
    """Project file transfer verification dashboard"""
    p = get_object_or_404(Project, pk=pid)
    preprod_servers = PreprodServer.objects.all()
    return render(request, 'elpis/elpis.html', {'project': p, 'preprod_servers': preprod_servers})


@login_required
def set_preprod_server(request, pid):
    """Ajax view to associate a preprod server with a project"""
    p = get_object_or_404(Project, pk=pid)
    try:
        p.preprod_server = PreprodServer.objects.get(pk=int(request.POST['preprod-server']))
        p.save()
        paths = p.preprod_server.get_clients()
        if p.name.lower() in paths:
            match = True
        else:
            match = False
        json_data = json.dumps({'success': True, 'type': p.preprod_server.application_type, 'paths': paths,
                                'match': match})
    except Exception as e:
        json_data = json.dumps({'success': False, 'error': str(e)})
    return HttpResponse(json_data, content_type="application/json")


@login_required
def set_preprod_path(request, pid):
    """Ajax view to associate a preprod path with a project"""
    p = get_object_or_404(Project, pk=pid)
    try:
        p.set_preprod_path(request.POST['preprod-path'])
        json_data = json.dumps({'success': True, 'path': p.preprod_path})
    except Exception as e:
        json_data = json.dumps({'success': False, 'error': str(e)})
    return HttpResponse(json_data, content_type="application/json")


@login_required
def verify_file_transfer(request, pid):
    """View to identify potential problems with file transfer from Bravo to Preprod"""
    p = get_object_or_404(Project, pk=pid)
    if request.method == 'GET':
        # Send list of Producer applications on GET request.
        apps = p.get_applications()
        json_data = json.dumps({'apps': apps})
        print json_data
        return HttpResponse(json_data, content_type="application/json")
    elif request.method == 'POST':
        apps = request.POST.getlist('applications')
        files = p.preprod_server.get_wavs_from_apps(p.preprod_client_id, apps)
        language_list = Language.objects.filter(project=p)
        missing_slots = set()
        file_struct = DirectoryTreeWithPayload('/usr/local/tuvox/public/Projects/', str)
        for language in language_list:
            # Get files on Producer, per language
            if language.name in files.keys():
                lang_name = language.name
            elif language.name == 'english' and 'en-us' in files.keys():
                lang_name = 'en-us'
            elif language.name == 'spanish' and 'es-us' in files.keys():
                lang_name = 'es-us'
            else:
                lang_name = language.name
                print language.name + " used by default from " + repr(files.keys())
            file_name_count = Counter([f.filename.split('/')[-1] for f in files[lang_name]])

            for f in files[lang_name]:
                file_struct.add(f.filename, ('untracked',))

            # Check for matches
            for slot in language.voiceslot_set.all():
                slot_name = slot.name.split('/')[-1] + '.wav'
                matching_name_count = language.voiceslot_set.filter(name=slot.name).count()
                if matching_name_count == 1:
                    if file_name_count[slot_name] == 0:
                        missing_slots.add(slot.filepath())
                    elif file_name_count[slot_name] == 1:
                        for f in files[lang_name]:
                            if f.filename.split('/')[-1] == slot_name:
                                if f.md5sum == slot.bravo_checksum:
                                    file_struct.add(f.filename, ('found',))
                                else:
                                    file_struct.add(f.filename, ('mismatch',))
                                break
                    else:
                        for f in files[lang_name]:
                            if f.filename.split('/')[-1] == slot_name:
                                file_struct.add(f.filename, ('unexpected-duplicate', ))
                else:
                    md5s = language.voiceslot_set.filter(name=slot.name).values_list('bravo_checksum', flat=True)
                    if md5s.count(md5s[0]) == len(md5s):  # If all md5s are equal
                        what_do_i_call_this = []
                        



        return render(request, 'elpis/verify_results.html', {'missing_slots': missing_slots,
                                                             'file_struct': file_struct.entries})