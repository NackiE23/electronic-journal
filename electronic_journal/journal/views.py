from django.contrib.auth import get_user_model
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
    template_name = 'journal/create_new_user.html'
    success_url = reverse_lazy('main')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Resister"
        # context['count'] = YourModel.objects.all()
        return context

    def form_valid(self, form):
        form.save()
        # user = form.save()
        # login(self.request, user)
        return redirect('main')
