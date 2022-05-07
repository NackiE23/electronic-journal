from django import template

from journal.models import *

register = template.Library()


@register.filter(name='enum')
def enum(value):
    return enumerate(value)


@register.filter(name='id')
def journal_id(value):
    return value[0] + 1


@register.filter(name='name')
def journal_name(value):
    return value[1]


@register.filter(name='get_pk')
def journal_student_pk(value):
    return value[1].pk


@register.filter(name='get_user_pk')
def journal_student_as_user_pk(value):
    return value[1].user.pk
