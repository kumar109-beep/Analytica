from django.contrib import admin

from . models import Geography, GeographyLevel, Survey, Category, Indicator, Attribute, Answer


admin.site.register([Geography, GeographyLevel, Survey, Category, Indicator, Attribute, Answer])
# Register your models here.
