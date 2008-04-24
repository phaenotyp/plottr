# Django settings for plotter project.

# Note: All these settings could be overriden in local_settings.py 
# Check this possiblity when debugging. 
DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEVELOPMENT = False 

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''   # this is  
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'DE-de'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '4t+b0ly^h7u1(!c*0b$u22wfz6tx5r=uqf1jllqe*i7@#4$v7e'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'plotter.middleware.restful.AcceptMiddleware',
    'plotter.middleware.debugging.AJAXSimpleExceptionResponse',
)

ROOT_URLCONF = 'plotter.urls'

TEMPLATE_DIRS = (
    '/usr/share/djangoprojects/plotter/templates',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'plotter.apps.dates',
)

# url to the image indicating that there is no static map available 
NO_STATIC_MAP = 'http://www.condominiumsph.com/img/nomap.gif'

# now import local_settings, which are not under version-control.
# see http://mccormac.org/blog/2007/mar/28/localized-settings-django/
#  make sure there a local_settings.py file.
# import local settings overriding the defaults
try:
    from local_settings import *
except ImportError:
    try:
        from mod_python import apache
        apache.log_error( "local_settings.py not set; using default settings", apache.APLOG_NOTICE )
    except ImportError:
        import sys
        sys.stderr.write( "local_settings.py not set; using default settings\n" )
