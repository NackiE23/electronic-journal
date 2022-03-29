from django import template
from journal.models import *

register = template.Library()


@register.filter(name='date_form_for_input')
def correct_date(date, date_filter=None):
    if not date:
        return '0000-00-00'
    if date_filter:
        return date.strftime(date_filter)
    return date.strftime("%Y-%m-%d")
