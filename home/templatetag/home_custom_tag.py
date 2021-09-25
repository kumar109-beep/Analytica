from django.template.defaulttags import register
from rolepermissions.roles import get_user_roles
# from rolepermissions.shortcuts import get_user_role

from django.conf import settings

@register.filter
def get_version():
    return { 'version': settings.VERSION }