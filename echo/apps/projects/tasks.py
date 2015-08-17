from collections import namedtuple
from datetime import datetime
from time import sleep

import pysftp
import pytz
from celery.utils.log import get_task_logger

from django.conf import settings
from django.contrib.auth.models import User

from echo import celery_app
from echo.apps.projects.models import Project, UpdateStatus, VoiceSlot
from echo.apps.activity.models import Action


@celery_app.task
def update_file_statuses(project_id, user_id):
    """Background process to update file statuses from Bravo server"""
    try:
        sleep(1.25)  # Stupid fix for a stupid race condition
        project = Project.objects.get(pk=int(project_id))
        status = UpdateStatus.objects.get_or_create(project__pk=project_id)[0]
        user = User.objects.get(pk=int(user_id))
        # Connect to Bravo server and get filenames and md5sums
        with pysftp.Connection(project.bravo_server.address, username=project.bravo_server.account,
                               private_key=settings.PRIVATE_KEY) as sftp:
            result = sftp.execute('find {0}/ -name "*.wav"'.format(project.root_path) +
                                  ' -exec md5sum {} \; -exec stat -c"%Y" {} \;')

        FileStatus = namedtuple('FileStatus', 'md5 path modified')
        file_statuses = []
        try:
            for i in range(0, len(result), 2):
                md5 = result[i].split()[0]
                filename = ' '.join(result[i].split()[1:])
                modified = result[i+1].strip()
                file_statuses.append(FileStatus(md5, filename, modified))
        except IndexError:
            print "Update IndexError Result:"
            print repr(result)

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
                            Action.log(user, Action.AUTO_NEW_SLOT, "Slot ready for testing", slot)
                            break
                        elif slot.status in (VoiceSlot.PASS, VoiceSlot.FAIL):
                            if fs.md5 != slot.bravo_checksum:
                                slot.bravo_checksum = fs.md5
                                slot.bravo_time = datetime.fromtimestamp(float(fs.modified)).replace(tzinfo=pytz.utc)
                                slot.status = VoiceSlot.READY
                                slot.save()
                                Action.log(user, Action.AUTO_NEW_SLOT, "Slot changed and needs retesting", slot)
                                break

        # Find and mark missing voiceslots
        vuid_set = set(slots.values_list('name', flat=True))
        found_set = set([fs.path.split('/')[-1][:-4] for fs in file_statuses])
        missing_set = vuid_set - found_set
        missing_slots = slots.filter(name__in=list(missing_set))
        missing_slots.update(status=VoiceSlot.MISSING)

        # Hack for files found in the wrong language. No es bueno
        stragglers = slots.filter(status=VoiceSlot.NEW)
        stragglers.update(status=VoiceSlot.MISSING)
        for slot in stragglers:
            Action.log(user, Action.AUTO_MISSING_SLOT, "Slot not found in update", slot)  # Missing period to distinguish

        for slot in missing_slots:
            Action.log(user, Action.AUTO_MISSING_SLOT, "Slot not found in update.", slot)
        status.running = False
        status.save()
    except Exception as e:
        logger = get_task_logger(__name__)
        logger.error("Celery task failed")
        logger.error(e)
        logger.error("Project id: {0}".format(project_id))
        sleep(3)
        try:
            project = Project.objects.get(pk=int(project_id))
            logger.error("Waiting would have fixed this.")
        except Exception as e:
            logger.error("Waiting didn't fix it")


