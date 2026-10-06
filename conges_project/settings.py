"""
Paramètres Django pour le projet gestion_conges.

Fonctionne tel quel en local (SQLite, DEBUG actif) et s'adapte
automatiquement à Render en production dès que les variables
d'environnement SECRET_KEY / DATABASE_URL / RENDER sont présentes.
"""
import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------
# Sécurité
# --------------------------------------------------------------------
# En local : valeur par défaut (sans danger, on ne déploie jamais avec).
# En production (Render) : définis SECRET_KEY dans les variables d'env.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-remplace-moi-avant-la-production-0123456789',
)

# DEBUG=True seulement si la variable d'env DEBUG vaut explicitement "True".
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = []
allowed_hosts_env = os.environ.get('ALLOWED_HOSTS')
if allowed_hosts_env:
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]
elif DEBUG:
    ALLOWED_HOSTS = ['*']

# Render fournit automatiquement le nom d'hôte externe du service.
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = []
csrf_trusted_env = os.environ.get('CSRF_TRUSTED_ORIGINS')
if csrf_trusted_env:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in csrf_trusted_env.split(',') if o.strip()]
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'conges',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'conges_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'conges_project.wsgi.application'

# --------------------------------------------------------------------
# Base de données
# --------------------------------------------------------------------
# Local : SQLite (aucune configuration requise).
# Render : Postgres via la variable d'environnement DATABASE_URL,
# injectée automatiquement quand la base est reliée au service.
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'Africa/Abidjan'

USE_I18N = True

USE_TZ = True

# --------------------------------------------------------------------
# Fichiers statiques (servis directement par WhiteNoise sur Render,
# pas besoin d'un serveur web séparé).
# --------------------------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'conges' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'conges:employe-list'
LOGOUT_REDIRECT_URL = 'conges:employe-list'

# Droit légal par défaut en Côte d'Ivoire : 2,2 jours ouvrables par mois de
# service effectif (soit 26,4 jours/an). Modifiable par employé dans sa fiche.
DROIT_JOURS_PAR_MOIS_DEFAUT = 2.2

# Derrière le proxy TLS de Render.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
