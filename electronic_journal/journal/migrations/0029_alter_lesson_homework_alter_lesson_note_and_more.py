# Generated by Django 4.0.3 on 2022-04-08 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0028_studentlesson_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='homework',
            field=models.CharField(max_length=200, null=True, verbose_name='Домашнє завдання'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='note',
            field=models.CharField(max_length=200, null=True, verbose_name='Примітка'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='topic',
            field=models.CharField(max_length=200, null=True, verbose_name='Тема'),
        ),
    ]
