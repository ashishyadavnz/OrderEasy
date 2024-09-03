from django import template
from django.utils import timezone  # Make sure this import is correct

register = template.Library()

@register.filter
def range_custom(value):
    return range(int(value))

@register.filter
def range_diff(value, diff):
    return range(int(diff) - int(value))

@register.filter
def is_restaurant_open(start_time, end_time):
    current_time = timezone.now().time()  # This now uses Django's timezone
    if start_time and end_time:
        return start_time <= current_time <= end_time
    return False

@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})