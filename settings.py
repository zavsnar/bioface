# Django settings for s project.

from local_settings import DEBUG, TIME_ZONE, SOURCE_ROOT, DATABASES, LOGGING
from local_settings import SECRET_KEY, MANAGERS, ADMINS, DISALLOW_SEARCH_ROBOTS
from local_settings import STATIC_FILES_VERSION
from local_settings import DEFAULT_FROM_EMAIL, EMAIL_BACKEND, EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from local_settings import APP_SERVER_SETTINGS
from local_settings import THUMBNAIL_DUMMY
from local_settings import DEBUG_TOOLBAR_PANELS, INTERNAL_IPS
#from local_settings import HOST_NAME

from os.path import join

import djcelery
djcelery.setup_loader()

TEMPLATE_DEBUG = DEBUG

SITE_ID = 1

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-AU'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

PROJECT_ROOT = SOURCE_ROOT + '../'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = join(SOURCE_ROOT, '../media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = join(SOURCE_ROOT, '../static/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
if not (STATIC_FILES_VERSION is None):
    STATIC_URL = '/static%s/' % STATIC_FILES_VERSION
else:
    STATIC_URL = '/static/'

# Make sure to use a leading and trailing slashes.
# E.g.: '/admin/'.
ADMIN_SITE_PREFIX = '/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(SOURCE_ROOT, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
# STATICFILES_FINDERS = (
#     'django.contrib.staticfiles.finders.FileSystemFinder',
#     'django.contrib.staticfiles.finders.AppDirectoriesFinder',
# #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
# )

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'dajaxice.finders.DajaxiceFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(SOURCE_ROOT, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    # 'context_processors.STATIC_URL',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.sites', # is required by sitemaps
    'django.contrib.sitemaps',
    'django.contrib.humanize',

    # third-parties
    'djkombu',
    'kombu.transport.django',
    'djcelery',


    'dajaxice',
    'dajax',

    'ajaxuploader',

    #'django_select2',

    'jsonfield',

    'django_extensions',
    # 'runfcgi',
    # 'widget_tweaks',
    # 'pipeline',
    'bootstrapform',
    # 'sorl.thumbnail',
    'debug_toolbar',
    
    # original
    # 'apps.open_facebook',
    # 'apps.tasks',
    # 'apps.accounts',
    # 'apps.financial_accounts',
    # 'apps.eway_au',
    'apps.bioface',
    'apps.objects',
    'apps.sequences',
    # 'apps.attributes',
)

LOGIN_URL = '/login/'

DOWNLOADS_ROOT = MEDIA_ROOT + 'downloads/'
DOWNLOADS_URL = MEDIA_URL + 'downloads/'

SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 86400
# SESSION_COOKIE_AGE = 15

AUTH_USER_MODEL = 'bioface.CustomUser'

FIXTURE_DIRS = (
    join(SOURCE_ROOT, 'fixtures'),
)

AUTO_RENDER_SELECT2_STATICS = False

CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
BROKER_URL = 'django://'

# STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

# PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
# PIPELINE_YUI_CSS_ARGUMENTS = '--charset utf-8'

# PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.yui.YUICompressor'
# PIPELINE_YUI_JS_ARGUMENTS = '--charset utf-8'
# PIPELINE_YUI_BINARY = 'yui-compressor'
# PIPELINE_DISABLE_WRAPPER = True

# from static_pipelines import PIPELINE_CSS, PIPELINE_JS

# THUMBNAIL_DEBUG = DEBUG
# THUMBNAIL_PREFIX = 'thumbs/'

# TASK_CREATION_COST = 5 # AUD
# BID_CREATION_COST = 2 # AUD
