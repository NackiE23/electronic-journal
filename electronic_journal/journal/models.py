from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):

    def create_user(self, email, name, surname, password=None):
        custom_user = self.model(email=self.normalize_email(email), name=name, surname=surname)
        custom_user.set_password(password)
        custom_user.save()
        print('custom user manager')
        return custom_user


class CustomUser(AbstractBaseUser):
    name = models.CharField(max_length=15, null=False)
    surname = models.CharField(max_length=15, null=False)
    patronymic = models.CharField(max_length=15, blank=True, null=True)

    email = models.EmailField(unique=True)  # require
    phone_number = models.CharField(max_length=16, blank=True, null=True)
    avatar = models.ImageField(upload_to='user/avatar/', blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["name", "surname"]

    def __str__(self):
        if self.name and self.surname:
            return f'{self.surname} {self.name}'
        return self.email.split('@')[0]

    def get_full_name(self):
        if self.name and self.surname and self.patronymic:
            return f'{self.surname}  {self.name} {self.patronymic}'
        return self.email.split('@')[0]


class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    working_since = models.CharField(max_length=4, verbose_name="Почав(ла) працювати з")

    def __str__(self):
        return str(self.user)


class Group(models.Model):
    name = models.CharField(max_length=45, verbose_name="Назва групи")
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey("Group", on_delete=models.CASCADE)
    subgroup = models.CharField(max_length=2)

    def __str__(self):
        return str(self.user)


class Attendance(models.Model):
    full_name = models.CharField(max_length=45)
    short_name = models.CharField(max_length=5)

    def __str__(self):
        return self.full_name


class EvaluationSystem(models.Model):
    name = models.CharField(max_length=45, verbose_name="Система оцінювання")
    numerical_form = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=45, verbose_name="Назва предмету")
    short_name = models.CharField(max_length=33, verbose_name="Скорочена назва предмету")
    evaluation_system = models.ForeignKey("EvaluationSystem", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class GroupSubject(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    amount_of_hours = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.subject.name} в групі {self.group.name}"


class TeacherSubject(models.Model):
    teacher = models.ForeignKey("Teacher", on_delete=models.CASCADE)
    group_subject = models.ForeignKey("GroupSubject", on_delete=models.CASCADE)
    subgroup = models.CharField(max_length=10, verbose_name="Підгрупа")
    semester = models.PositiveIntegerField(verbose_name="Семестр")
    academic_year = models.CharField(max_length=4, verbose_name="Навчальний рік")

    def __str__(self):
        return f"{self.teacher} - {self.group_subject}"


class Lesson(models.Model):
    date = models.DateField(default=timezone.now)
    topic = models.CharField(max_length=200, verbose_name="Тема")
    homework = models.CharField(max_length=200, verbose_name="Домашнє завдання")
    note = models.CharField(max_length=200, verbose_name="Примітка")
    teacher_subject = models.ForeignKey("TeacherSubject", on_delete=models.CASCADE)

    def __str__(self):
        return self.topic


class StudentGrade(models.Model):
    lesson = models.ForeignKey("Lesson", on_delete=models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    mark = models.PositiveIntegerField()
    attendance = models.ForeignKey("Attendance", on_delete=models.CASCADE)

    def __str__(self):
        return self.student
