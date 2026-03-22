"""
Production settings for config project.
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

from .base import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# .env 로드
load_dotenv(BASE_DIR / ".env")


# =========================
# Core
# =========================
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set.")

DEBUG = True

ALLOWED_HOSTS = [
    "35.172.205.54",
    "yooncoin.com",
    "www.yooncoin.com",
    "127.0.0.1",
    "localhost",
]

# =========================
# Installed apps
# =========================
INSTALLED_APPS = [
    "arena.apps.ArenaConfig",
    "main.apps.MainConfig",
    "common.apps.CommonConfig",
    "user.apps.UserConfig",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",

    # allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
]

SITE_ID = int(os.getenv("SITE_ID", "1"))


# =========================
# Middleware
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================
# URLs / WSGI
# =========================
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"


# =========================
# Templates
# =========================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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


# =========================
# Database
# =========================
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set.")

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=True,
    )
}


# =========================
# Password validation
# =========================
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


# =========================
# Internationalization
# =========================
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"

USE_I18N = True
USE_TZ = True


# =========================
# Static / Media
# =========================
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# =========================
# Default PK
# =========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================
# Auth redirect
# =========================
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# =========================
# Authentication backends
# =========================
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


# =========================
# allauth
# =========================
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = True

SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}



# =========================
# LemonSqueezy
# =========================
LEMON_SQUEEZY_API_KEY = os.getenv("LEMONSQUEEZY_API_KEY", "")
LEMON_SQUEEZY_STORE_ID = os.getenv("LEMONSQUEEZY_STORE_ID", "")
LEMON_SQUEEZY_WEBHOOK_SECRET = os.getenv("LEMONSQUEEZY_WEBHOOK_SECRET", "")
LEMON_SQUEEZY_PRO_VARIANT_ID = os.getenv("LEMONSQUEEZY_PRO_VARIANT_ID", "")
LEMON_SQUEEZY_PRO_PLUS_VARIANT_ID = os.getenv("LEMONSQUEEZY_PRO_PLUS_VARIANT_ID", "")


# =========================
# Security (Production)
# =========================

CSRF_TRUSTED_ORIGINS = [
    "http://35.172.205.54",
    "http://yooncoin.com",
    "http://www.yooncoin.com",
    "https://yooncoin.com",
    "https://www.yooncoin.com",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False


# =========================
# Logging
# =========================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
}
