from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build


# credentials = service_account.Credentials.from_service_account_file(
#     settings.GAPI_SERVICE_ACCOUNT_FILE,
#     scopes=['https://www.googleapis.com/auth/drive']
# )
# service = build('drive', 'v3', credentials=credentials)


def build_folder_link(object_id: str) -> str:
    return f'https://drive.google.com/drive/folders/{object_id}'


def build_file_link(object_id: str) -> str:
    return f'https://drive.google.com/file/d/{object_id}'


# results = service.files().list(pageSize=10,
#                                fields="nextPageToken, files(id, name, mimeType)",
#                                q="'1FIiT3WKfvqTNviGPwNzJweA6VOeNvE0a' in parents").execute()
# for r in results['files']:
#     print(build_file_link(r['id']))
