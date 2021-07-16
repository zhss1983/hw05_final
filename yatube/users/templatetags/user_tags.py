from django import template

register = template.Library()


@register.simple_tag
def new_variable(variable):
    return variable
