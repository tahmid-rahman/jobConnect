# Generated by Django 5.1.6 on 2025-03-07 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employer', '0010_jobapplication_id_scheduled'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobapplication',
            name='id_scheduled',
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='is_scheduled',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
