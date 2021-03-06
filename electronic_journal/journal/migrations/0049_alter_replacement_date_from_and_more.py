# Generated by Django 4.0.3 on 2022-06-06 18:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0048_rename_roles_customuser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replacement',
            name='date_from',
            field=models.DateField(auto_now_add=True, verbose_name='З'),
        ),
        migrations.AlterField(
            model_name='replacement',
            name='date_to',
            field=models.DateField(verbose_name='До'),
        ),
        migrations.AlterField(
            model_name='replacement',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.teacher', verbose_name='Викладач на заміну'),
        ),
        migrations.AlterField(
            model_name='replacement',
            name='teacher_subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.teachersubject', verbose_name='Предмет викладача'),
        ),
    ]
