import json

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Role(models.Model):
    class Meta:
        verbose_name = "Роль у системі"
        verbose_name_plural = "Ролі у системі"

    name = models.CharField(max_length=45, verbose_name="Назва")

    def __str__(self):
        return self.name


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
    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"
        ordering = ['surname', 'name', 'patronymic']

    name = models.CharField(max_length=45, null=False, verbose_name="Ім'я")
    surname = models.CharField(max_length=45, null=False, verbose_name="Прізвище")
    patronymic = models.CharField(max_length=45, blank=True, null=True, verbose_name="По батькові")

    email = models.EmailField(unique=True)  # require
    avatar = models.ImageField(upload_to='user/avatar/', blank=True, null=True, verbose_name="Аватар")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="День народження")
    about = models.TextField(null=True, blank=True, verbose_name="Про себе")

    role = models.ForeignKey("Role", on_delete=models.CASCADE, null=False, verbose_name="Роль у системі")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["name", "surname", "role"]

    objects = CustomUserManager()

    def __str__(self):
        if self.name and self.surname:
            return f'{self.surname} {self.name}'
        return self.email.split('@')[0]

    def get_full_name(self):
        if self.name and self.surname and self.patronymic:
            return f'{self.surname}  {self.name} {self.patronymic}'
        return self.email.split('@')[0]

    def get_short_name(self):
        if self.name and self.surname:
            return f'{self.surname}  {self.name}'
        return self.email.split('@')[0]

    def get_name(self):
        if self.name and self.surname and self.patronymic:
            return f'{self.surname}  {self.name} {self.patronymic}'
        if self.name and self.surname:
            return f'{self.surname}  {self.name}'
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
    class Meta:
        verbose_name = "Викладач"
        verbose_name_plural = "Викладачі"
        ordering = ['user']

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Користувач")

    def __str__(self):
        return str(self.user)


class Specialization(models.Model):
    class Meta:
        verbose_name = "Сцеціалізація"
        verbose_name_plural = "Спеціалізації"

    name = models.CharField(max_length=45, verbose_name="Назва")

    def __str__(self):
        return self.name


class TeacherSpecialization(models.Model):
    class Meta:
        verbose_name = "Спеціалізація викладача"
        verbose_name_plural = "Спеціалізації викладачів"

    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)
    specialization = models.ForeignKey('Specialization', on_delete=models.CASCADE)

    def __str__(self):
        return f'{str(self.teacher)} {str(self.specialization)}'


class Group(models.Model):
    class Meta:
        verbose_name = "Група"
        verbose_name_plural = "Групи"

    name = models.CharField(max_length=45, verbose_name="Назва групи")
    slug = models.SlugField(max_length=45, unique=True, verbose_name="URL")
    teacher = models.OneToOneField('Teacher', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('group', kwargs={'group_slug': self.slug})


class StudyForm(models.Model):
    class Meta:
        verbose_name = "Форма навчання"
        verbose_name_plural = "Форми навчання"

    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Student(models.Model):
    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенти"
        ordering = ['user']

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    study_form = models.ForeignKey("StudyForm", on_delete=models.CASCADE, verbose_name="Форма навчання")
    group = models.ForeignKey("Group", on_delete=models.CASCADE, verbose_name="Група")

    def __str__(self):
        return str(self.user)


class Attendance(models.Model):
    class Meta:
        verbose_name = "Відвідуваність"
        verbose_name_plural = "Відвідуваність"

    full_name = models.CharField(max_length=45, verbose_name="Повна назва")
    short_name = models.CharField(max_length=5, verbose_name="Скорочена назва")

    def __str__(self):
        return self.full_name


class EvaluationSystem(models.Model):
    class Meta:
        verbose_name = "Система оцінювання"
        verbose_name_plural = "Системи оцінювання"

    name = models.CharField(max_length=45, verbose_name="Назва")
    numerical_form = models.PositiveIntegerField(verbose_name="Числова форма")

    def __str__(self):
        return self.name


class Subject(models.Model):
    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предмети"

    name = models.CharField(max_length=45, verbose_name="Назва предмету")
    slug = models.SlugField(max_length=45, unique=True, verbose_name="Ідентифікатор")
    short_name = models.CharField(max_length=33, verbose_name="Скорочена назва предмету")
    evaluation_system = models.ForeignKey("EvaluationSystem", on_delete=models.CASCADE, verbose_name="Система оцінювання")

    def __str__(self):
        return self.name


class GroupSubject(models.Model):
    class Meta:
        verbose_name = "Предмет групи"
        verbose_name_plural = "Предмети груп"

    group = models.ForeignKey('Group', on_delete=models.CASCADE, verbose_name="Група")
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, verbose_name="Предмет")
    amount_of_hours = models.PositiveIntegerField(verbose_name="Кількість годин")

    def __str__(self):
        return f"{self.subject.name} {self.group.name}"


class TeacherSubject(models.Model):
    class Meta:
        verbose_name = "Предмет викладача"
        verbose_name_plural = "Предмети викладачів"

    teacher = models.ForeignKey("Teacher", on_delete=models.CASCADE, verbose_name="Викладач")
    group_subject = models.ForeignKey("GroupSubject", on_delete=models.CASCADE, verbose_name="Предмет")
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
    class Meta:
        verbose_name = "Тип пари"
        verbose_name_plural = "Типи пар"

    name = models.CharField(max_length=25, verbose_name="Назва")
    slug = models.SlugField(max_length=25, unique=True, verbose_name="Ідентифікатор")

    def __str__(self):
        return self.name


class Lesson(models.Model):
    class Meta:
        verbose_name = "Пара"
        verbose_name_plural = "Пари"
        ordering = ['date']

    date = models.DateField(default=timezone.now, verbose_name="Дата")
    last_update = models.DateTimeField(auto_now=True, verbose_name="Останнє оновлення")
    topic = models.CharField(max_length=200, verbose_name="Тема", null=True)
    homework = models.CharField(max_length=200, verbose_name="Домашнє завдання", null=True)
    note = models.CharField(max_length=200, blank=True, verbose_name="Примітка", null=True)
    type = models.ForeignKey('LessonType', on_delete=models.CASCADE, verbose_name="Тип")
    teacher_subject = models.ForeignKey("TeacherSubject", on_delete=models.CASCADE)

    def __str__(self):
        return self.topic

    def is_changeable(self):
        return self.date


class StudentLesson(models.Model):
    class Meta:
        verbose_name = "Пара студента"
        verbose_name_plural = "Пари студентів"
        ordering = ['lesson__date']

    lesson = models.ForeignKey("Lesson", on_delete=models.CASCADE, verbose_name="Предмет")
    student = models.ForeignKey("Student", on_delete=models.CASCADE, verbose_name="Студент")
    mark = models.CharField(max_length=5, null=True, verbose_name="Оцінка")
    date = models.DateField(auto_now_add=True, verbose_name="Дата")
    read_only = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.student} in {self.lesson}: {self.mark}'


class Message(models.Model):
    class Meta:
        verbose_name = "Повідомлення"
        verbose_name_plural = "Повідомлення"

    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="from_user")
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="to_user")
    time = models.DateTimeField(auto_now_add=True, verbose_name="Час")
    text = models.TextField(verbose_name="Текст")
    is_check = models.BooleanField(default=False, verbose_name="Чи перевірино")

    def __str__(self):
        return f'{self.from_user} to {self.to_user}'


class Replacement(models.Model):
    class Meta:
        verbose_name = "Заміна"
        verbose_name_plural = "Заміни"

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Викладач на заміну")
    teacher_subject = models.ForeignKey(TeacherSubject, on_delete=models.CASCADE, verbose_name="Предмет викладача")
    date_from = models.DateField(auto_now_add=True, verbose_name="З")
    date_to = models.DateField(verbose_name="До")

    def __str__(self):
        return f"{self.teacher} {str(self.teacher_subject.group_subject)}"
