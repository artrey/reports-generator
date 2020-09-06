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


def get_or_make_google_drive_folder(parent_folder_id: str, folder_name: str) -> str:
    exists = services.drive.files().list(
        fields='files(id)', q=f'name contains "{folder_name}" and "{parent_folder_id}" in parents'
    ).execute()
    if exists['files']:
        return exists['files'][0]['id']

    return services.drive.files().create(body={
        'name': folder_name,
        'parents': [parent_folder_id],
        'mimeType': 'application/vnd.google-apps.folder',
    }).execute().get('id')


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


def update_results(sheet_id: str, report: Report, file_url: str, need_score: bool = True) -> None:
    group = report.user.student_groups.first().title

    get_data = functools.partial(get_sheet_data, sheet_id)

    data = get_data(f'{group}!A4:A50')
    row_idx = next((
        idx for idx, c in enumerate(data['rowData'])
        if c['values'][0].get('formattedValue', '').startswith(report.username)
    ), None)
    if row_idx is None:
        raise RuntimeError(f'Student "{report.username}" not found in Google Sheet')

    row = data['startRow'] + row_idx + 1

    data = get_data(f'{group}!C2:W2')
    task_number = str(report.task.number)

    col_idx = next((
        idx for idx, c in enumerate(data['rowData'][0]['values'])
        if c.get('formattedValue', '').endswith(task_number)
    ), None)
    if col_idx is None:
        raise RuntimeError(f'Task with number "{task_number}" not found in Google Sheet')

    col = data['startColumn'] + col_idx + 1

    if need_score:
        data = get_data(f'{group}!R1C{col}')
        deadline = timezone.make_aware(
            datetime.strptime(
                data['rowData'][0]['values'][0]['formattedValue'].split('-')[-1].strip(), '%d.%m.%Y'
            ) + timedelta(days=1)
        )

        data = get_data(f'{group}!R3C{col + 2}')
        score = int(re.search(r'(\d+)', data['rowData'][0]['values'][0]['formattedValue']).group(0))
        if report.created_at >= deadline:
            offset = report.created_at - deadline
            score -= (offset.days // 7) + 1

        ranges = f'{group}!R{row}C{col}:R{row}C{col + 2}'
        values = [[report.created_at.strftime('%d.%m.%Y'), file_url, score]]

    else:
        ranges = f'{group}!R{row}C{col}:R{row}C{col + 1}'
        values = [[report.created_at.strftime('%d.%m.%Y'), file_url]]

    services.sheets.spreadsheets().values().batchUpdate(spreadsheetId=sheet_id, body={
        'valueInputOption': 'USER_ENTERED',
        'data': [{
            'range': ranges,
            'majorDimension': 'ROWS',
            'values': values,
        }],
        'includeValuesInResponse': False,
    }).execute()
