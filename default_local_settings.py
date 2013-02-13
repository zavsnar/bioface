from os.path import abspath, dirname, join

SOURCE_ROOT =  dirname(abspath( __file__))
DEBUG = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None    # operating system timezone

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': join(dirname(SOURCE_ROOT), 'database'),  # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'tasks': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'open_facebook': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'financial_accounts': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'eway_au': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'accounts': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

STATIC_FILES_VERSION = None

ADMINS = MANAGERS = tuple()

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'gw6&l9aqg(h=$g01j02hp34min4ae2&)wnbqa^-f_djsc7ca3('

# Email backend settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None
DEFAULT_FROM_EMAIL = u'TaskMarket<no-reply@tasks-market.levelupdev.com>'

DISALLOW_SEARCH_ROBOTS = True

#FCGI settings. 'port' value should be specified explicitly
APP_SERVER_SETTINGS = {
    'host': '127.0.0.1',
    'pidfile': join(SOURCE_ROOT, '../fcgi.pid'),
    'method': 'prefork',
    'maxchildren': 2,
    'maxrequests': 0,
    'debug': True,
    'umask': '022',
    'daemonize': 'false',
}

# FACEBOOK_APP_ID for tasks-market.levelupdev.com. It is registered to Evgeny Evseev (pelid).
# None value disables Facebook API integration
FACEBOOK_APP_ID = '459911757376906'
FACEBOOK_APP_SECRET = 'ea4a98c90dce193552a7d4608adeb7c7'
FACEBOOK_READ_ONLY = False

FACEBOOK_ADMIN_ACCOUNTS = ['1333909046']    # pelid (Evgeny Evseev)
GOOGLE_ANALITICS_ID = None

ENABLE_GOOGLE_API_LIBS = not DEBUG

THUMBNAIL_DUMMY = False # This will generate placeholder images for all thumbnails missing input source.

GOOGLE_MAPS_API_KEY = 'AIzaSyCoxQ3CrUtILPA_q7dKezriOzuR_l_B0-4' # It is registered to Evgeny Evseev (pelid80@gmail.com)>>>>>>> other

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

INTERNAL_IPS = ('127.0.0.1',)

# Eway.com.au test account , Test Credit Card is  4444333322221111
# EWAY_AU_MERCHANT = {
#         'customer_id': '87654321',
#         'username': 'TestAccount',
#     }

# Eway.com.au sandbox account
# EWAY_AU_MERCHANT = {
#         'customer_id': '91389768',
#         'username': 'me@orend.net.sand',
#     }

# DISABLE_SSL_CERTIFICATE_VALIDATION = True