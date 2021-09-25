from django.conf import settings

def app_versions(request):
    return {
        'version': settings.VERSION
    }