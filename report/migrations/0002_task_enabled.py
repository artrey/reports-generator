# Generated by Django 3.1.1 on 2020-09-03 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='enabled',
            field=models.BooleanField(default=True, verbose_name='Enabled'),
        ),
    ]
