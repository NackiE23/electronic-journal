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
    context = {
        'title': 'Profile',
        'cur_user': get_user_model().objects.get(pk=pk),
        'pk': pk,
    }
    return render(request, 'journal/profile.html', context=context)


@login_required(login_url='login')
def change_profile(request):
    context = {
        'title': 'Change profile',
    }
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
