from models import Language, VoiceSlot, VUID
from openpyxl import load_workbook


PAGE_NAME = "Page Name"
PROMPT_NAME = "Prompt Name"
PROMPT_TEXT = "Prompt Text"
LANGUAGE = "Language"
STATE_NAME = "State Name"
DATE_CHANGED = "Date Changed"


VUID_HEADER_NAME_SET = {
    PAGE_NAME,
    PROMPT_NAME,
    PROMPT_TEXT,
    LANGUAGE,
    STATE_NAME,
    DATE_CHANGED
}


def get_language_context(language):
    return {
        'language': language,
        'slots': language.voiceslots()
    }


def get_master_context(project):
    return {
        'project': project,
        'slots': project.voiceslots()
    }


def get_testslot_context(project, slot):
    return {
        'project': project,
        'slot': slot
    }


def get_vuid_context(vuid):
    wb = load_workbook(vuid.file.url)
    ws = wb.active
    return {
        'vuid': vuid,
        'headers': [i.value for i in ws.rows[0]],
        'path': ws['A2'].value,
        'records': [r for r in ws.rows[2:]]
    }


def make_filename(path, name):
    if path.endswith('/') and name.startswith('/'):
        return "{0}{1}".format(path[:-1], name)
    elif path.endswith('/') or name.startswith('/'):
        return "{0}{1}".format(path, name)
    return "{0}/{1}".format(path, name)


def parse_vuid(vuid):
    wb = load_workbook(vuid.file.url)
    ws = wb.active

    headers = [i.value for i in ws.rows[0]]
    try:
        prompt_name_i = headers.index(PROMPT_NAME)
        prompt_text_i = headers.index(PROMPT_TEXT)
        language_i = headers.index(LANGUAGE)
        date_changed_i = headers.index(DATE_CHANGED)
    except ValueError:
        return {"valid": False, "message": "Parser error, invalid headers"}

    v = ws['A2'].value
    i = v.find('/')
    path = v[i:].strip()

    for w in ws.rows[2:]:
        try:
            language = Language.objects.get(project=vuid.project, name=w[language_i].value.strip())
        except Language.DoesNotExist:
            language = Language(project=vuid.project, name=w[language_i].value.strip())
            language.save()
        except Language.MultipleObjectsReturned:
            return {"valid": False, "message": "Parser error, multiple languages returned"}

        name = w[prompt_name_i].value.strip()
        verbiage = w[prompt_text_i].value.strip()
        vuid_time = w[date_changed_i].value.date()

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
    wb = load_workbook(vuid.file.url)
    ws = wb.active
    if len(ws.rows) > 2:
        if verify_vuid_headers(vuid):
            return {"valid": True, "message": "Uploaded file successfully"}
    elif len(ws.rows) == 2:
        if verify_vuid_headers(vuid):
            return {"valid": False, "message": "No records in file, unable to upload"}
    return {"valid": False, "message": "Invalid file structure, unable to upload"}


def verify_vuid_headers(vuid):
    wb = load_workbook(vuid.file.url)
    ws = wb.active
    if len(ws.rows) >= 2:
        headers = set([i.value for i in ws.rows[0]])
        if headers.issubset(VUID_HEADER_NAME_SET) and ws['A2'].value.startswith("Bravo path:"):
            return True
    return False