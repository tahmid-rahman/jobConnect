# Generated by Django 5.1.6 on 2025-02-17 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobseeker", "0004_alter_job_exp_need"),
    ]

    operations = [
        migrations.AlterField(
            model_name="job",
            name="exp_need",
            field=models.IntegerField(default=0),
        ),
    ]
