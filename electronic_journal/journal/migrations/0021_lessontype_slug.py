# Generated by Django 4.0.3 on 2022-04-01 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0020_alter_lesson_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessontype',
            name='slug',
            field=models.SlugField(default='para', max_length=25, unique=True, verbose_name='identificator'),
            preserve_default=False,
        ),
    ]
