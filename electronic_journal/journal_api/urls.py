from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'teachers', views.TeacherViewSet)
router.register(r'specializations', views.SpecializationViewSet)
router.register(r'tr_specializations', views.TeacherSpecializationViewSet)
router.register(r'study_form', views.StudyFormViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'attendances', views.AttendanceViewSet)
router.register(r'evaluation_systems', views.EvaluationSystemViewSet)
router.register(r'subjects', views.SubjectViewSet)
router.register(r'group_subjects', views.GroupSubjectViewSet)
router.register(r'teacher_subjects', views.TeacherSubjectViewSet)
router.register(r'lesson_types', views.LessonTypeViewSet)
router.register(r'lessons', views.LessonViewSet)
router.register(r'student_lessons', views.StudentLessonViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'replacements', views.ReplacementViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # session (browser) api auth
    path('drf-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # token api auth
    path('token-auth/', obtain_auth_token),
]
