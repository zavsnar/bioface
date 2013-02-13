from django import template

register = template.Library()

@register.filter
def get(d, key):
	return d.get(key, '')

@register.filter
def is_false(arg): 
    return arg is False

@register.filter
def is_true(arg): 
    return arg is True