# Generated by Django 5.1.6 on 2025-03-05 19:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employer', '0007_jobapplication'),
        ('jobseeker', '0018_alter_contact_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobapplication',
            name='applicant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobseeker.profile'),
        ),
    ]
