import datetime
from time import time

from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpResponseRedirect, JsonResponse
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
        'messages': Message.objects.order_by('-time'),
    }

    if request.method == "POST":
        pk = request.POST['pk-message']
        message_obj = Message.objects.get(pk=pk)
        if request.POST['button'] == "delete_button":
            message_obj.delete()
        elif request.POST['button'] == "check_button":
            message_obj.is_check = True
            message_obj.save()

    return render(request, 'journal/messages.html', context=context)


def group(request, group_slug):
    group_obj = Group.objects.get(slug=group_slug)
    context = {
        'curator': group_obj.teacher,
        'members': Student.objects.filter(group=group_obj),
    }
    return render(request, 'journal/group.html', context=context)


def journal_list(request, group_slug="1-mp-9"):
    group_obj = Group.objects.get(slug=group_slug)
    context = {
        'title': 'Journal list',
        'group_subjects': GroupSubject.objects.filter(group=group_obj),
    }
    return render(request, 'journal/journals.html', context=context)


def journal(request, group_slug="1-mp-9", subject_slug="mathematic"):
    group_obj = Group.objects.get(slug=group_slug)
    subject_obj = Subject.objects.get(slug=subject_slug)
    group_subject_obj = GroupSubject.objects.get(group=group_obj, subject=subject_obj)
    teacher_subject_obj = TeacherSubject.objects.get(group_subject=group_subject_obj)

    students_objs = Student.objects.filter(group=group_obj).order_by('-user')
    condition = (len(teacher_subject_obj.get_students()) != 0)
    students = students_objs.filter(pk__in=teacher_subject_obj.get_students()) if condition \
        else None
    other_students = students_objs.exclude(pk__in=teacher_subject_obj.get_students()) if condition \
        else students_objs

    lesson_objs = Lesson.objects.filter(teacher_subject=teacher_subject_obj)
    months = {}
    for lesson_obj in lesson_objs:
        month = number_to_month(lesson_obj.date.month)
        if month not in months.values():
            months.update({lesson_obj.pk: month})
    json_months = json.dumps(months)

    student_lesson_objects = StudentLesson.objects.filter(lesson__in=lesson_objs)
    student_lesson_list = [
        {'student_pk': obj.student.pk,
         'lesson_pk': obj.lesson.pk,
         'mark': obj.mark} for obj in student_lesson_objects
    ]
    json_student_lesson_list = json.dumps(student_lesson_list)

    context = {
        'title': 'Journal',
        'lesson_create_form': LessonCreateForm(initial={'teacher_subject': teacher_subject_obj}),
        'group_subject': group_subject_obj,
        'teacher_subject': teacher_subject_obj,
        'lessons': lesson_objs,
        'months': json_months,
        'student_lesson_list': json_student_lesson_list,
        # студенти, які входять вже є у журналі
        'students': students,
        # інші студенти, які не входять в класс, але тієїж групи
        'other_students': other_students,
    }

    if request.method == "POST":
        # AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Write down a mark
            if request.POST['type'] == "write down a mark":
                student_pk = request.POST['student_pk']
                lesson_pk = request.POST['lesson_pk']
                value = request.POST['value']

                try:
                    lesson_obj = Lesson.objects.get(pk=lesson_pk)
                    student_obj = Student.objects.get(pk=student_pk)
                    stl_obj, created = StudentLesson.objects.get_or_create(lesson=lesson_obj, student=student_obj)

                    if value == "":
                        stl_obj.mark = None
                        stl_obj.save()
                    else:
                        if value == "н":
                            stl_obj.mark = value
                            stl_obj.save()
                        else:
                            assert isinstance(int(value), int)
                            assert int(value) >= 0
                            stl_obj.mark = value
                            stl_obj.save()

                    result = f"Зміни внесені: {created=}; {student_pk=}; {lesson_pk=}; {value=};"
                    return JsonResponse({'data': result}, status=200)
                except ValueError:
                    result = f"{value} - Неприйнятне значення!!!"
                    return JsonResponse({'data': result}, status=200)
                except AssertionError:
                    result = f"{value} - Неприйнятне значення"
                    return JsonResponse({'data': result}, status=200)
                except Exception as e:
                    result = f"Error: {e}"
                    return JsonResponse({'data': result}, status=200)
        # Add Student
        if request.POST['button'] == "add_student":
            selected_students_list = request.POST.getlist('students')
            students_list = teacher_subject_obj.get_students()
            for student in selected_students_list:
                students_list.append(student)
            teacher_subject_obj.set_students(students_list)
            teacher_subject_obj.save()
        # Delete Student
        if request.POST['button'] == "delete_student":
            selected_students_list = request.POST.getlist('students')
            students_list = teacher_subject_obj.get_students()
            for student in selected_students_list:
                students_list.remove(student)
            teacher_subject_obj.set_students(students_list)
            teacher_subject_obj.save()
        # Add Column
        if request.POST['button'] == "add_column":
            form = LessonCreateForm(request.POST)
            if form.is_valid():
                form.save()

        return redirect('journal')

    return render(request, 'journal/journal.html', context=context)


def example_table(request):
    return render(request, 'journal/example_table.html', {'title': 'example_table'})


def test_table(request):
    return render(request, 'journal/test_table.html', {'title': 'test_table'})


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
            user.role = self.request.POST['choices']
            user.save()
            Student.objects.create(user=user, group=group)
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


def number_to_month(number):
    if number == 1:
        return "Січень"
    elif number == 2:
        return "Лютий"
    elif number == 3:
        return "Березень"
    elif number == 4:
        return "Квітень"
    elif number == 5:
        return "Травень"
    elif number == 6:
        return "Червень"
    elif number == 7:
        return "Липень"
    elif number == 8:
        return "Серпень"
    elif number == 9:
        return "Вересень"
    elif number == 10:
        return "Жовтень"
    elif number == 11:
        return "Листопад"
    elif number == 12:
        return "Грудень"
    else:
        return "Undefind"
