# Generated by Django 2.2.1 on 2019-09-23 12:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0011_auto_20190923_1146'),
    ]

    operations = [
        migrations.RenameField(
            model_name='geography',
            old_name='g_type',
            new_name='GeographyLevel',
        ),
        migrations.RenameField(
            model_name='surveytogeography',
            old_name='geography',
            new_name='Geography',
        ),
        migrations.RenameField(
            model_name='surveytogeography',
            old_name='survey',
            new_name='Survey',
        ),
    ]
