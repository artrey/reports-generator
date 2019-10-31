from django.contrib.auth.models import User
from django.db import models


class Group(models.Model):
    title = models.CharField(verbose_name='Title', max_length=32)
    upload_link = models.CharField(verbose_name='Upload link', max_length=256)
    users = models.ManyToManyField(User, related_name='student_groups',
                                   verbose_name='Users')


class File(models.Model):
    path = models.CharField(verbose_name='Path to file', max_length=256)


class Task(models.Model):
    number = models.IntegerField(verbose_name='Number')
    title = models.CharField(verbose_name='Title', max_length=128)
    description = models.ForeignKey(File, on_delete=models.CASCADE,
                                    related_name='tasks',
                                    verbose_name='Description')


class Report(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    solution_text = models.TextField(verbose_name='Solution text')
    files = models.ManyToManyField(File, related_name='reports',
                                   verbose_name='Files')
    created_at = models.DateTimeField(verbose_name='Created at', auto_now_add=True)
    approved_at = models.DateTimeField(verbose_name='Approved at', null=True, blank=True)
    rejected_at = models.DateTimeField(verbose_name='Rejected at', null=True, blank=True)
    comment = models.TextField(verbose_name='Comment', null=True, blank=True)
