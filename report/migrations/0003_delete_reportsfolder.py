# Generated by Django 3.1 on 2020-09-06 18:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0002_task_enabled'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ReportsFolder',
        ),
    ]