from models import VUID
from openpyxl import load_workbook


VUID_HEADER_NAME_SET = {
    "Page Name",
    "Prompt Name",
    "Prompt Text",
    "Language",
    "State Name",
    "Date Changed"
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


def parse_vuid(vuid):
    wb = load_workbook(vuid.file.url)
    ws = wb.active
    for w in ws.rows:
        print w
        # print ws['A1'].value
        # print ws['B1'].value
        # print ws['C1'].value
        # print ws['D1'].value
        # print ws['E1'].value
        # print ws['F1'].value
    return {"valid": False, "message": "Parser error, unable to upload"}


def upload_vuid(uploaded_file, user, project):
    vuid = VUID(filename=uploaded_file.name, file=uploaded_file, project=project, upload_by=user)
    vuid.save()
    result = verify_vuid(vuid)
    if not result['valid']:
        vuid.delete()
        return result
    # result = parse_vuid(vuid)
    # if not result['valid']:
    #     vuid.delete()
    #     return result
    return result


def verify_vuid(vuid):
    wb = load_workbook(vuid.file.url)
    ws = wb.active
    if len(ws.rows) > 2:
        if verify_vuid_headers(vuid):
            return {"valid": True, "message": "Uploaded file"}
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