from django.contrib.auth import get_user_model
from rest_framework import serializers

from journal.models import *

User = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'avatar', 'name', 'surname', 'patronymic', 'email', 'date_of_birth', 'about', 'role']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Teacher
        fields = ['pk', 'user']


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['pk', 'name']


class TeacherSpecializationSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(required=True)
    specialization = SpecializationSerializer(required=True)

    class Meta:
        model = TeacherSpecialization
        fields = ['pk', 'teacher', 'specialization']


class StudyFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyForm
        fields = ['pk', 'name']


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    study_form = StudyFormSerializer(required=True)
    Group = GroupSerializer(required=True)

    class Meta:
        model = Student
        fields = ['pk', 'user', 'study_form', 'group']


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['pk', 'full_name', 'short_name']


class EvaluationSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationSystem
        fields = ['pk', 'name', 'numerical_form']


class SubjectSerializer(serializers.ModelSerializer):
    evaluation_system = EvaluationSystemSerializer(required=True)

    class Meta:
        model = Subject
        fields = ['pk', 'name', 'slug', 'short_name', 'evaluation_system']


class GroupSubjectSerializer(serializers.ModelSerializer):
    group = GroupSerializer(required=True)
    subject = SubjectSerializer(required=True)

    class Meta:
        model = GroupSubject
        fields = ['pk', 'group', 'subject', 'amount_of_hours']


class TeacherSubjectSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(required=True)
    group_subject = GroupSubjectSerializer(required=True)

    class Meta:
        model = TeacherSubject
        fields = ['pk', 'teacher', 'group_subject', 'semester', 'academic_year', 'students']


class LessonTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonType
        fields = ['pk', 'name', 'slug']


class LessonSerializer(serializers.ModelSerializer):
    teacher_subject = TeacherSubjectSerializer(required=True)
    type = LessonTypeSerializer(required=True)

    class Meta:
        model = Lesson
        fields = ['pk', 'date', 'last_update', 'topic', 'homework', 'note', 'type', 'teacher_subject']


class StudentLessonSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer(required=True)
    student = StudentSerializer(required=True)

    class Meta:
        model = StudentLesson
        fields = ['pk', 'lesson', 'student', 'mark', 'date']


class MessageSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(required=True)
    to_user = UserSerializer(required=True)

    class Meta:
        model = Message
        fields = ['pk', 'from_user', 'to_user', 'time', 'text', 'is_check']


class ReplacementSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(required=True)
    teacher_subject = TeacherSubjectSerializer(required=True)

    class Meta:
        model = Replacement
        fields = ['pk', 'teacher', 'teacher_subject', 'date_from', 'date_to']

