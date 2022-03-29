from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm, AuthenticationForm

# from .models import *

User = get_user_model()


class UserChangeForm(forms.ModelForm):
    email = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={'class': 'form-input',
                                                                            'placeholder': 'Вкажіть пошту'}))
    name = forms.CharField(label="Ім'я", widget=forms.TextInput(attrs={'class': 'form-input'}))
    surname = forms.CharField(label="Призвіще", widget=forms.TextInput(attrs={'class': 'form-input'}))
    patronymic = forms.CharField(label="По батькові", widget=forms.TextInput(attrs={'class': 'form-input'}))
    phone_number = forms.CharField(label="phone_number", widget=forms.TextInput(attrs={'class': 'form-input'}))
    date_of_birth = forms.DateField(label="date_of_birth", widget=forms.DateInput(attrs={'class': 'form-input'}))
    about = forms.CharField(label="about", widget=forms.Textarea(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('email', 'name', 'surname', 'patronymic', 'phone_number', 'date_of_birth', 'about')


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
