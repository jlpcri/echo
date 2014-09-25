from datetime import date, datetime
import os
from models import Language, Project, VoiceSlot, VUID
from openpyxl import load_workbook
import echo.settings.base as settings


PAGE_NAME = "page name"
PROMPT_NAME = "prompt name"
PROMPT_TEXT = "prompt text"
LANGUAGE = "language"
STATE_NAME = "state name"
DATE_CHANGED = "date changed"

VUID_HEADER_NAME_SET = {
    PAGE_NAME,
    PROMPT_NAME,
    PROMPT_TEXT,
    LANGUAGE,
    STATE_NAME,
    DATE_CHANGED
}


def fetch_slots_from_server(project, sftp):
    slots = project.voiceslots()
    for s in slots:
        try:
            remote_path = "{0}.wav".format(s.filepath())
            sum = sftp.execute('md5sum {0}'.format(remote_path))[0].strip()
            stat = sftp.execute('stat -c %Y {0}'.format(remote_path))[0].strip()
            if sum.startswith('md5sum:') or stat.startswith('date:'):
                s.status = VoiceSlot.MISSING
                s.history = "Slot missing, {0}\n".format(datetime.now()) + s.history
                s.save()
            else:
                dt = datetime.utcfromtimestamp(float(stat))
                bravo_time = s.bravo_time.replace(tzinfo=None)
                if s.status == VoiceSlot.MISSING:
                    s.status = VoiceSlot.NEW
                    s.bravo_checksum = sum.split(' ')[0]
                    s.bravo_time = dt
                    s.history = "Slot found, {0}\n".format(datetime.now()) + s.history
                    s.save()
                else:
                    if bravo_time < dt and sum.split(' ')[0] != s.bravo_checksum:
                        s.status = VoiceSlot.NEW
                        s.bravo_checksum = sum.split(' ')[0]
                        s.bravo_time = dt
                        s.history = "Slot is new, {0}\n".format(datetime.now()) + s.history
                        s.save()
        except IOError:
            s.status = VoiceSlot.MISSING
            s.history = "Slot missing, {0}\n".format(datetime.now()) + s.history
            s.save()


def make_filename(path, name):
    if path.endswith('/') and name.startswith('/'):
        return "{0}{1}".format(path[:-1], name)
    elif path.endswith('/') or name.startswith('/'):
        return "{0}{1}".format(path, name)
    return "{0}/{1}".format(path, name)


def parse_vuid(vuid):
    wb = load_workbook(vuid.file.path)
    ws = wb.active

    headers = [i.value.lower() for i in ws.rows[0]]
    try:
        prompt_name_i = headers.index(PROMPT_NAME)
        prompt_text_i = headers.index(PROMPT_TEXT)
        language_i = headers.index(LANGUAGE)
        date_changed_i = headers.index(DATE_CHANGED)
    except ValueError:
        return {"valid": False, "message": "Parser error, invalid headers"}

    v = unicode(ws['A2'].value).strip()
    i = v.find('/')
    path = v[i:].strip()

    for w in ws.rows[2:]:
        try:
            if w[language_i].value is not None:
                language = Language.objects.get(project=vuid.project, name=unicode(w[language_i].value).strip().lower())
            else:
                language = Language.objects.get(project=vuid.project, name=unicode('english'))
        except Language.DoesNotExist:
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
            vs.save()
        except VoiceSlot.DoesNotExist:
            vs = VoiceSlot(name=name, path=path, verbiage=verbiage, language=language, vuid_time=vuid_time, vuid=vuid)
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
        if headers.issubset(VUID_HEADER_NAME_SET) and i != -1:
            return True
    return False