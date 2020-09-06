from django.core.management.base import BaseCommand
from report import gapi, models


class Command(BaseCommand):
    help = 'Create folders structure in google drive'

    def add_arguments(self, parser):
        parser.add_argument(
            'root_folder_id',
            type=str,
            help='provide root folder id in Google Drive'
        )
        parser.add_argument(
            'groups',
            type=int,
            help='provide groups count'
        )
        parser.add_argument(
            'labs',
            type=int,
            help='provide labs count'
        )
        parser.add_argument(
            '-g', '--group_pattern',
            type=str,
            default='M32{group:02}',
            help='provide group folder name pattern'
        )
        parser.add_argument(
            '-l', '--lab_pattern',
            type=str,
            default='Lab{lab:02}',
            help='provide lab folder name pattern'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            default=False,
            help='clear all previous links in database'
        )

    def handle(self, root_folder_id: str, groups: int, labs: int,
               group_pattern: str, lab_pattern: str, clear: bool, **options):
        if clear:
            self.stdout.write(f'Clearing old links are requested...')
            models.GoogleApiFolder.objects.all().delete()
            self.stdout.write(f'Clearing finished...')

        for group in range(1, groups + 1):
            group_name = group_pattern.format(group=group)
            group_folder_id = gapi.get_or_make_google_drive_folder(
                root_folder_id, group_name
            )
            models.GoogleApiFolder.objects.update_or_create(title=group_name, defaults={
                'api_id': group_folder_id,
            })
            self.stdout.write(f'Folder "{group_name}" now exists and registered in admin')

            for lab in range(1, labs + 1):
                lab_name = lab_pattern.format(lab=lab)
                lab_folder_id = gapi.get_or_make_google_drive_folder(
                    group_folder_id, lab_name
                )
                models.GoogleApiFolder.objects.update_or_create(
                    title=f'{group_name}-{lab_name}',
                    defaults={'api_id': lab_folder_id}
                )
                self.stdout.write(f'Folder "{group_name}/{lab_name}" now exists '
                                  'and registered in admin')
