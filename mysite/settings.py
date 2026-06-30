"""
Django settings for mysite project.
"""

from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

# ===== CHAVE SECRETA =====
# Use variável de ambiente em produção
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-tl!)oyd!7(bud1h40uc-yf=gvxlqe@87bmdx-d1w8gkmwe!fi_')

# ===== DEBUG =====
# Desativa DEBUG em produção
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ===== ALLOWED_HOSTS =====
# Detecta se está no Render
IS_RENDER = 'RENDER' in os.environ

# Hosts permitidos
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'testserver',
]

# Adiciona hosts do Render se estiver na plataforma
if IS_RENDER:
    # Adiciona o hostname específico
    render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if render_hostname:
        ALLOWED_HOSTS.append(render_hostname)
    # Permite todos os subdomínios do Render
    ALLOWED_HOSTS.append('.onrender.com')
    
    # Permite qualquer host se DEBUG=False (não recomendado, mas útil)
    # ALLOWED_HOSTS = ['*']

# Se estiver em desenvolvimento, adicione hosts extras
if DEBUG:
    ALLOWED_HOSTS.extend([
        'localhost',
        '127.0.0.1',
        '0.0.0.0',  # Para testes locais
        'testserver',
    ])

# ===== Application definition =====
INSTALLED_APPS = [
    "polls.apps.PollsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'rest_framework',      # Django REST Framework
    'corsheaders',         # CORS headers
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Deve vir no topo
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

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

WSGI_APPLICATION = 'mysite.wsgi.application'

# ===== DATABASE =====
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ===== PASSWORD VALIDATION =====
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===== INTERNATIONALIZATION =====
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ===== STATIC FILES =====
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ===== DEFAULT PRIMARY KEY =====
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===== CORS CONFIGURATION =====
# Configuração para o Render
if IS_RENDER:
    # Em produção, lista específica de origens permitidas
    CORS_ALLOWED_ORIGINS = [
        'https://capiquest-front-v2.onrender.com',  # Frontend em produção
        'https://capiquest-back-v2.onrender.com',   # Backend em produção
        'http://localhost:3000',
        'http://localhost:8000',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:8000',
    ]
    # Em produção, NUNCA use CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_ALL_ORIGINS = False
else:
    # Em desenvolvimento, permite qualquer origem para facilitar
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    CORS_ALLOW_ALL_ORIGINS = True  # Apenas para desenvolvimento

# Configurações adicionais de CORS (opcional)
CORS_ALLOW_CREDENTIALS = True  # Permite envio de cookies/credenciais
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
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

# ===== REST FRAMEWORK =====
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Permite qualquer um (apenas para teste)
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Interface web da API
    ],
}

# ===== CSRF CONFIGURATION =====
# Configurações para o Render
CSRF_TRUSTED_ORIGINS = [
    'https://capiquest-back-v2.onrender.com',
    'https://capiquest-front-v2.onrender.com',
    'http://localhost:3000',
    'http://localhost:8000',
]

if IS_RENDER:
    # Adiciona os hosts do Render
    render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if render_hostname:
        CSRF_TRUSTED_ORIGINS.append(f'https://{render_hostname}')