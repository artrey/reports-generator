from django.db import models


class File(models.Model):
    pass


class Task(models.Model):
    number = models.IntegerField(verbose_name='Number')
    title = models.CharField(verbose_name='Title', max_length=128)
    description = models.ForeignKey(File, on_delete=models.CASCADE,
                                    related_name='tasks',
                                    verbose_name='description')


class Report(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    info = models.TextField()
    # files = models.Many
