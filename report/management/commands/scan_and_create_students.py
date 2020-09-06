import functools

from django.conf import settings
from django.core.management.base import BaseCommand
from report import gapi, models


class Command(BaseCommand):
    help = 'Scan students in Google Sheet and create records in database'

    def add_arguments(self, parser):
        parser.add_argument(
            'groups',
            type=int,
            help='provide groups count'
        )
        parser.add_argument(
            '-g', '--group_pattern',
            type=str,
            default='M32{group:02}',
            help='provide group folder name pattern'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            default=False,
            help='clear all previous students and groups in database'
        )

    def handle(self, groups: int, group_pattern: str, clear: bool, **options):
        if clear:
            self.stdout.write(f'Clearing old students and groups are requested...')
            models.Group.objects.all().delete()
            models.User.objects.filter(username__startswith='student').delete()
            self.stdout.write(f'Clearing finished...')

        get_data = functools.partial(gapi.get_sheet_data, settings.GAPI_RESULT_SHEET)

        for group_number in range(1, groups + 1):
            group_name = group_pattern.format(group=group_number)

            try:
                self.stdout.write(f'Creating or getting group "{group_name}"...')
                group, _ = models.Group.objects.update_or_create(title=group_name, defaults={
                    'folder': models.GoogleApiFolder.objects.filter(title=group_name).first()
                })

                self.stdout.write(f'Start scanning group "{group_name}"...')
                data = get_data(f'{group_name}!A4:B50')

                students = []
                for row_data in data['rowData']:
                    name, login = (
                        val.get('formattedValue') for val in row_data['values']
                    )
                    if not name:
                        break

                    last_name, first_name, *_ = name.split()
                    student = models.User.objects.filter(username=login).first()
                    if not student:
                        student = models.User.objects.create_user(
                            login, password=login, first_name=first_name, last_name=last_name
                        )
                    students.append(student.id)

                group.users.set(students)

                self.stdout.write(f'Finished scanning group "{group_name}"')

            except Exception as ex:
                self.stderr.write(str(ex))
