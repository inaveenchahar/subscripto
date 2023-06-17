from .common import *  # noqa
from .common import env

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres:///subscripto_app",
    ),
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
