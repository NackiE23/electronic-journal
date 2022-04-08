from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

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
    list_display = ['email', 'get_html_photo', 'is_admin', 'is_staff', 'is_active']
    list_filter = ['is_admin', 'is_staff', 'is_active']

    fieldsets = (
        (None, {
            'fields': ('email', 'password', ('name', 'surname', 'patronymic'), 'role', 'about',)
        }),
        ('Contact', {
            # 'classes': ('collapse',),
            'fields': ('phone_number',)
        }),
        ('Biographical Details', {
            # 'classes': ('collapse',),
            'fields': ('avatar', 'get_html_photo', 'date_of_birth')
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
    readonly_fields = ('get_html_photo', 'is_admin', 'is_staff', 'is_active')

    def get_html_photo(self, object):
        if object.avatar:
            return mark_safe(f"<img src='{object.avatar.url}' width=50>")

    get_html_photo.short_description = "Miniature"


class StudentLessonAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'student', 'mark', 'date']
    readonly_fields = ('date', )


class SlugToName(admin.ModelAdmin):
    prepopulated_fields = {'slug': ("name",)}


admin.site.register(Teacher)
admin.site.register(Group, SlugToName)
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(EvaluationSystem)
admin.site.register(Subject, SlugToName)
admin.site.register(GroupSubject)
admin.site.register(TeacherSubject)
admin.site.register(Lesson)
admin.site.register(LessonType)
admin.site.register(StudentLesson, StudentLessonAdmin)
