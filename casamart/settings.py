
import datetime
import os
from pathlib import Path

import cloudinary
import cloudinary.uploader
import cloudinary.api
import dj_database_url

from python_paystack.paystack_config import PaystackConfig

# from python_paystack.paystack_config import PaystackConfig

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-n&%-v!ww@*g2as4^c$px1ace(0asndsvj9ph6!(938&)34d+8g"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["cassamart.up.railway.app", "localhost"]


# Application definition

INSTALLED_APPS = [
    # LOCAL APPS
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "daphne",
    "django.contrib.staticfiles",
    'store',
    'accounts',
    "chat",
    "payment",
    "manager",


    # 3RD PARTY packages
    'channels',
    'cloudinary_storage',
    'cloudinary',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'corsheaders',
    "python_paystack",
    'rest_framework_swagger',
    'drf_yasg',
    'django_filters',
    ]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]



AUTHENTICATION_BACKENDS = [
'accounts.authentication.EmailAuthBackend',
'django.contrib.auth.backends.ModelBackend',
]


ROOT_URLCONF = "casamart.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "casamart.wsgi.application"
ASGI_APPLICATION = 'casamart.routing.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases



# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CSRF_TRUSTED_ORIGINS = ['https://cassamart.up.railway.app', "http://localhost:8000"]


SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ["Bearer"],
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(hours=6),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(weeks=12)
}


DATABASE_URL = "postgresql://postgres:5b6c5DADcfe6bcbac15EB25bbcc3egfg@viaduct.proxy.rlwy.net:55046/railway"


DATABASES = {
    "default": dj_database_url.config(default=DATABASE_URL, conn_max_age=1800),
}

# DATABASES = {
#     "default": {
#         "NAME": BASE_DIR / "db.sqlite3",
#         "ENGINE": "django.db.backends.sqlite3",
#     }
# }



CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    },
}


LOGGING = {
    'version': 1,
    # The version number of our log
    'disable_existing_loggers': False,
    # django uses some of its own loggers for internal operations. In case you want to disable them just replace the False above with true.
    # A handler for WARNING. It is basically writing the WARNING messages into a file called WARNING.log
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'warning.log',
        },
    },
    # A logger for WARNING which has a handler called 'file'. A logger can have multiple handler
    'loggers': {
        # notice the blank '', Usually you would put built in loggers like django or root here based on your needs
        '': {
            'handlers': ['file'],  # notice how file variable is called in handler which has been defined above
            'level': 'WARNING',
            'propagate': True,
        },
    },
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # "rest_framework.authentication.SessionAuthentication",
    ],
    'DEFAULT_PERMISSION_CLASSES ': [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}

PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_PUBLIC = os.getenv("PAYSTACK_PUBLIC_KEY")

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST = 'casamart.com.ng'
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

PaystackConfig.SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PaystackConfig.PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")
FIREBASE_ADMIN_CREDENTIALS_FILE = os.getenv("FIREBASE_ADMIN_CREDENTIALS_FILE")

# print(PaystackConfig.SECRET_KEY)

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    api_environment_variable=os.getenv('CLOUDINARY_URL'),
    secure=True
)

# Cloudinary Configuration
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
    "API_ENVIRONMENT_VARIABLE" : os.getenv('CLOUDINARY_URL'),
    "Secure": True
}
print(CLOUDINARY_STORAGE)

# Use Cloudinary for media storage
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# You can keep using the local static files storage or configure Cloudinary for static files as well:
# STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'

MEDIA_URL = '/media/'  # This will automatically route through Cloudinary

