# Generated by Django 4.0.3 on 2022-03-29 14:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0012_customuser_about'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='working_since',
        ),
    ]