import io
import typing

from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build

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


def update_results(sheet_id: str, sheet_tab: str, bio: str, task_number: int, file_url: str) -> None:
    r = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    print(r)
