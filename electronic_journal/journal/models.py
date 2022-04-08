import json

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.urls import reverse
from django.utils import timezone


class CustomUserManager(BaseUserManager):

    def create_user(self, email, name, surname, password=None, is_staff=False, is_admin=False, is_active=True):
        custom_user = self.model(email=self.normalize_email(email), name=name, surname=surname)
        custom_user.set_password(password)
        custom_user.is_staff = is_staff
        custom_user.is_admin = is_admin
        custom_user.is_active = is_active
        custom_user.save()
        return custom_user

    def create_staffuser(self, email, name, surname, password=None):
        user = self.create_user(
            email,
            name=name,
            surname=surname,
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, email, name, surname, password=None):
        user = self.create_user(
            email,
            name=name,
            surname=surname,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user


class CustomUser(AbstractBaseUser):
    name = models.CharField(max_length=15, null=False)
    surname = models.CharField(max_length=15, null=False)
    patronymic = models.CharField(max_length=15, blank=True, null=True)

    email = models.EmailField(unique=True)  # require
    phone_number = models.CharField(max_length=16, blank=True, null=True)
    avatar = models.ImageField(upload_to='user/avatar/', blank=True, null=True)
    date_of_birth = models.DateField(null=True)
    about = models.TextField(null=True)

    role = models.CharField(max_length=8, null=False, default="Other")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["name", "surname"]

    objects = CustomUserManager()

    def __str__(self):
        if self.name and self.surname:
            return f'{self.surname} {self.name}'
        return self.email.split('@')[0]

    def get_full_name(self):
        if self.name and self.surname and self.patronymic:
            return f'{self.surname}  {self.name} {self.patronymic}'
        return self.email.split('@')[0]

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_absolute_url(self):
        return reverse('profile', kwargs={'pk': self.pk})


class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


class Group(models.Model):
    name = models.CharField(max_length=45, verbose_name="Назва групи")
    slug = models.SlugField(max_length=45, unique=True, verbose_name="URL")
    teacher = models.OneToOneField('Teacher', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('group', kwargs={'group_slug': self.slug})


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey("Group", on_delete=models.CASCADE)

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
    slug = models.SlugField(max_length=45, unique=True, verbose_name="identificator")
    short_name = models.CharField(max_length=33, verbose_name="Скорочена назва предмету")
    evaluation_system = models.ForeignKey("EvaluationSystem", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class GroupSubject(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    amount_of_hours = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.subject.name} {self.group.name}"


class TeacherSubject(models.Model):
    teacher = models.ForeignKey("Teacher", on_delete=models.CASCADE)
    group_subject = models.ForeignKey("GroupSubject", on_delete=models.CASCADE)
    semester = models.PositiveIntegerField(verbose_name="Семестр")
    academic_year = models.CharField(max_length=4, verbose_name="Навчальний рік")
    students = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.teacher} - {self.group_subject}"

    def set_students(self, students):
        self.students = json.dumps(students)

    def get_students(self):
        return json.loads(self.students)


class LessonType(models.Model):
    name = models.CharField(max_length=25)
    slug = models.SlugField(max_length=25, unique=True, verbose_name="identificator")

    def __str__(self):
        return self.name


class Lesson(models.Model):
    date = models.DateField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    topic = models.CharField(max_length=200, verbose_name="Тема")
    homework = models.CharField(max_length=200, verbose_name="Домашнє завдання")
    note = models.CharField(max_length=200, verbose_name="Примітка")
    type = models.ForeignKey('LessonType', on_delete=models.CASCADE)
    teacher_subject = models.ForeignKey("TeacherSubject", on_delete=models.CASCADE)

    def __str__(self):
        return self.topic

    def is_changeable(self):
        return timezone.now() - self.date


class StudentLesson(models.Model):
    lesson = models.ForeignKey("Lesson", on_delete=models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    mark = models.CharField(max_length=3, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.student)


class Message(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="from_user")
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="to_user")
    time = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    is_check = models.BooleanField(default=False)
