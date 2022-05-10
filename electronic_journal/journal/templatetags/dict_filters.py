from django import template

register = template.Library()


@register.filter
def get_value(obj, name):
    return obj.get(name)
