from django import template

register = template.Library()

@register.filter(name='abs')
def absolute_value(value):
    """
    Returns the absolute value of the given number.
    Usage in template: {{ value|abs }}
    """
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value
