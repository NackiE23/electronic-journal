from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .forms import UserAdminChangeForm, UserAdminCreationForm
from .models import *

User = get_user_model()


@admin.register(User)
class UserInAdmin(UserAdmin):
    """ All User Admin Model (Include Super User) """
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    search_fields = ['email', 'name', 'surname', 'is_admin', 'is_staff', 'is_active']
    list_display = ['email', 'is_admin', 'is_staff', 'is_active']
    list_filter = ['is_admin', 'is_staff', 'is_active']

    fieldsets = (
        (None, {
            'fields': ('email', 'password', ('name', 'surname'),)
        }),
        ('Contact', {
            # 'classes': ('collapse',),
            'fields': ('phone_number',)
        }),
        ('Biographical Details', {
            # 'classes': ('collapse',),
            'fields': ('avatar',)
        }),
        ('Permissions', {
            'fields': ('is_admin', 'is_staff', 'is_active')
        }),
        # ('Group Permissions', {'fields': ('groups', 'user_permissions')}), if add permissions class
    )

    add_fieldsets = (
        (None, {
            # 'classes': ('wide',),
            'fields': ('name', 'surname', 'email', 'password1', 'password2')}
         ),
    )

    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(Teacher)
admin.site.register(Group)
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(EvaluationSystem)
admin.site.register(Subject)
admin.site.register(GroupSubject)
admin.site.register(TeacherSubject)
admin.site.register(Lesson)
admin.site.register(StudentGrade)
