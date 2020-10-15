from django.core.management.base import BaseCommand
from report import models, utils


class Command(BaseCommand):
    help = 'Reset passwords of all students'

    def handle(self, **options):
        for student in models.User.objects.filter(is_superuser=False).order_by('student_groups'):
            password = utils.gen_pass()
            student.set_password(password)
            student.save()
            self.stdout.write(f'{student.last_name} {student.first_name} {student.username} {password}')
