# Generated by Django 5.1.6 on 2025-03-08 09:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employer', '0011_remove_jobapplication_id_scheduled_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interview',
            name='candidate',
        ),
        migrations.RemoveField(
            model_name='interview',
            name='company',
        ),
        migrations.AddField(
            model_name='interview',
            name='appication',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='employer.jobapplication'),
            preserve_default=False,
        ),
    ]
