# Generated by Django 5.1.6 on 2025-03-05 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobseeker', '0016_alter_profile_profile_picture_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='phone',
            field=models.IntegerField(blank=True, max_length=15, null=True),
        ),
    ]
