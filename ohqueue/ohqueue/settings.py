import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASGI_APPLICATION = 'ohqueue.routing.application'

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '=)')
DEBUG = os.environ.get('DJANGO_DEBUG', "TRUE") == "TRUE"
DOCKER = os.environ.get('DJANGO_DOCKER', "FALSE") == "TRUE"
TESTING = sys.argv[1:2] == ['test'] or sys.argv[1:2] == ['jenkins']
SSL = os.environ.get('DJANGO_SSL', "FALSE") == "TRUE"
DJANGO_HOSTNAME = os.environ.get('DJANGO_HOSTNAME', 'localhost')

ALLOWED_HOSTS = [DJANGO_HOSTNAME, 'ohqueue_server']

if DJANGO_HOSTNAME == 'localhost':
    ALLOWED_HOSTS += ['0.0.0.0', '127.0.0.1']

if SSL:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# change password hashing for faster testing
if TESTING:
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )

TEST_RUNNER = 'ohqueue.runner.PytestTestRunner'


WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    }
}

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'frontend/assets'),
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'rest_framework',
    'backend_app',
    'frontend',
    'webpack_loader',
    'corsheaders'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'ohqueue.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ohqueue.wsgi.application'

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('POSTGRES_DB', 'postgres'),
            'USER': os.environ.get('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': '5432',
        }
    }

REDIS_HOST = 'redis' if DOCKER else 'localhost'
RQ_QUEUES = {
    'default': {
        'HOST': REDIS_HOST,
        'PORT': 6379,
        'DB': 0
    },
    'high': {
        'HOST': REDIS_HOST,
        'PORT': 6379,
        'DB': 0
    },
    'low': {
        'HOST': REDIS_HOST,
        'PORT': 6379,
        'DB': 0,
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, 6379)],
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        }
    },
    'loggers': {
        'backend_app.consumers': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    }
}

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', 'guardian.backends.ObjectPermissionBackend')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
}

CHANNELS_API = {
    'DEFAULT_PERMISSION_CLASSES': ('channels_api.permissions.IsAuthenticated',)
}

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
if DOCKER:
    MEDIA_ROOT = '/media/'
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")

if DOCKER:
    STATIC_ROOT = '/static/'
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
