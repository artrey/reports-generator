import functools
import io
import re
import typing
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build
from report.models import Report


class LazyServices:
    def __init__(self):
        self._credentials = None
        self._drive = None
        self._sheets = None

    def _init_creds(self):
        if not self._credentials:
            self._credentials = service_account.Credentials.from_service_account_file(
                settings.GAPI_SERVICE_ACCOUNT_FILE,
                scopes=[
                    'https://www.googleapis.com/auth/drive',
                    'https://www.googleapis.com/auth/spreadsheets',
                ]
            )

    def _get_drive(self):
        if not self._drive:
            self._init_creds()
            self._drive = build('drive', 'v3', credentials=self._credentials)
        return self._drive

    def _get_sheets(self):
        if not self._sheets:
            self._init_creds()
            self._sheets = build('sheets', 'v4', credentials=self._credentials)
        return self._sheets

    @property
    def drive(self):
        return self._get_drive()

    @property
    def sheets(self):
        return self._get_sheets()


services = LazyServices()


def build_folder_link(object_id: str) -> str:
    return f'https://drive.google.com/drive/folders/{object_id}'


def build_file_link(object_id: str) -> str:
    return f'https://drive.google.com/file/d/{object_id}'


def upload_file(folder_id: str, name: str, file: bytes) -> typing.Optional[str]:
    media = MediaIoBaseUpload(io.BytesIO(file), mimetype='application/pdf', resumable=True)
    exists = services.drive.files().list(
        fields='files(id)', q=f'name contains "{name}" and "{folder_id}" in parents'
    ).execute()
    if exists['files']:
        gfile = services.drive.files().update(
            fileId=exists['files'][0]['id'],
            media_body=media
        ).execute()
    else:
        gfile = services.drive.files().create(
            body={'name': name, 'parents': [folder_id]},
            media_body=media, fields='id'
        ).execute()
    return gfile.get('id')


def get_sheet_data(sheet_id: str, ranges: str) -> dict:
    book = services.sheets.spreadsheets().get(
        spreadsheetId=sheet_id,
        ranges=ranges,
        includeGridData=True
    ).execute()
    sheet = book['sheets'][0]
    return sheet['data'][0]


def update_results(sheet_id: str, report: Report, file_url: str) -> None:
    group = report.user.student_groups.first().title

    get_data = functools.partial(get_sheet_data, sheet_id)

    data = get_data(f'{group}!A4:A50')
    row = data['startRow'] + next((idx for idx, c in enumerate(data['rowData'])
                                   if c['values'][0]['formattedValue'].startswith(report.username))) + 1

    data = get_data(f'{group}!B2:V2')
    task_number = str(report.task.number)
    col = data['startColumn'] + next((idx for idx, c in enumerate(data['rowData'][0]['values'])
                                      if c.get('formattedValue', '').endswith(task_number))) + 1

    data = get_data(f'{group}!R1C{col}')
    deadline = timezone.make_aware(
        datetime.strptime(
            data['rowData'][0]['values'][0]['formattedValue'].split('-')[-1].strip(), '%d.%m.%Y'
        ) + timedelta(days=1)
    )

    data = get_data(f'{group}!R3C{col + 2}')
    score = int(re.search(r'(\d+)', data['rowData'][0]['values'][0]['formattedValue']).group(0))
    if timezone.localtime() >= deadline:
        offset = timezone.localtime() - deadline
        score -= (offset.days // 7) + 1

    services.sheets.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
        'valueInputOption': 'USER_ENTERED',
        'data': [{
            'range': f'{group}!R{row}C{col}:R{row}C{col + 2}',
            'majorDimension': 'ROWS',
            'values': [[report.created_at.strftime('%d.%m.%Y'), file_url, score]],
        }],
        'includeValuesInResponse': False,
    }).execute()
