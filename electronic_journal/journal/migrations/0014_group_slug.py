# Generated by Django 4.0.3 on 2022-03-30 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0013_remove_teacher_working_since'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='slug',
            field=models.SlugField(default='asd', max_length=45, verbose_name='URL'),
            preserve_default=False,
        ),
    ]
