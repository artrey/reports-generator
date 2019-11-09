import io
import typing
from datetime import datetime, timedelta

from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build

from report.models import Report

credentials = service_account.Credentials.from_service_account_file(
    settings.GAPI_SERVICE_ACCOUNT_FILE,
    scopes=[
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets',
    ]
)
drive_service = build('drive', 'v3', credentials=credentials)
sheets_service = build('sheets', 'v4', credentials=credentials)


def build_folder_link(object_id: str) -> str:
    return f'https://drive.google.com/drive/folders/{object_id}'


def build_file_link(object_id: str) -> str:
    return f'https://drive.google.com/file/d/{object_id}'


def upload_file(folder_id: str, name: str, file: bytes) -> typing.Optional[str]:
    media = MediaIoBaseUpload(io.BytesIO(file), mimetype='application/pdf', resumable=True)
    gfile = drive_service.files().create(
        body={'name': name, 'parents': [folder_id]},
        media_body=media, fields='id'
    ).execute()
    return gfile.get('id')


def update_results(sheet_id: str, report: Report, file_url: str) -> None:
    group = report.user.student_groups.first().title

    book = sheets_service.spreadsheets().get(
        spreadsheetId=sheet_id,
        ranges=f'{group}!A4:A50',
        includeGridData=True
    ).execute()

    sheet = book['sheets'][0]
    data = sheet['data'][0]
    row = data['startRow'] + next((idx for idx, c in enumerate(data['rowData'])
                                   if c['values'][0]['formattedValue'].startswith(report.username)))

    book = sheets_service.spreadsheets().get(
        spreadsheetId=sheet_id,
        ranges=f'{group}!B2:V2',
        includeGridData=True
    ).execute()

    sheet = book['sheets'][0]
    data = sheet['data'][0]
    task_number = str(report.task.number)
    col = data['startColumn'] + next((idx for idx, c in enumerate(data['rowData'][0]['values'])
                                      if c.get('formattedValue', '').endswith(task_number)))

    book = sheets_service.spreadsheets().get(
        spreadsheetId=sheet_id,
        ranges=f'{group}!R1C{col + 1}',
        includeGridData=True
    ).execute()
    sheet = book['sheets'][0]
    data = sheet['data'][0]

    deadline = datetime.strptime(data['rowData'][0]['values'][0]['formattedValue'].split('-')[-1].strip(),
                                 '%d.%m.%Y') + timedelta(days=1)
    print(deadline)
