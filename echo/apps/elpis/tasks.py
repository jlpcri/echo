from collections import Counter

from django.shortcuts import render_to_response

from echo.apps.elpis.utils.compatibility import normalize_language
from echo.apps.elpis.utils.directory_tree import DirectoryTreeWithPayload
from echo.apps.projects.models import Project, Language

from echo import celery_app


@celery_app.task
def verify_file_transfer(project_id, apps):
    project = Project.objects.get(pk=int(project_id))
    language_list = Language.objects.filter(project=project)
    files = project.preprod_server.get_wavs_from_apps(project.preprod_client_id, apps)
    missing_slots = set()
    file_struct = DirectoryTreeWithPayload('/usr/local/tuvox/public/Projects/', str)

    for language in language_list:
        lang_name = normalize_language(language.name, files.keys())
        if not lang_name:
            return {'missing_slots': (language.name + "not found on server", )}

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
                if md5s.count(md5s[0]) == len(md5s):  # If all md5s in VoiceSlots are equal
                    same_named_files = []
                    for f in files[lang_name]:
                        if f.filename.split('/')[-1] == slot_name:
                            same_named_files.append(f)
                    if len(set([f.md5sum for f in same_named_files])) == 1:  # If all md5s in files are equal
                        if len(same_named_files) == matching_name_count:
                            for f in same_named_files:
                                file_struct.add(f.filename, ('found', ))
                        elif len(same_named_files) > matching_name_count:
                            for f in same_named_files:
                                file_struct.add(f.filename, ('unexpected-duplicate', ))
                        else:
                            for f in same_named_files:
                                file_struct.add(f.filename, ('insufficient-copies', ))
                            missing_slots.add(slot.filepath())
                    else:  # All md5s in VoiceSlots match, but not all md5s in files match
                        for f in same_named_files:
                            if f.md5sum == md5s[0]:
                                file_struct.add(f.filename, ('found', ))
                            else:
                                file_struct.add(f.filename, ('mismatch', ))
                else:  # VoiceSlots with same name have different md5
                    same_named_files = []
                    for f in files[lang_name]:
                        if f.filename.split('/')[-1] == slot_name:
                            if file_struct[f.filename] == 'untracked':
                                same_named_files.append(f)
                    for f in same_named_files:
                        if f.md5sum == slot.bravo_checksum:
                            file_struct.add(f.filename, ('found', ))
                        else:
                            for f in same_named_files:
                                file_struct.add(f.filename, ('insufficient-copies', ))
                            for matching_slot in language.voiceslot_set.filter(name=slot.name):
                                missing_slots.add(matching_slot.filepath())
    return render_to_response('elpis/verify_results.html', {'missing_slots': missing_slots,
                                                            'file_struct': file_struct.entries})