from django import template

register = template.Library()


@register.simple_tag
def add_variable(value):
    return value
