from django.core.management.base import BaseCommand
from report import models, tasks


class Command(BaseCommand):
    help = 'Check and fill uniqueness of reports'

    def handle(self, **options):
        for report_id in models.Report.objects.values_list('id', flat=True)[:2]:
            tasks.check_uniqueness(report_id)
            self.stdout.write(f'Report {report_id} was processed')
