from django.conf import settings

def STATIC_URL(request):
    return {'STATIC_URL': settings.STATIC_URL}