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
        'messages': Message.objects.filter(to_user=request.user).order_by('-time'),
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


def teacher_journal_list(request, teacher_pk):
    teacher_subj_objs = TeacherSubject.objects.filter(teacher__pk=teacher_pk)
    replacement_objs = Replacement.objects.filter(teacher__pk=teacher_pk)

    context = {
        'title': 'Teacher journal list',
        'teacher_subjects': teacher_subj_objs,
        'replacements': replacement_objs,
    }
    return render(request, 'journal/teacher_journals.html', context=context)


def student_journal(request, student_pk):
    student_obj = Student.objects.get(pk=student_pk)
    group_subject_objs = GroupSubject.objects.filter(group=student_obj.group)
    group_teacher_subject_objs = TeacherSubject.objects.filter(group_subject__in=group_subject_objs)
    st_teacher_subject_objs = [obj for obj in group_teacher_subject_objs if obj.check_student(student_pk)]
    lesson_objs = Lesson.objects.filter(teacher_subject__in=st_teacher_subject_objs)
    st_lesson_objs = StudentLesson.objects.filter(lesson__in=lesson_objs, student=student_obj).order_by('lesson__date')

    months = {}
    for st_teacher_subject_obj in st_teacher_subject_objs:
        l_lesson_objs = Lesson.objects.filter(teacher_subject=st_teacher_subject_obj)
        l_months = {}
        for lesson_obj in l_lesson_objs:
            month = number_to_month(lesson_obj.date.month)
            if month not in l_months.values():
                l_months.update({lesson_obj.pk: month})
                months.update({lesson_obj.pk: month})

    context = {
        'title': 'Student journal',
        'student': student_obj,
        'st_teacher_subjects': st_teacher_subject_objs,
        'lessons': lesson_objs,
        'student_lessons': st_lesson_objs,
        'months': json.dumps(months),
    }

    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.POST['type'] == "get_lesson_info":
                lesson_pk = request.POST['lesson_pk']
                lesson_obj = Lesson.objects.get(pk=lesson_pk)
                result = {
                    'teacher': lesson_obj.teacher_subject.teacher.user.get_full_name(),
                    'subject': lesson_obj.teacher_subject.group_subject.subject.name,
                    'last_update': lesson_obj.last_update,
                    'date': lesson_obj.date,
                    'topic': lesson_obj.topic,
                    'homework': lesson_obj.homework,
                    'note': lesson_obj.note,
                    'type': lesson_obj.type.name,
                }
                return JsonResponse(result, status=200)

    return render(request, 'journal/student_journal.html', context=context)


def teacher_journal(request, teacher_pk, group_slug, subject_slug):
    if request.user.role != "Teacher":
        return redirect('student_journal', request.user.student.pk)

    group_obj = Group.objects.get(slug=group_slug)
    subject_obj = Subject.objects.get(slug=subject_slug)
    group_subject_obj = GroupSubject.objects.get(group=group_obj, subject=subject_obj)

    teacher_obj = Teacher.objects.get(pk=teacher_pk)
    teacher_subject_obj = TeacherSubject.objects.get(group_subject=group_subject_obj, teacher=teacher_obj)
    teacher_subject_objs = TeacherSubject.objects.filter(group_subject=group_subject_obj)

    students_objs = Student.objects.filter(group=group_obj).order_by('-user')
    condition = teacher_subject_obj.if_exist()
    students = students_objs.filter(pk__in=teacher_subject_obj.get_students()) if condition \
        else None
    other_students = list()
    for obj in teacher_subject_objs:
        if obj.if_exist():
            other_students += obj.get_students()
    other_students = students_objs.exclude(pk__in=other_students) if len(other_students) > 0 \
        else students_objs

    lesson_objs = Lesson.objects.filter(teacher_subject=teacher_subject_obj)
    months = {}
    for lesson_obj in lesson_objs:
        month = number_to_month(lesson_obj.date.month)
        if month not in months.values():
            months.update({lesson_obj.pk: month})

    student_lesson_objects = StudentLesson.objects.filter(lesson__in=lesson_objs)
    student_lesson_list = [
        {'student_pk': obj.student.pk,
         'lesson_pk': obj.lesson.pk,
         'mark': obj.mark} for obj in student_lesson_objects
    ]

    context = {
        'title': 'Journal',
        'lesson_create_form': LessonCreateForm(initial={'teacher_subject': teacher_subject_obj}),
        'group_subject': group_subject_obj,
        'teacher_subject': teacher_subject_obj,
        'lessons': lesson_objs,
        'lesson_update_form': LessonUpdateForm,
        'months': json.dumps(months),
        'student_lesson_list': json.dumps(student_lesson_list),
        'students': students,
        'other_students': other_students,
        'other_teachers': Teacher.objects.exclude(pk=teacher_subject_obj.teacher.pk),
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
            # Get lesson info
            if request.POST['type'] == "get lesson info":
                lesson_obj = Lesson.objects.get(pk=request.POST['lesson_pk'])
                info = {
                    'topic': lesson_obj.topic,
                    'homework': lesson_obj.homework,
                    'note': lesson_obj.note,
                    'type_pk': lesson_obj.type.pk,
                }
                return JsonResponse(info, status=200)
            # Change lesson
            if request.POST['type'] == "change_lesson":
                try:
                    lesson_obj = Lesson.objects.get(pk=request.POST['lesson_pk'])
                    if request.POST['name'] == 'topic':
                        lesson_obj.topic = request.POST['value']
                        lesson_obj.save()
                    elif request.POST['name'] == 'homework':
                        lesson_obj.homework = request.POST['value']
                        lesson_obj.save()
                    elif request.POST['name'] == 'note':
                        lesson_obj.note = request.POST['value']
                        lesson_obj.save()
                    elif request.POST['name'] == 'type':
                        lesson_obj.type = LessonType.objects.get(pk=int(request.POST['value']))
                        lesson_obj.save()
                    return JsonResponse({'message': 'Lesson changed successfuly'}, status=200)
                except Exception as e:
                    return JsonResponse({'message': f"Error: {e}"}, status=200)
        # Add Student
        if request.POST['button'] == "add_student":
            selected_students_list = request.POST.getlist('students')
            students_list = teacher_subject_obj.get_students() if condition else list()
            for student in selected_students_list:
                students_list.append(student)
            teacher_subject_obj.set_students(students_list)
            teacher_subject_obj.save()
        # Add Column
        if request.POST['button'] == "add_column":
            form = LessonCreateForm(request.POST)
            if form.is_valid():
                form.save()
        # Add Teacher Allow To Change A Jounal
        if request.POST['button'] == "allow_teacher":
            select = request.POST['teacher-select-input']
            date = request.POST['up-to-date-input']
            print({'select': select, 'date': date})
        # Delete Student
        if request.POST['button'] == "delete_student":
            selected_students_list = request.POST.getlist('students')
            students_list = teacher_subject_obj.get_students()
            for student in selected_students_list:
                students_list.remove(student)
            teacher_subject_obj.set_students(students_list)
            teacher_subject_obj.save()
        # Delete lesson
        if request.POST['button'] == "delete_lesson":
            try:
                Lesson.objects.get(pk=request.POST['lesson_pk']).delete()
                return redirect('teacher_journal', teacher_pk, group_slug, subject_slug)
            except Exception as e:
                return JsonResponse({'message': f'Error: {e}'}, status=200)

        return redirect('teacher_journal', teacher_pk, group_slug, subject_slug)

    return render(request, 'journal/teacher_journal.html', context=context)


def admin_settings(request):
    context = {
        'title': 'Admin Settings',
        'subject_creation_form': SubjectCreationForm,
        'subject_creation_full_form': SubjectFullCreationForm,
    }

    return render(request, 'journal/admin_settings.html', context=context)


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
