from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.files.base import ContentFile

from report import utils
from report.models import *

logger = get_task_logger(__name__)


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3},
             default_retry_delay=10)
def generate_task_pdf(task_id: int):
    logger.info('Started')
    task = Task.objects.filter(id=task_id).first()

    if not task:
        return

    pdf_content = utils.build_task_pdf(task, base_url=settings.BASE_URL)
    file_data = ContentFile(pdf_content, name=f'{task.name}.pdf')

    if getattr(task, 'task_file', None):
        task.task_file.delete()
    TaskFile.objects.create(task=task, file=file_data)

    logger.info('Successfully finished')


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3},
             default_retry_delay=10)
def generate_report_pdf(report_id: int):
    logger.info('Started')
    report = Report.objects.filter(id=report_id).first()

    if not report:
        return

    pdf_content = utils.build_report_pdf(report, base_url=settings.BASE_URL)
    file_data = ContentFile(
        pdf_content, name=f'{timezone.now().strftime("%Y%m%d%H%M%S")}.pdf'
    )
    ReportFile.objects.create(report=report, file=file_data)

    logger.info('Successfully finished')


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3},
             default_retry_delay=10)
def check_uniqueness(report_id: int):
    logger.info('Started')
    report = Report.objects.filter(id=report_id).first()

    if not report:
        return

    other_reports = list(Report.objects.exclude().filter(
        task_id=report.task_id
    ).exclude(user=report.user).prefetch_related('source_files'))
    if not other_reports:
        return

    ratio, _, other_report = max(map(
        lambda x: (utils.ratio_reports(x, report), x.created_at, x), other_reports
    ))

    ReportsSimilarity.objects.get_or_create(left=other_report, right=report, defaults={
        'ratio': ratio
    })

    logger.info('Successfully finished')
