# Django settings for logos project.
import os
import sys
import socket
import logging
import email_settings
logger = logging.getLogger(__name__)

# BASE_DIR is deemed to be one directory above this file's directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
# Probably best to leave DEBUG = False unless testing or debugging.  If set
# to true this uses up an inordinate amount of RAM over a short period of time.
# However CSS information doesn't show when running off the development server
# if DEBUG == True.

DEBUG_HOSTS_PATH = os.path.join(FILE_DIR, "debug_hosts.txt")
DEBUG = True
if os.path.isfile(DEBUG_HOSTS_PATH):
    f = open(DEBUG_HOSTS_PATH, "r")
    for line in f.readlines():
        if line.strip() == socket.gethostname():
            DEBUG = True

TEMPLATE_DEBUG = DEBUG

# This is used by the test runner to avoid threaded behaviour
# while testing.
IM_IN_TEST_MODE = False

#
# REGENERATE_TEST_DATABASE: Whether to recreate the test database 
# (if it doesn't already exist).  Sometimes I leave this as False because 
# it takes awhile to create the test database. After all, if it already exists, 
# why bother?  On the off chance it becomes corrupted you might want to 
# change this to True or maybe just delete 
# sqlite-databases\test-bibles.sqlite3.db might be the better option.
REGENERATE_TEST_DATABASE = False

ACCOUNT_ACTIVATION_DAYS = 3

# Expire browser sessions after 10 minutes of inactivity
SESSION_COOKIE_AGE = 10*60

ADMINS = (
    ('Splat', 'splat@myself.com'),
)

MANAGERS = ADMINS
DB_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "sqlite-databases")



DATABASES = {
    'default' : {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(DB_ROOT, 'default.sqlite3.db'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    },        

    'bibles': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(DB_ROOT, 'bibles.sqlite3.db'),  # Or path to database file if using sqlite3.
        'TEST_NAME': os.path.join(DB_ROOT, 'test-bibles.sqlite3.db'),
        # Don't overwrite the test database
        'CLOBBER_TEST_DB':False,
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    },
    'statistics': {
        'NAME': os.path.join(DB_ROOT, 'statistics.sqlite3.db'), 
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',          
    },
     'settings': {
        'NAME': os.path.join(DB_ROOT, 'settings.sqlite3.db'), 
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',          
    },
     'game-data': {
        'NAME': os.path.join(DB_ROOT, 'game-data.sqlite3.db'), 
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',          
    }
}


DATABASE_ROUTERS = ['logos.logos_router.LogosRouter',]

# Declare TEST_RUNNER to silence capricious warning message
# http://daniel.hepper.net/blog/2014/04/fixing-1_6-w001-when-upgrading-from-django-1-5-to-1-7/

#TEST_RUNNER = 'django.test.runner.DiscoverRunner'
TEST_RUNNER = 'bot.testing.logos_test_runner.LogosDiscoverRunner'

#### Email Settings

EMAIL_HOST = email_settings.EMAIL_HOST

EMAIL_PORT = email_settings.EMAIL_PORT 

EMAIL_HOST_USER = email_settings.EMAIL_HOST_USER

EMAIL_HOST_PASSWORD = email_settings.EMAIL_HOST_PASSWORD

EMAIL_USE_TLS = email_settings.EMAIL_USE_TLS

DEFAULT_FROM_EMAIL = email_settings.DEFAULT_FROM_EMAIL
SERVER_EMAIL = email_settings.SERVER_EMAIL
###### End -- Email Settings



SQLITE_DB_DIR = os.path.join(BASE_DIR, "sqlite-databases")

if not os.path.exists(SQLITE_DB_DIR):
    os.mkdir(SQLITE_DB_DIR)

if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

BIBLES_DIR = os.path.join(BASE_DIR, 'bibles')


# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
allowed_hosts = os.path.join(BASE_DIR, "allowed_hosts.txt")
f = open(allowed_hosts, "r")
for line in f.readlines():
    hostname = line.strip()
    ALLOWED_HOSTS.append(hostname)
f.close()
#ALLOWED_HOSTS.append(socket.gethostname())

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'assets'),
    os.path.join(BASE_DIR, 'vendor'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '^bs(!pky#$ijpvj-lzq3%su2u-q3x0aiw#1c@-8qlchds=4acd'

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
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.transaction.TransactionMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'logos.backends.CaseInsensitiveModelBackend', # this is default
    'guardian.backends.ObjectPermissionBackend',
)

ANONYMOUS_USER_ID = None  # Disable Anonymous Users

ROOT_URLCONF = 'logos.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'logos.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = (
  # ...
  'django.core.context_processors.request',
  # ...
  'django.contrib.messages.context_processors.messages',
  'django.contrib.auth.context_processors.auth',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, "templates"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
#    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'registration',
    'guardian',

    'logos',
    'cloud_notes',
    'cloud_memos',
    'pybb',
    'widget_tweaks',
#    'simple_forums',
    # Uncomment the next line to enable the admin:
     'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    
    # Add admin interface permission widget
    # http://permissions-widget.readthedocs.org/en/latest/
    'permissions_widget',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ' %(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'timeLog': {
            'format': ' %(asctime)s %(levelname)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'console_debug':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },        
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'logos-log.txt'),
            'formatter': 'timeLog'
        },        
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'cloud_notes': {
            'handlers': ['console_debug', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'logos': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'bot': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },        
        'plugins': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },        
        'plugins.twitter.plugin': {
            'handlers': ['console_debug', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        }, 
    },
    # the 'root' logger seems to cause things to
    # be logged twice.  Especially "manage.py import"
    'root': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
    },
}
