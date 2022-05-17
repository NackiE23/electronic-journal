# Generated by Django 4.0.3 on 2022-05-17 15:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0040_studyform_alter_teachersubject_group_subject'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='study_form',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='journal.studyform', verbose_name='Форма навчання'),
            preserve_default=False,
        ),
    ]