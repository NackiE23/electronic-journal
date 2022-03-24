from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect


def main(request):
    user_model = get_user_model()
    all_users = user_model.objects.all()

    return render(request, 'journal/main.html', {'all_users': all_users, 'title': "main"})


def create_new_user(request):
    if request.method == "POST":
        email = request.POST['email']
        name = request.POST['name']
        surname = request.POST['surname']
        password = request.POST['password']
        working_since = request.POST['working_since']
        user_model = get_user_model()
        user_obj = user_model.objects.create_user(email=email, name=name, surname=surname)
        user_obj.set_password(password)
        user_obj.teacher.working_since = working_since
        user_obj.save()
        return redirect('main')
    else:
        return render(request, 'journal/create_new_user.html', {'title': 'New User'})
