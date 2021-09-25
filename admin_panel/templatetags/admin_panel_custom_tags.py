from django.template.defaulttags import register
from rolepermissions.roles import get_user_roles
# from rolepermissions.shortcuts import get_user_role

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

from django import template

register = template.Library()

@register.filter
def replace(value, args=","):
    try:
        old, new = args.split(',')
        return value.replace(old, new).title()
    except ValueError:
        return value

@register.filter
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return None
        
@register.filter
def list_item(lst, i):
    try:
        return lst[i]
    except:
        return None

@register.filter
def get_role(user):
    role = get_user_roles(user)
    if role:
        return role[0].__name__
    else:
        return "Super Admin"
    # return user.groups.filter(name=group_name).exists()