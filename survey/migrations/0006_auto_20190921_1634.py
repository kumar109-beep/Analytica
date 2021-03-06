# Generated by Django 2.2.1 on 2019-09-21 16:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0005_auto_20190921_1508'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attribute',
            name='indicator',
        ),
        migrations.RemoveField(
            model_name='indicator',
            name='category',
        ),
        migrations.RemoveField(
            model_name='indicator',
            name='surveygeo',
        ),
        migrations.CreateModel(
            name='Indicatorsurveygeo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Category')),
                ('indicator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Indicator')),
                ('surveygeo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Surveygeo')),
            ],
        ),
        migrations.AddField(
            model_name='attribute',
            name='indicatorsurveygeo',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='survey.Indicatorsurveygeo'),
            preserve_default=False,
        ),
    ]
