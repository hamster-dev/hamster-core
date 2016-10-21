
import os
import tempfile
import importlib
import logging

logger = logging.getLogger(__name__)


DEBUG = True if 'HAMSTER_DEBUG' in os.environ else False
TEMPLATE_DEBUG = DEBUG

#TODO: refactor these auth variables into the database
github_hostname = os.environ.get(
    'HAMSTER_GITHUB_HOST', 'github.com'
)
HAMSTER_GITHUB_URL = "https://{}".format(github_hostname)
HAMSTER_GITHUB_USER = os.environ.get(
    'HAMSTER_GITHUB_API_USER'
)
HAMSTER_GITHUB_TOKEN = os.environ.get(
    'HAMSTER_GITHUB_API_TOKEN'
)

class Secrets(object):
    """Container for injecting secrets into pipeline build context.
    """
    jenkins_user = os.environ.get(
        'HAMSTER_JENKINS_API_USERNAME'
    )
    jenkins_token = os.environ.get(
        'HAMSTER_JENKINS_API_TOKEN'
    )

SECRETS = Secrets()

HAMSTER_FILTER_MODULES = []

HAMSTER_MATCHER_MODULES = []
#TODO: move this to some initialization code
for matcher in HAMSTER_MATCHER_MODULES:
    try:
        importlib.import_module(matcher)
    except ImportError as exc:
        logger.error(
            "Could not iport matcher {}: {}".format(
                matcher, exc
            ))

# this will run on the worker, so s/b correct
PIPELINE_WORKSPACE_ROOT = tempfile.gettempdir()

#TODO: this is docker-specific. Can I set
BROKER_URL = CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

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
    #'pipeline',  # TODO this is here ony for task registration in celery.py - figure out another way to get the pipeline tasks
    'core',
    'hookshot',
    'pipeline',
    'watbot',
    'dt2',
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
        'core': {
           'handlers': ['console'],
           'level': 'DEBUG',
           'propagate': False,
        },
        'hookshot': {
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
        'watbot': {
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
