
import os
import tempfile

DEBUG = True if 'HAMSTER_DEBUG' in os.environ else False
TEMPLATE_DEBUG = DEBUG

github_hostname = os.environ.get(
    'HAMSTER_GITHUB_HOST', 'github.com'
)
HAMSTER_GITHUB_URL = "https://{}".format(github_hostname)
HAMSTER_GITHUB_USERNAME = os.environ.get(
    'HAMSTER_GITHUB_API_USERNAME'
)
HAMSTER_GITHUB_TOKEN = os.environ.get(
    'HAMSTER_GITHUB_API_TOKEN'
)

# this will run on the worker, so s/b correct
PIPELINE_WORKSPACE_ROOT = tempfile.gettempdir()

#TODO: this is docker-specific. Can I set
# 'PIPELINE_BROKER=REDIS_PORT_6379_TCP_ADDR' in fig.yml?
celery_host = os.environ.get('REDIS_PORT_6379_TCP_ADDR', 'localhost')
BROKER_URL = CELERY_RESULT_BACKEND = 'redis://{}:6379/0'.format(celery_host)

#TODO celery recommends against using pickle serializer,
# but in order to use json we will need to make changes to
# some internal structures to make them json-serializable.
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_RESULT_SERIALIZER = CELERY_TASK_SERIALIZER = 'pickle'

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ALLOWED_HOSTS = ['*']  # FIXME

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'pipeline',  # TODO this is here ony for task registration in celery.py - figure out another way to get the pipeline tasks
    'pipeline_django',
    'pullman',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'hamster.urls'

WSGI_APPLICATION = 'hamster.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'github3': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'requests': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'pipeline_django': {
           'handlers': ['console'],
           'level': 'DEBUG',
           'propagate': False,
        },
        'pullman': {
           'handlers': ['console'],
           'level': 'DEBUG',
           'propagate': False,
        },
        'commandsession': {
           'handlers': ['console'],
           'level': 'DEBUG',
           'propagate': False,
        },
        'pipeline': {
           'handlers': ['console'],
           'level': 'DEBUG',
           'propagate': False,
        },
        'hamster': {
           'handlers': ['console'],
           'level': 'DEBUG',
           'propagate': False,
        }
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
#STATICFILES_DIRS = (os.path.join(BASE_DIR, 'hamster', "static"),)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')


SECRET_KEY = 'XYZ'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'  # for log timestamps
USE_I18N = True
USE_L10N = True
USE_TZ = True
