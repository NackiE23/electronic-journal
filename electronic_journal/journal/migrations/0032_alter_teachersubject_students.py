# Generated by Django 4.0.3 on 2022-04-18 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0031_alter_teacher_specializations_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teachersubject',
            name='students',
            field=models.TextField(max_length=1000, null=True),
        ),
    ]