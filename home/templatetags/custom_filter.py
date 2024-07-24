from django import template

register = template.Library()

@register.filter
def range_custom(value):
    return range(int(value))

@register.filter
def range_diff(value, diff):
    return range(int(diff) - int(value))