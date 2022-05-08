import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm, AuthenticationForm

from .models import Lesson, LessonType, TeacherSubject, Subject, EvaluationSystem, Group, Teacher

User = get_user_model()


class LessonCreateForm(forms.ModelForm):
    topic = forms.CharField(label="Тема", widget=forms.TextInput(attrs={'class': 'form-input'}))
    homework = forms.CharField(label="Домашнє завдання", widget=forms.TextInput(attrs={'class': 'form-input'}))
    note = forms.CharField(label="Примітка", widget=forms.TextInput(attrs={'class': 'form-input'}))
    type = forms.ModelChoiceField(label="Тип",
                                  queryset=LessonType.objects.all(),
                                  widget=forms.Select(attrs={'class': 'form-input'}))
    teacher_subject = forms.ModelChoiceField(queryset=TeacherSubject.objects.all(),
                                             widget=forms.HiddenInput())

    class Meta:
        model = Lesson
        fields = ('topic', 'homework', 'note', 'type', 'teacher_subject')

    def __init__(self, *args, **kwargs):
        super(LessonCreateForm, self).__init__(*args, **kwargs)


class LessonUpdateForm(forms.ModelForm):
    topic = forms.CharField(label="Тема", widget=forms.TextInput(attrs={'class': 'form-input'}))
    homework = forms.CharField(label="Домашнє завдання", widget=forms.TextInput(attrs={'class': 'form-input'}))
    note = forms.CharField(label="Примітка", widget=forms.TextInput(attrs={'class': 'form-input'}))
    type = forms.ModelChoiceField(label="Тип",
                                  queryset=LessonType.objects.all(),
                                  widget=forms.Select(attrs={'class': 'form-input'}))

    class Meta:
        model = Lesson
        fields = ('date', 'topic', 'homework', 'note', 'type')


class SubjectCreationForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ('name', 'short_name', 'evaluation_system')


class SubjectFullCreationForm(forms.Form):
    name = forms.CharField(label="Назва")
    short_name = forms.CharField(label="Скорочена назва")
    evaluation_system = forms.ModelChoiceField(label="Система оцінювання", queryset=EvaluationSystem.objects.all())
    group = forms.ModelMultipleChoiceField(label="Для груп(и)", queryset=Group.objects.all())
    amount_of_hours = forms.IntegerField(label="Кількість годин", widget=forms.NumberInput(attrs={'min': 0}))
    teacher = forms.ModelMultipleChoiceField(label="Викладач(і)", queryset=Teacher.objects.all())
    semester = forms.IntegerField(label="Семестр", widget=forms.NumberInput(attrs={'min': 0, 'max': 12}))
    academic_year = forms.IntegerField(label="Навчальний рік",
                                       widget=forms.NumberInput(attrs={'min': 2020, 'max': 3000}))

    def __init__(self, *args, **kwargs):
        super(SubjectFullCreationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-input'


class MyUserChangeForm(forms.ModelForm):
    email = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={'class': 'form-input',
                                                                            'placeholder': 'Вкажіть пошту'}))
    name = forms.CharField(label="Ім'я", widget=forms.TextInput(attrs={'class': 'form-input'}))
    surname = forms.CharField(label="Призвіще", widget=forms.TextInput(attrs={'class': 'form-input'}))
    patronymic = forms.CharField(label="По батькові", widget=forms.TextInput(attrs={'class': 'form-input'}))
    phone_number = forms.CharField(label="Номер телефону", widget=forms.TextInput(attrs={'class': 'form-input'}))
    date_of_birth = forms.DateField(label="Дата народження", initial=datetime.date.today(),
                                    widget=forms.DateInput(attrs={'class': 'form-input',
                                                                  'placeholder': 'дд.мм.рррр або рррр-мм-дд'}))
    about = forms.CharField(label="about", widget=forms.Textarea(attrs={'class': 'form-input'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patronymic'].required = False
        self.fields['phone_number'].required = False
        self.fields['date_of_birth'].required = False
        self.fields['about'].required = False

    class Meta:
        model = User
        fields = ('avatar', 'email', 'name', 'surname', 'patronymic', 'phone_number', 'date_of_birth', 'about')


class UserAdminCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', 'password', 'is_active', 'is_staff', 'is_admin']

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class RegisterUserForm(UserCreationForm):
    CHOICES = (('Student', 'Студент'), ('Teacher', 'Викладач'), )
    choices = forms.ChoiceField(label="Роль", widget=forms.Select(attrs={'class': 'form-input'}),
                                choices=CHOICES)
    name = forms.CharField(label="Ім'я", widget=forms.TextInput(attrs={'class': 'form-input'}))
    surname = forms.CharField(label="Призвіще", widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('choices', 'email', 'name', 'surname', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                _("This account is inactive."),
                code='inactive',
            )
