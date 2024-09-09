from django import template
from django.utils import timezone
from home.models import Pages  # Make sure this import is correct
import pytz

register = template.Library()

@register.filter
def range_custom(value):
    return range(int(value))

@register.filter
def range_diff(value, diff):
    return range(int(diff) - int(value))

@register.filter
def is_restaurant_open(start_time, end_time):
    auckland_tz = pytz.timezone('Pacific/Auckland')
    current_time = timezone.now().astimezone(auckland_tz).time()
    if start_time and end_time:
        return start_time <= current_time <= end_time
    return False

@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})

@register.filter
def is_page(value):
    item = Pages.objects.filter(status="Active",slug=value).last()
    return item

@register.filter
def add_class(field, css_class):
    if hasattr(field, 'as_widget'): 
        return field.as_widget(attrs={'class': css_class})
    return field