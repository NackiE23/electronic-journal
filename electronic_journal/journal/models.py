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
    name = models.CharField(max_length=15, null=False, verbose_name="Ім'я")
    surname = models.CharField(max_length=15, null=False, verbose_name="Прізвище")
    patronymic = models.CharField(max_length=15, blank=True, null=True, verbose_name="По батькові")

    email = models.EmailField(unique=True)  # require
    phone_number = models.CharField(max_length=16, blank=True, null=True, verbose_name="Номер телефону")
    avatar = models.ImageField(upload_to='user/avatar/', blank=True, null=True, verbose_name="Аватар")
    date_of_birth = models.DateField(null=True, verbose_name="День народження")
    about = models.TextField(null=True, verbose_name="Про себе")

    role = models.CharField(max_length=8, null=False, default="Other", verbose_name="Роль")

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

    def get_group_slug(self):
        if self.role == "Teacher":
            return self.teacher.group.slug
        elif self.role == "Student":
            return self.student.group.slug
        return None

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_absolute_url(self):
        return reverse('profile', kwargs={'pk': self.pk})


class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specializations = models.CharField(max_length=1000, null=True, verbose_name="Спеціалізації")

    def __str__(self):
        return str(self.user)

    def set_specializations(self, students: list) -> None:
        if type(students) is list:
            self.specializations = json.dumps(students)
        else:
            raise ValueError(f'Received value must be a list. But got {type(students)}')

    def get_specializations(self) -> list:
        return json.loads(self.specializations)


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
    group = models.ForeignKey("Group", on_delete=models.CASCADE, verbose_name="Група")

    def __str__(self):
        return str(self.user)


class Attendance(models.Model):
    full_name = models.CharField(max_length=45, verbose_name="Повна назва")
    short_name = models.CharField(max_length=5, verbose_name="Скорочена назва")

    def __str__(self):
        return self.full_name


class EvaluationSystem(models.Model):
    name = models.CharField(max_length=45, verbose_name="Система оцінювання")
    numerical_form = models.PositiveIntegerField(verbose_name="Числова форма")

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=45, verbose_name="Назва предмету")
    slug = models.SlugField(max_length=45, unique=True, verbose_name="Ідентифікатор")
    short_name = models.CharField(max_length=33, verbose_name="Скорочена назва предмету")
    evaluation_system = models.ForeignKey("EvaluationSystem", on_delete=models.CASCADE, verbose_name="Система оцінювання")

    def __str__(self):
        return self.name


class GroupSubject(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE, verbose_name="Група")
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, verbose_name="Предмет")
    amount_of_hours = models.PositiveIntegerField(verbose_name="Кількість годин")

    def __str__(self):
        return f"{self.subject.name} {self.group.name}"


class TeacherSubject(models.Model):
    teacher = models.ForeignKey("Teacher", on_delete=models.CASCADE, verbose_name="Викладач")
    group_subject = models.ForeignKey("GroupSubject", on_delete=models.CASCADE)
    semester = models.PositiveIntegerField(verbose_name="Семестр")
    academic_year = models.CharField(max_length=4, verbose_name="Навчальний рік")
    students = models.CharField(max_length=1000, null=True, verbose_name="Студенти")

    def __str__(self):
        return f"{self.teacher} - {self.group_subject}"

    def set_students(self, students: list) -> None:
        self.students = json.dumps(students)

    def get_students(self) -> list:
        return json.loads(self.students)

    def if_exist(self) -> bool:
        if self.students is not None:
            return True
        return False

    def check_student(self, student_pk) -> bool:
        if self.if_exist():
            if str(student_pk) in self.get_students():
                return True
            return False
        return False


class LessonType(models.Model):
    name = models.CharField(max_length=25, verbose_name="Назва")
    slug = models.SlugField(max_length=25, unique=True, verbose_name="Ідентифікатор")

    def __str__(self):
        return self.name


class Lesson(models.Model):
    date = models.DateField(auto_now_add=True, verbose_name="Дата")
    last_update = models.DateTimeField(auto_now=True, verbose_name="Останнє оновлення")
    topic = models.CharField(max_length=200, verbose_name="Тема", null=True)
    homework = models.CharField(max_length=200, verbose_name="Домашнє завдання", null=True)
    note = models.CharField(max_length=200, verbose_name="Примітка", null=True)
    type = models.ForeignKey('LessonType', on_delete=models.CASCADE, verbose_name="Тип")
    teacher_subject = models.ForeignKey("TeacherSubject", on_delete=models.CASCADE)

    def __str__(self):
        return self.topic

    def is_changeable(self):
        return self.date


class StudentLesson(models.Model):
    lesson = models.ForeignKey("Lesson", on_delete=models.CASCADE, verbose_name="Предмет")
    student = models.ForeignKey("Student", on_delete=models.CASCADE, verbose_name="Студент")
    mark = models.CharField(max_length=3, null=True, verbose_name="Оцінка")
    date = models.DateField(auto_now_add=True, verbose_name="Дата")

    def __str__(self):
        return f'{self.student} in {self.lesson}: {self.mark}'


class Message(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="from_user")
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="to_user")
    time = models.DateTimeField(auto_now_add=True, verbose_name="Час")
    text = models.TextField(verbose_name="Текст")
    is_check = models.BooleanField(default=False, verbose_name="Чи перевірино")


class Replacement(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    teacher_subject = models.ForeignKey(TeacherSubject, on_delete=models.CASCADE)
    date_from = models.DateField(auto_now_add=True)
    date_to = models.DateField()

    def __str__(self):
        return str(self.teacher_subject)
