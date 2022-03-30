import datetime

from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic
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
def messages(request):
    context = {
        'title': 'Messages',
        'messages': Message.objects.filter(to_user=request.user),
    }
    return render(request, 'journal/messages.html', context=context)


def group(request, group_slug):
    group_obj = Group.objects.get(slug=group_slug)
    context = {
        'curator': group_obj.teacher,
        'members': Student.objects.filter(group=group_obj),
    }
    return render(request, 'journal/group.html', context=context)


class UserEditView(LoginRequiredMixin, generic.UpdateView):
    login_url = reverse_lazy('login')

    form_class = MyUserChangeForm
    template_name = 'journal/edit_profile.html'
    success_url = reverse_lazy('own_profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edit Profile"
        return context

    def get_object(self):
        return self.request.user


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
            user.role = self.request.POST['choices']
            user.save()
            Teacher.objects.create(user=user)
        elif self.request.POST['choices'] == "Student":
            group = self.request.POST['groups']
            group = Group.objects.get(pk=group)
            subgroup = self.request.POST['subgroup']
            user.role = self.request.POST['choices']
            user.save()
            Student.objects.create(user=user, group=group, subgroup=subgroup)
        login(self.request, user)
        return redirect('own_profile')


class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'journal/change_password.html'
    success_url = reverse_lazy('own_profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Change password form"
        return context


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
