"""
Django settings for jobapp project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import cloudinary.api

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-n%d&ul84it5m&(pr!=y#$(njzilwu2(3*-3414*#4&aw4*#q6#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'jobs.apps.JobsConfig',
    'ckeditor',
    'ckeditor_uploader',
    'rest_framework',
    'drf_yasg',
    'cloudinary',
    'oauth2_provider',
    'corsheaders',
    'debug_toolbar',
    'rest_framework_simplejwt.token_blacklist',
    # 'chartjs',
    # 'admincharts',

    # 'jet',
    # 'rest_framework.authtoken',  # Thêm dòng này

]
# CHART_CONFIG = {
#     'use_cache': True,
#     'cache_timeout': 60 * 15,  # 15 minutes
# }

AUTH_USER_MODEL = 'jobs.User'
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',

    )
}
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]
CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'jobapp.urls'
CKEDITOR_UPLOAD_PATH = "images/ckeditor/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',  # Chỉ định thanh công cụ sử dụng (xem thêm phần cấu hình tùy chỉnh CKEditor)
        'height': 300,  # Chiều cao của trình soạn thảo văn bản
        'width': 800,  # Chiều rộng của trình soạn thảo văn bản
    },
}
MEDIA_ROOT = '%s/jobs/static/' % BASE_DIR
# OAUTH2_PROVIDER = { 'OAUTH2_BACKEND_CLASS': 'oauth2_provider.oauth2_backends.JSONOAuthLibCore' }


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

WSGI_APPLICATION = 'jobapp.wsgi.application'

cloudinary.config(
    cloud_name="debpu6bvf",
    api_key="917416417964682",
    api_secret="fQU8qnEQ5kUSH1sjV64ZsA9Esk4"
)

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# import pymysql
#
# pymysql.install_as_MySQLdb()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jobfinding',
        'USER': 'root',
        'PASSWORD': '8318278',
        'HOST': ''  # mặc định localhost
    }
}
ALLOWED_HOSTS = ['localhost', '127.0.0.1', ]

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
#
#
#
# #send mail config
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'travel.agency.ou.management@gmail.com'
# EMAIL_HOST_PASSWORD = 'dvbrqvpkhcooagil'
# EMAIL_PORT = 587
#
# #auth-social config
# GOOGLE_CLIENT_ID = '223587602728-cgo32g1e3tbkabc4hdhllf6oq79l9cn2.apps.googleusercontent.com'
# GOOGLE_CLIENT_SECRET = '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'
# SOCIAL_SECRET = '@gbklknspajdoughwblwdoiushuolnjhsuyu5w#@#%$'

# # //
# JET_SIDE_MENU_COMPACT = True  # Hiển thị menu bên gọn gàng hơn
# JET_CHANGE_LIST_FILTER = True  # Sử dụng bộ lọc tùy chỉnh
# JET_INDEX_DASHBOARD = 'jobs.dashboard.CustomIndexDashboard'  # Tạo trang dashboard tùy chỉnh


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
client_id = 'mF52gu9Skf7q6DzwbtpgUhs7owCwCF3JVGEBCNZ3'
client_secret = '9XpvEAyOckjClVgVfKzg8nj4B8MHJtsSo01wOz94ul2ZhWth4yBuLdTwcK7G8b0tcRsbFjTkwvWE5CRe5c0reNNqAwOD25trAh0tdfQ8rPPGMAhbwgfT5BX904cJQKN7'
