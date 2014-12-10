from collections import namedtuple
from datetime import datetime

import pysftp
import pytz

from django.conf import settings

from echo import celery_app
from echo.apps.projects.models import Project, UpdateStatus, VoiceSlot


@celery_app.task
def update_file_statuses(project_id):
    """Background process to update file statuses from Bravo server"""
    project = Project.objects.get(pk=int(project_id))
    status = UpdateStatus.objects.get_or_create(project__pk=project_id)[0]
    # Connect to Bravo server and get filenames and md5sums
    with pysftp.Connection(project.bravo_server.address, username=project.bravo_server.account,
                           private_key=settings.PRIVATE_KEY) as sftp:
        result = sftp.execute('find {0}/ -name "*.wav"'.format(project.root_path) +
                              ' -exec md5sum {} \; -exec stat -c"%Y" {} \;')

    FileStatus = namedtuple('FileStatus', 'md5 path modified')
    file_statuses = [FileStatus(*result[i].split() + [result[i + 1].strip(), ]) for i in range(0, len(result), 2)]

    # Find and update matching voiceslots
    slots = project.voiceslots()
    for fs in file_statuses:
        if slots.filter(name=fs.path.split('/')[-1][:-4]).exists():
            slot_candidates = slots.filter(name=fs.path.split('/')[-1][:-4])
            for slot in slot_candidates:
                if fs.path == slot.filepath():
                    if slot.status in (VoiceSlot.NEW, VoiceSlot.MISSING, VoiceSlot.READY):
                        slot.bravo_checksum = fs.md5
                        slot.bravo_time = datetime.utcfromtimestamp(float(fs.modified)).replace(tzinfo=pytz.utc)
                        slot.status = VoiceSlot.READY
                        slot.save()
                    elif slot.status in (VoiceSlot.PASS, VoiceSlot.FAIL):
                        if fs.md5 != slot.bravo_checksum:
                            slot.bravo_checksum = fs.md5
                            slot.bravo_time = datetime.fromtimestamp(float(fs.modified)).replace(tzinfo=pytz.utc)
                            slot.status = VoiceSlot.READY
                            slot.save()
                    else:
                        print "No status match"
                else:
                    print "No match between {0} and {1}".format(fs.path, slot.filepath())
        else:
            print "No match for " + fs.path

    # Find and mark missing voiceslots
    vuid_set = set(slots.values_list('name', flat=True))
    found_set = set([fs.path.split('/')[-1][:-4] for fs in file_statuses])
    missing_set = vuid_set - found_set
    missing_slots = slots.filter(name__in=list(missing_set))
    missing_slots.update(status=VoiceSlot.MISSING)

    status.running = False
    status.save()