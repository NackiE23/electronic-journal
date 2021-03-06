# Generated by Django 4.0.3 on 2022-05-08 10:02

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0036_replacement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='full_name',
            field=models.CharField(max_length=45, verbose_name='Повна назва'),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='short_name',
            field=models.CharField(max_length=5, verbose_name='Скорочена назва'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='about',
            field=models.TextField(null=True, verbose_name='Про себе'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='user/avatar/', verbose_name='Аватар'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='date_of_birth',
            field=models.DateField(null=True, verbose_name='День народження'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='name',
            field=models.CharField(max_length=15, verbose_name="Ім'я"),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='patronymic',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='По батькові'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='Номер телефону'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(default='Other', max_length=8, verbose_name='Роль'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='surname',
            field=models.CharField(max_length=15, verbose_name='Прізвище'),
        ),
        migrations.AlterField(
            model_name='evaluationsystem',
            name='numerical_form',
            field=models.PositiveIntegerField(verbose_name='Числова форма'),
        ),
        migrations.AlterField(
            model_name='groupsubject',
            name='amount_of_hours',
            field=models.PositiveIntegerField(verbose_name='Кількість годин'),
        ),
        migrations.AlterField(
            model_name='groupsubject',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.group', verbose_name='Група'),
        ),
        migrations.AlterField(
            model_name='groupsubject',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.subject', verbose_name='Предмет'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='Останнє оновлення'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.lessontype', verbose_name='Тип'),
        ),
        migrations.AlterField(
            model_name='lessontype',
            name='name',
            field=models.CharField(max_length=25, verbose_name='Назва'),
        ),
        migrations.AlterField(
            model_name='lessontype',
            name='slug',
            field=models.SlugField(max_length=25, unique=True, verbose_name='Ідентифікатор'),
        ),
        migrations.AlterField(
            model_name='message',
            name='is_check',
            field=models.BooleanField(default=False, verbose_name='Чи перевірино'),
        ),
        migrations.AlterField(
            model_name='message',
            name='text',
            field=models.TextField(verbose_name='Текст'),
        ),
        migrations.AlterField(
            model_name='message',
            name='time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Час'),
        ),
        migrations.AlterField(
            model_name='student',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.group', verbose_name='Група'),
        ),
        migrations.AlterField(
            model_name='studentlesson',
            name='date',
            field=models.DateField(auto_now_add=True, verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='studentlesson',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.lesson', verbose_name='Предмет'),
        ),
        migrations.AlterField(
            model_name='studentlesson',
            name='mark',
            field=models.CharField(max_length=3, null=True, verbose_name='Оцінка'),
        ),
        migrations.AlterField(
            model_name='studentlesson',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.student', verbose_name='Студент'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='evaluation_system',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.evaluationsystem', verbose_name='Система оцінювання'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='slug',
            field=models.SlugField(max_length=45, unique=True, verbose_name='Ідентифікатор'),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='specializations',
            field=models.CharField(max_length=1000, null=True, verbose_name='Спеціалізації'),
        ),
        migrations.AlterField(
            model_name='teachersubject',
            name='students',
            field=models.CharField(max_length=1000, null=True, verbose_name='Студенти'),
        ),
        migrations.AlterField(
            model_name='teachersubject',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='journal.teacher', verbose_name='Викладач'),
        ),
    ]
