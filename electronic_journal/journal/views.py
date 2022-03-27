from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .models import *
from .forms import *


def main(request):
    user_model = get_user_model()
    all_users = user_model.objects.all()

    return render(request, 'journal/main.html', {'all_users': all_users, 'title': "main"})


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'journal/register.html'
    success_url = reverse_lazy('main')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Register"
        return context

    def form_valid(self, form):
        user = form.save()
        if self.request.POST['choices'] == "Teacher":
            ws = self.request.POST['working_since']
            Teacher.objects.create(user=user, working_since=ws)
        elif self.request.POST['choices'] == "Student":
            sb = self.request.POST['subgroup']
            print(sb)
        login(self.request, user)
        return redirect('main')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'journal/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Login"
        return context

    def get_success_url(self):
        return reverse_lazy('main')
