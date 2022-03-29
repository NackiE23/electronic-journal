import datetime

from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView

from .models import *
from .forms import *


def main(request):
    user_model = get_user_model()
    all_users = user_model.objects.all()

    return render(request, 'journal/main.html', {'all_users': all_users, 'title': "main"})


@login_required(login_url='login')
def own_profile(request):
    # return render(request, 'journal/profile.html', {'title': 'Profile'})
    return redirect('profile', request.user.pk)


def profile(request, pk):
    cur_user = get_user_model().objects.get(pk=pk)
    guest_condition = str(request.user) == "AnonymousUser" or cur_user != request.user
    context = {
        'title': 'Profile',
        'cur_user': cur_user,
        'guest': guest_condition,
    }

    if cur_user.role == "Teacher":
        teacher = cur_user.teacher

        c_def = {
            'subjects': TeacherSubject.objects.filter(teacher=teacher),
        }
        context = dict(list(context.items()) + list(c_def.items()))

    return render(request, 'journal/profile.html', context=context)


@login_required(login_url='login')
def change_profile(request):
    context = {
        'title': 'Change profile',
        'form': UserChangeForm,
    }

    if request.method == "POST":
        if request.POST['form-action'] == "change_user_text_info":
            user = request.user
            user.email = request.POST['email']
            user.name = request.POST['name']
            user.surname = request.POST['surname']
            user.patronymic = request.POST['patronymic']
            user.phone_number = request.POST['phone_number']
            user.date_of_birth = datetime.datetime.strptime(request.POST['date_of_birth'], '%Y-%m-%d')
            user.about = request.POST['about']
            user.save()
        if request.POST['form-action'] == "change_user_avatar":
            user = request.user
            user.avatar = request.FILES['avatar']
            user.save()

    return render(request, 'journal/change_profile.html', context=context)


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'journal/register.html'
    success_url = reverse_lazy('main')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Register"
        context['groups'] = Group.objects.all()
        return context

    def form_valid(self, form):
        user = form.save()
        if self.request.POST['choices'] == "Teacher":
            working_since = self.request.POST['working_since']
            user.role = self.request.POST['choices']
            user.save()
            Teacher.objects.create(user=user, working_since=working_since)
        elif self.request.POST['choices'] == "Student":
            group = self.request.POST['groups']
            group = Group.objects.get(pk=group)
            subgroup = self.request.POST['subgroup']
            user.role = self.request.POST['choices']
            user.save()
            Student.objects.create(user=user, group=group, subgroup=subgroup)
        login(self.request, user)
        return redirect('own_profile')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'journal/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Login"
        return context

    def get_success_url(self):
        return reverse_lazy('own_profile')


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))
