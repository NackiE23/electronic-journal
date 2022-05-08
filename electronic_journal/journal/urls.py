from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('', own_profile, name="main"),
    path('profile/', own_profile, name="own_profile"),
    path('profile/<int:pk>/', profile, name="profile"),
    path('profile/edit/', UserEditView.as_view(), name="edit_profile"),
    path('messages/', messages, name="messages"),
    path('find_person/', find_person, name="find_person"),
    path('group/<slug:group_slug>/', group, name="group"),
    path('journal/teacher-<int:teacher_pk>/list/', teacher_journal_list, name="teacher_journal_list"),
    path('journal/<int:teacher_pk>/<slug:group_slug>/<slug:subject_slug>/', teacher_journal, name="teacher_journal"),
    path('journal/student-<int:student_pk>/', student_journal, name="student_journal"),
    path('register/', RegisterUser.as_view(), name="register"),
    path('login/', LoginUser.as_view(), name="login"),
    path('logout/', logout_user, name="logout"),
    path('password/change/', PasswordsChangeView.as_view(), name="password_change"),

    path('main/', main, name="gl_main"),
    path('settings/', admin_settings, name="admin_settings"),
]
