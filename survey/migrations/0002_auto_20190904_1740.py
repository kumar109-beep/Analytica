# Generated by Django 2.2.1 on 2019-09-04 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geographylevel',
            name='name',
            field=models.CharField(max_length=25, unique=True),
        ),
    ]
