from django import template

register = template.Library()

@register.filter
def get(d, key):
	print d
	return d.get(key, '')

@register.filter
def is_false(arg): 
    return arg is False

@register.filter
def is_true(arg): 
    return arg is True

@register.filter(name='split')
def split(value, arg):
    return value.split(arg) if value else value