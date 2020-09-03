import os

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from report import tasks
from report.models import *


def remove_file(instance):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(post_delete, sender=TaskFile, dispatch_uid='delete_task_file')
def auto_delete_task_file_on_delete(sender, instance: TaskFile, **kwargs):
    remove_file(instance)


@receiver(post_delete, sender=ReportFile, dispatch_uid='delete_report_file')
def auto_delete_report_file_on_delete(sender, instance: ReportFile, **kwargs):
    remove_file(instance)


@receiver(post_save, sender=Task, dispatch_uid='generate_task_pdf')
def generate_task_pdf(sender, instance: Task, **kwargs):
    if instance.enabled:
        tasks.generate_task_pdf.delay(instance.id)
