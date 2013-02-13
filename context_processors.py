from django.conf import settings

def STATIC_URL(request):
    return {'STATIC_URL': settings.STATIC_URL}

# def GOOGLE_ANALITICS_ID(request):
#     return {'GOOGLE_ANALITICS_ID': settings.GOOGLE_ANALITICS_ID}

# def FACEBOOK_ADMIN_ACCOUNTS(request):
#     return {'FACEBOOK_ADMIN_ACCOUNTS': settings.FACEBOOK_ADMIN_ACCOUNTS}

# def FACEBOOK_APP_ID(request):
#     return {'FACEBOOK_APP_ID': settings.FACEBOOK_APP_ID}

# def ENABLE_GOOGLE_API_LIBS(request):
#     return {'ENABLE_GOOGLE_API_LIBS': settings.ENABLE_GOOGLE_API_LIBS}

# def GOOGLE_MAPS_API_KEY(request):
#     return {'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY}