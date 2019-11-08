from collections import OrderedDict

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class GoogleApiFolder(models.Model):
    title = models.CharField(verbose_name='Title', max_length=64)
    api_id = models.CharField(verbose_name='Google drive folder ID', max_length=128)

    def __str__(self) -> str:
        return self.title


class Group(models.Model):
    title = models.CharField(verbose_name='Title', max_length=32, db_index=True)
    folder = models.ForeignKey(
        GoogleApiFolder, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Google drive folder with group data'
    )
    users = models.ManyToManyField(User, related_name='student_groups',
                                   verbose_name='Users', blank=True)

    @property
    def users_count(self) -> int:
        return self.users.count()

    def __str__(self) -> str:
        return self.title


class Task(models.Model):
    number = models.IntegerField(verbose_name='Number')
    title = models.CharField(verbose_name='Title', max_length=128)
    description = models.TextField(verbose_name='Description')

    def get_absolute_url(self) -> str:
        return reverse('task', args=(self.id,))

    def __str__(self) -> str:
        return f'{self.number}. {self.title}'


class ReportsFolder(models.Model):
    folder = models.ForeignKey(
        GoogleApiFolder, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Google drive folder for storing reports'
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE,
        verbose_name='Group', related_name='reports_folders'
    )
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE,
        verbose_name='Task', related_name='reports_folders'
    )


class ApprovedReportManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(approved_at__isnull=False)


class RejectedReportManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(rejected_at__isnull=False)


class VerifyingReportManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(approved_at__isnull=True,
                                             rejected_at__isnull=True)


class Report(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='User')
    solution_text = models.TextField(verbose_name='Solution text')
    created_at = models.DateTimeField(verbose_name='Created at', auto_now_add=True)
    approved_at = models.DateTimeField(verbose_name='Approved at',
                                       null=True, blank=True, db_index=True)
    rejected_at = models.DateTimeField(verbose_name='Rejected at',
                                       null=True, blank=True, db_index=True)
    comment = models.TextField(verbose_name='Comment', null=True, blank=True)

    objects = models.Manager()
    approved_objects = ApprovedReportManager()
    rejected_objects = RejectedReportManager()
    verifying_objects = VerifyingReportManager()

    @property
    def status(self) -> str:
        if self.approved_at:
            return 'approved'
        elif self.rejected_at:
            return 'rejected'
        return 'verifying'

    @staticmethod
    def statuses() -> OrderedDict:
        return OrderedDict({
            'approved': Report.approved_objects,
            'rejected': Report.rejected_objects,
            'verifying': Report.verifying_objects,
        })

    class Meta:
        ordering = '-created_at',

    @property
    def username(self) -> str:
        return f'{self.user.last_name} {self.user.first_name}'

    def __str__(self) -> str:
        return f'{self.task} | {self.username}'


def report_path(file: 'File', filename: str) -> str:
    return f'sources/{file.report.username}/{filename}'


class File(models.Model):
    file = models.FileField(verbose_name='Source file', upload_to=report_path)
    report = models.ForeignKey(Report, on_delete=models.CASCADE,
                               related_name='files', verbose_name='Report')

    def __str__(self) -> str:
        return f'{self.file.path} | {self.report}'
