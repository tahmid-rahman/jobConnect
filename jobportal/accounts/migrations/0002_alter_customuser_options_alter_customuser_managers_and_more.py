# Generated by Django 5.1.6 on 2025-02-16 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="customuser",
            options={},
        ),
        migrations.AlterModelManagers(
            name="customuser",
            managers=[],
        ),
        migrations.RemoveField(
            model_name="customuser",
            name="date_joined",
        ),
        migrations.RemoveField(
            model_name="customuser",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="customuser",
            name="last_name",
        ),
        migrations.AlterField(
            model_name="customuser",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="is_staff",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="role",
            field=models.CharField(
                choices=[("admin", "Admin"), ("user", "User")],
                default="user",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="username",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
