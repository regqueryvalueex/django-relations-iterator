import os

DIRNAME = os.path.dirname(__file__)

DEBUG = True
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'mydatabase'}}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'tasks',
)
