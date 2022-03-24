from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUserManager(BaseUserManager):

    def create_user(self, email, name, surname, password=None):
        custom_user = self.model(email=self.normalize_email(email), name=name, surname=surname)
        custom_user.set_password(password)
        custom_user.save()
        print('custom user manager')
        return custom_user


class CustomUser(AbstractBaseUser):
    # Names
    name = models.CharField(max_length=15, blank=True, null=True)
    surname = models.CharField(max_length=15, blank=True, null=True)
    patronymic = models.CharField(max_length=15, blank=True, null=True)
    # contact
    email = models.EmailField(unique=True)  # require
    phone_number = models.CharField(max_length=16)
    # about
    avatar = models.ImageField(upload_to='user/avatar/', blank=True, null=True)

    objects = CustomUserManager()

    # Main Field for authentication
    USERNAME_FIELD = 'email'
    # When user create must need to fill this field
    REQUIRED_FIELDS = ["name", "surname"]

    def __str__(self):
        return self.name

    def get_short_name(self):
        if self.name and self.surname:
            return f'{self.surname} {self.name}'

    # def get_full_name(self):
    #     if all(self.name, self.surname, self.patronymic):
    #         return f'{self.surname}  {self.name} {self.patronymic}'
    #     return self.email.split('@')[0]


class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    working_since = models.CharField(max_length=4, verbose_name="Почав(ла) працювати з")

    def __str__(self):
        return self.user.get_short_name()
