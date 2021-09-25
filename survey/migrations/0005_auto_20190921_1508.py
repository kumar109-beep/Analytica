# Generated by Django 2.2.1 on 2019-09-21 15:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0004_auto_20190921_1051'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='survey',
        ),
        migrations.RemoveField(
            model_name='survey',
            name='geography',
        ),
        migrations.AlterField(
            model_name='attribute',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='name',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='survey',
            name='name',
            field=models.CharField(default=2, max_length=255),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Surveygeo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('geography', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Geography')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Survey')),
            ],
        ),
        migrations.AddField(
            model_name='indicator',
            name='surveygeo',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='survey.Surveygeo'),
            preserve_default=False,
        ),
    ]