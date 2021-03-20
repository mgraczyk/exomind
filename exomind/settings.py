import os
import dj_database_url
import raven


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY')

SESSION_COOKIE_AGE = 31536000

# https://devcenter.heroku.com/articles/getting-started-with-python#introduction
if os.getenv('ENVIRONMENT') == 'development':
  DEBUG = True
  ALLOWED_HOSTS = ['*']
  CORS_ORIGIN_ALLOW_ALL = True

  try:
    release_name = raven.fetch_git_sha(os.path.dirname(os.pardir)) + "-dev"
  except Exception:
    release_name = 'unknown-dev'
else:
  DEBUG = False

  ALLOWED_HOSTS = ['*']
  CORS_ORIGIN_ALLOW_ALL = True

  SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
  SECURE_CONTENT_TYPE_NOSNIFF = True
  SECURE_BROWSER_XSS_FILTER = True
  SECURE_SSL_REDIRECT = True
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True

  # Get git sha from build.
  release_name = 'TODO'

SITE_URL = os.getenv('SITE_ENV')

# Application definition

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'app',
    'crawler',
    'social_django',
    'raven.contrib.django.raven_compat',
]

if os.getenv('MIGRATE_SOCIAL_HACK'):
  INSTALLED_APPS.remove('social_django')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # Serving static files.
    'exomind.whitenoise_catchall_middleware.WhiteNoiseCatchAllMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crawler.middleware.CrawlerMiddleware',
]

ROOT_URLCONF = 'exomind.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

ASGI_APPLICATION = 'exomind.asgi.application'

DATABASES = {'default': dj_database_url.config()}

DATABASES['default'].setdefault('OPTIONS', {})
if not os.getenv('ENVIRONMENT') == 'development':
  DATABASES['default']['OPTIONS']['sslmode'] = 'require'

DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
DATABASES['default']['CONN_MAX_AGE'] = 0
# DATABASES['default']['OPTIONS']['MAX_CONNS'] = 80


AUTH_USER_MODEL = 'app.user'
# AUTHENTICATION_BACKENDS = ('exomind.django_auth_jwt_backend.JWTBackend',)

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login'

# Social Auth Settings
SOCIAL_AUTH_USER_MODEL = 'app.User'
SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
SOCIAL_AUTH_TWITTER_KEY = os.getenv('SOCIAL_AUTH_TWITTER_KEY')
SOCIAL_AUTH_TWITTER_SECRET = os.getenv('SOCIAL_AUTH_TWITTER_SECRET')
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
)

# Setup Sentry.
# https://docs.sentry.io/clients/python/integrations/django/
RAVEN_CONFIG = {
    'dsn': os.getenv('SENTRY_DSN'),
    'release': release_name,
    'ignore_exceptions':
    ('common.exceptions.AgainError', 'common.exceptions.UserInputError',
     'common.exceptions.InvalidTwoFactorCode'),
}

ATOMIC_REQUESTS = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s:%(filename)s:%(lineno)d] %(message)s'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'exomind': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = True


STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
WHITENOISE_MAX_AGE=600
