from datetime import datetime
from django.db import transaction
from itertools import izip, takewhile
from models import Language, Project, VoiceSlot, VUID
from openpyxl import load_workbook


PAGE_NAME = "page name"
PROMPT_NAME = "prompt name"
PROMPT_TEXT = "prompt text"
LANGUAGE = "language"
STATE_NAME = "state name"
DATE_CHANGED = "date changed"

VUID_HEADER_NAME_SET = {
    PROMPT_NAME,
    PROMPT_TEXT,
    DATE_CHANGED
}


class FileStatus(object):
    def __init__(self, pathname, msum, mtime):
        self.pathname = pathname
        self.msum = msum
        self.mtime = float(mtime)


def allnamesequal(name):
    return all(n == name[0] for n in name[1:])


def commonprefix(paths, sep='/'):
    bydirectorylevels = zip(*[p.split(sep) for p in paths])
    return sep.join(x[0] for x in takewhile(allnamesequal, bydirectorylevels))

@transaction.atomic
def fetch_slots_from_server(project, sftp):
    """Contains logic to update file statuses"""
    # get shared path of all distinct paths from voiceslot models in project
    path = commonprefix(project.voiceslots().values_list('path', flat=True).distinct())
    try:
        result = sftp.execute('find {0}/ -name "*.wav"'.format(path) + ' -exec md5sum {} \; -exec stat -c"%Y" {} \;')
    except IOError:
        # something in the execute didn't stir the kool-aid
        return {"valid": False, "message": "Error running command on server"}
    if len(result) == 0:
        # means path exists, but no files in path, mark all files as missing
        slots = project.voiceslots()
        for slot in slots:
            slot.status = VoiceSlot.MISSING
            slot.history = "Slot missing, {0}\n".format(datetime.now()) + slot.history
            slot.save()
        return {"valid": False, "message": "All files missing on server, given path \"{0}\"".format(path)}
    elif len(result) == 1 and result[0].startswith('find:'):
        # means error was returned, path does not exist
        return {"valid": False, "message": "Path \"{0}\" does not exist on server".format(path)}
    else:
        if len(result) % 2 == 1:
            # dataset should be 2 lines per record, if odd then something is not right
            return {"valid": False, "message": "Server providing invalid dataset"}
        else:
            # parse result into dictionary using izip
            l = izip(*([iter(result)]*2))
            map = {}
            for i in l:
                msum, pathname = i[0].strip().split('  ')
                mtime = i[1].strip()
                map[pathname] = FileStatus(pathname, msum, mtime)
            # get voiceslots for project and iterate over them
            slots = project.voiceslots()
            for slot in slots:
                # check for slot.filepath() in map.keys()
                if slot.filepath() not in map:
                    # if slot not in map, slot is missing
                    slot.status = VoiceSlot.MISSING
                    slot.history = "Slot missing, {0}\n".format(datetime.now()) + slot.history
                    slot.save()
                else:
                    # else slot in map, run additional tests
                    fs = map.get(slot.filepath())
                    bravo_time = datetime.fromtimestamp(fs.mtime)
                    if slot.bravo_time:
                        bravo_time = slot.bravo_time.replace(tzinfo=None)
                    if slot.status == VoiceSlot.MISSING:
                        slot.status = VoiceSlot.NEW
                        slot.bravo_checksum = fs.msum
                        slot.bravo_time = datetime.fromtimestamp(fs.mtime)
                        slot.history = "Slot found, {0}\n".format(datetime.now()) + slot.history
                        slot.save()
                    elif slot.bravo_time is None or bravo_time < datetime.fromtimestamp(fs.mtime) and slot.bravo_checksum != fs.msum:
                        slot.status = VoiceSlot.NEW
                        slot.bravo_checksum = fs.msum
                        slot.bravo_time = datetime.fromtimestamp(fs.mtime)
                        slot.history = "Slot is new, {0}\n".format(datetime.now()) + slot.history
                        slot.save()
            return {"valid": True, "message": "Files from Bravo Server have been fetched"}


def make_filename(path, name):
    if path.endswith('/') and name.startswith('/'):
        return "{0}{1}".format(path[:-1], name)
    elif path.endswith('/') or name.startswith('/'):
        return "{0}{1}".format(path, name)
    return "{0}/{1}".format(path, name)

@transaction.atomic
def parse_vuid(vuid):
    wb = load_workbook(vuid.file.path)
    ws = wb.active

    headers = [i.value.lower() for i in ws.rows[0]]
    try:
        prompt_name_i = headers.index(PROMPT_NAME)
        prompt_text_i = headers.index(PROMPT_TEXT)
        date_changed_i = headers.index(DATE_CHANGED)
    except ValueError:
        return {"valid": False, "message": "Parser error, invalid headers"}

    no_language = False
    try:
        language_i = headers.index(LANGUAGE)
    except ValueError:
        no_language = True

    v = unicode(ws['A2'].value).strip()
    i = v.find('/')
    path = v[i:].strip()
    slots = []

    for w in ws.rows[2:]:
        try:
            if no_language:
                language = Language.objects.get(project=vuid.project, name=unicode('english'))
            elif w[language_i].value is not None:
                language = Language.objects.get(project=vuid.project, name=unicode(w[language_i].value).strip().lower())
            else:
                language = Language.objects.get(project=vuid.project, name=unicode('english'))
        except Language.DoesNotExist:
            if no_language:
                language = Language(project=vuid.project, name=unicode('english'))
            else:
                language = Language(project=vuid.project, name=unicode(w[language_i].value).strip().lower())
            language.save()
        except Language.MultipleObjectsReturned:
            return {"valid": False, "message": "Parser error, multiple languages returned"}

        name = unicode(w[prompt_name_i].value).strip()
        verbiage = unicode(w[prompt_text_i].value).strip()
        vuid_time = w[date_changed_i].value.date() if w[date_changed_i].value is datetime else None

        try:
            vs = VoiceSlot.objects.get(name=name, path=path, language=language)
            if vuid_time > vs.vuid_time:
                vs.vuid_time = vuid_time.date()
                vs.verbiage = verbiage
                vs.vuid = vuid
            elif vuid_time == vs.vuid_time:
                if vs.verbiage != verbiage:
                    vs.verbiage = verbiage
                    vs.vuid = vuid
            slots.append(vs)
            vs.save()
        except VoiceSlot.DoesNotExist:
            vs = VoiceSlot(name=name, path=path, verbiage=verbiage, language=language, vuid_time=vuid_time, vuid=vuid)
            slots.append(vs)
            vs.save()
        except VoiceSlot.MultipleObjectsReturned:
            return {"valid": False, "message": "Parser error, multiple voice slots returned"}
    return {"valid": True, "message": "Parsed file successfully"}


def upload_vuid(uploaded_file, user, project):
    vuid = VUID(filename=uploaded_file.name, file=uploaded_file, project=project, upload_by=user)
    vuid.save()
    result = verify_vuid(vuid)
    if not result['valid']:
        vuid.delete()
        return result
    result = parse_vuid(vuid)
    if not result['valid']:
        vuid.delete()
        return result
    return {"valid": True, "message": "File uploaded and parsed successfully"}


def verify_vuid(vuid):
    wb = load_workbook(vuid.file.path)
    ws = wb.active
    if len(ws.rows) > 2:
        if verify_vuid_headers(vuid):
            return {"valid": True, "message": "Uploaded file successfully"}
    elif len(ws.rows) == 2:
        if verify_vuid_headers(vuid):
            return {"valid": False, "message": "No records in file, unable to upload"}
    return {"valid": False, "message": "Invalid file structure, unable to upload"}


def verify_vuid_headers(vuid):
    wb = load_workbook(vuid.file.path)
    ws = wb.active
    if len(ws.rows) >= 2:
        headers = set([i.value.lower() for i in ws.rows[0]])
        i = unicode(ws['A2'].value).strip().find('/')
        if VUID_HEADER_NAME_SET.issubset(headers) and i != -1:
            return True
    return False