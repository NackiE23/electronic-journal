# Generated by Django 4.0.3 on 2022-06-06 17:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0046_customuser_roles'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='role',
        ),
    ]
