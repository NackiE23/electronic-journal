from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import CreateView

from . import services
from .forms import *
from .models import *


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

    if request.method == "POST":
        # AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            text = request.POST['input_text']
            cur_user.about = text
            cur_user.save()
        # Send Message
        if request.POST['action'] == 'send_message':
            if request.POST['message-text']:
                services.send_message(from_user=get_user_model().objects.get(pk=request.POST['user_pk']),
                                      to_user=cur_user,
                                      text=request.POST['message-text'])
        # Change profile picture
        if request.POST['action'] == 'change_avatar':
            if cur_user == request.user:
                cur_user.avatar = request.FILES['file']
                cur_user.save()
        # Delete profile picture
        if request.POST['action'] == 'delete_avatar':
            if cur_user == request.user:
                cur_user.avatar = None
                cur_user.save()

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


def find_person(request):
    context = {
        'title': 'Find a person',
    }

    query = request.GET.get('q')
    if query:
        results = CustomUser.objects.filter(Q(name__icontains=query) |
                                            Q(surname__icontains=query) |
                                            Q(patronymic__icontains=query))
        if results:
            context.update({'results': results})
        else:
            context.update({'results': 'Не знайдено жодної подібності'})
    else:
        results = CustomUser.objects.all().exclude(role="Admin")
        context.update({'results': results})

    return render(request, 'journal/find_person.html', context=context)


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

    subjects = dict()
    for obj in teacher_subj_objs:
        obj_subject = obj.group_subject.subject
        obj_group_subj = obj.group_subject
        if obj_subject in subjects:
            subjects[obj_subject].append({'group_subject': obj_group_subj, 'teacher_pk': obj.teacher.pk})
        else:
            subjects.update({obj_subject: [{'group_subject': obj_group_subj, 'teacher_pk': obj.teacher.pk}]})

    replacements = dict()
    for obj in replacement_objs:
        obj_subject = obj.teacher_subject.group_subject.subject
        obj_group_subj = obj.teacher_subject.group_subject
        if obj_subject in replacements:
            replacements[obj_subject].append({'group_subject': obj_group_subj, 'teacher_pk': obj.teacher.pk, 'time': obj.date_to})
        else:
            replacements.update({obj_subject: [{'group_subject': obj_group_subj, 'teacher_pk': obj.teacher.pk, 'time': obj.date_to}]})

    context = {
        'title': 'Teacher journal list',
        # 'teacher_subjects': teacher_subj_objs,
        # 'replacements': replacement_objs,
        'subject_list': Subject.objects.all(),
        'group_list': Group.objects.all(),
        'journal_create_form': JournalCreateForm,
        'replacements': replacements.items(),
        'subjects': subjects.items()
    }

    if request.method == "POST":
        # Create journal
        if request.POST.get('action') == 'create_journal':
            teacher_obj = Teacher.objects.get(pk=teacher_pk)
            group_obj = Group.objects.get(name=request.POST['group'])
            subject_obj = Subject.objects.get(name=request.POST['subject'])
            semester = int(request.POST['semester'])
            academic_year = request.POST['academic_year']
            amount_of_hours = int(request.POST['amount_of_hours'])

            group_subject_obj, _ = GroupSubject.objects.get_or_create(
                group=group_obj,
                subject=subject_obj,
                amount_of_hours=amount_of_hours
            )

            TeacherSubject.objects.create(
                teacher=teacher_obj,
                group_subject=group_subject_obj,
                semester=semester,
                academic_year=academic_year
            )

            return redirect('teacher_journal_list', teacher_pk)

    return render(request, 'journal/teacher_journals.html', context=context)


def student_journal(request, student_pk):
    student_obj = Student.objects.get(pk=student_pk)
    group_subject_objs = GroupSubject.objects.filter(group=student_obj.group)
    group_teacher_subject_objs = TeacherSubject.objects.filter(group_subject__in=group_subject_objs)
    st_teacher_subject_objs = [obj for obj in group_teacher_subject_objs if obj.check_student(student_pk)]

    subjects = list()
    global_months = {}
    for pk, st_teacher_subject_obj in enumerate(st_teacher_subject_objs):
        lessons = Lesson.objects.filter(teacher_subject=st_teacher_subject_obj)
        st_lessons = StudentLesson.objects.filter(lesson__in=lessons, student=student_obj)

        paginate_by = 20
        lessons_pag = Paginator(lessons, paginate_by)
        st_lessons_pag = Paginator(st_lessons, paginate_by)
        page_number = int(request.GET.get(f'page{pk}')) if request.GET.get(f'page{pk}') else 1
        pag_lessons = lessons_pag.get_page(page_number)
        pag_st_lessons = st_lessons_pag.get_page(page_number)

        subjects.append({
            'page': f'page{pk}',
            'teacher_subject': st_teacher_subject_obj,
            'student_lessons': pag_st_lessons,
            'lessons': pag_lessons,
            'sequence_number': st_teacher_subject_obj.get_students().index(str(student_pk)) + 1,
        })

        months = {}
        for lesson_obj in list(lessons[(page_number - 1) * paginate_by:page_number * paginate_by]):
            month = number_to_month(lesson_obj.date.month)
            if month not in months.values():
                months.update({lesson_obj.pk: month})
        global_months.update(months)

    context = {
        'title': 'Student journal',
        'student': student_obj,
        'months': json.dumps(global_months),
        'subjects': subjects,
    }

    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.POST['type'] == "get_lesson_info":
                lesson_pk = request.POST['lesson_pk']
                lesson_obj = Lesson.objects.get(pk=lesson_pk)
                result = {
                    'teacher': lesson_obj.teacher_subject.teacher.user.get_name(),
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
    replacement_teachers = Replacement.objects.filter(teacher_subject=teacher_subject_obj)
    other_teachers = Teacher.objects.exclude(pk__in=[obj.teacher.pk for obj in replacement_teachers] + [teacher_subject_obj.teacher.pk])

    students_objs = Student.objects.filter(group=group_obj)
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
    paginate_by = 20
    paginator = Paginator(lesson_objs, paginate_by)
    if request.GET.get('page'):
        page_number = int(request.GET.get('page'))
    else:
        page_number = 1
    page_objs = paginator.get_page(page_number)
    json_lesson_objs = list(lesson_objs[(page_number - 1) * paginate_by:page_number * paginate_by])

    months = {}
    for lesson_obj in json_lesson_objs:
        month = number_to_month(lesson_obj.date.month)
        if month not in months.values():
            months.update({lesson_obj.pk: month})

    student_lesson_objects = StudentLesson.objects.filter(lesson__in=json_lesson_objs)
    student_lesson_list = [
        {'input_id': str(obj.student.pk) + str(obj.lesson.pk), 'mark': obj.mark} for obj in student_lesson_objects
    ]

    context = {
        'title': 'Journal',
        'lesson_create_form': LessonCreateForm(initial={'teacher_subject': teacher_subject_obj}),
        'group_subject': group_subject_obj,
        'teacher_subject': teacher_subject_obj,
        'lessons': page_objs,
        'lesson_update_form': LessonUpdateForm,
        'months': json.dumps(months),
        'student_lesson_list': json.dumps(student_lesson_list),
        'students': students,
        'other_students': other_students,
        'other_teachers': other_teachers,
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
                            assert int(value) <= subject_obj.evaluation_system.numerical_form
                            stl_obj.mark = value
                            stl_obj.save()

                    result = f"Відмітка занесена успішно"
                    return JsonResponse({'data': result, 'value': value, 'error': False}, status=200)
                except ValueError:
                    result = f"{value} - Неприйнятне значення!"
                    return JsonResponse({'data': result, 'value': value, 'error': True}, status=200)
                except AssertionError:
                    result = f"{value} - Неприйнятне значення"
                    return JsonResponse({'data': result, 'value': value, 'error': True}, status=200)
                except Exception as e:
                    result = f"Error: {e}"
                    return JsonResponse({'data': result, 'value': value, 'error': True}, status=200)
            # Get lesson info
            if request.POST['type'] == "get lesson info":
                lesson_obj = Lesson.objects.get(pk=request.POST['lesson_pk'])
                info = {
                    'date': lesson_obj.date,
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
                    field = request.POST['field']
                    if field == 'date':
                        lesson_obj.date = request.POST['value']
                        lesson_obj.save()
                    elif field == 'topic':
                        lesson_obj.topic = request.POST['value']
                        lesson_obj.save()
                    elif field == 'homework':
                        lesson_obj.homework = request.POST['value']
                        lesson_obj.save()
                    elif field == 'note':
                        lesson_obj.note = request.POST['value']
                        lesson_obj.save()
                    elif field == 'type':
                        lesson_obj.type = LessonType.objects.get(pk=int(request.POST['value']))
                        lesson_obj.save()
                    return JsonResponse({'data': 'Поле було успішно змінено'}, status=200)
                except Exception as e:
                    return JsonResponse({'data': f"Error: {e}"}, status=200)
        # Add Student
        if request.POST['button'] == "add_student":
            selected_students_list = request.POST.getlist('students')
            students_list = teacher_subject_obj.get_students() if condition else list()
            for student in selected_students_list:
                if student:
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
            teacher_selected_pk = int(request.POST['selected_teacher'])
            date_to = request.POST['up-to-date-input']
            Replacement.objects.create(
                teacher=Teacher.objects.get(pk=teacher_selected_pk),
                teacher_subject=teacher_subject_obj,
                date_to=date_to
            )
        # Delete Student
        if request.POST['button'] == "delete_student":
            selected_students_list = request.POST.getlist('students')
            students_list = teacher_subject_obj.get_students()
            for student in selected_students_list:
                if student:
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


class StaffMemberRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class RegisterUser(StaffMemberRequiredMixin, CreateView):
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
    authentication_form = LoginUserForm
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
        return "Січ."
    elif number == 2:
        return "Лют."
    elif number == 3:
        return "Бер."
    elif number == 4:
        return "Квіт."
    elif number == 5:
        return "Трав."
    elif number == 6:
        return "Черв."
    elif number == 7:
        return "Лип."
    elif number == 8:
        return "Серп."
    elif number == 9:
        return "Вер."
    elif number == 10:
        return "Жовт."
    elif number == 11:
        return "Лист."
    elif number == 12:
        return "Груд."
    else:
        return "Undefind"
