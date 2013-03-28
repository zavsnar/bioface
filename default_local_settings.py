from os.path import abspath, dirname, join

SOURCE_ROOT = dirname(abspath( __file__)) + '/'
PROJECT_NAME = 'bioface'

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

ADMINS = MANAGERS = ('zavsnar@gmail.com',)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'gw6&l9aqg(h=$g01j02hp34min4aexcxqa^-f_djsc7ca3('

# Email backend settings
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 25
# EMAIL_HOST_USER = None
# EMAIL_HOST_PASSWORD = None
# DEFAULT_FROM_EMAIL = u'TaskMarket<no-reply@tasks-market.levelupdev.com>'

DISALLOW_SEARCH_ROBOTS = True

# #FCGI settings. 'port' value should be specified explicitly
# APP_SERVER_SETTINGS = {
#     'host': '127.0.0.1',
#     'pidfile': join(SOURCE_ROOT, '../fcgi.pid'),
#     'method': 'prefork',
#     'maxchildren': 2,
#     'maxrequests': 0,
#     'debug': True,
#     'umask': '022',
#     'daemonize': 'false',
# }

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

BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis"
CELERY_REDIS_HOST = "localhost"
CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 0
CELERYD_LOG_FILE='/tmp/celery.log'
CELERND_TASK_ERROR_EMAILS = True 
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

import djcelery
djcelery.setup_loader()

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