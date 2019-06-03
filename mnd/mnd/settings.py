# flake8: noqa
import os

from rdrf.settings import *
import mnd


FALLBACK_REGISTRY_CODE = "mnd"
LOCALE_PATHS = env.getlist("locale_paths", ['/data/translations/locale'])

# Adding this project's app first, so that its templates overrides base templates
INSTALLED_APPS = [
    FALLBACK_REGISTRY_CODE,
] + INSTALLED_APPS

ROOT_URLCONF = '%s.urls' % FALLBACK_REGISTRY_CODE

SEND_ACTIVATION_EMAIL = False

PROJECT_TITLE = env.get("project_title", "MND")
PROJECT_TITLE_LINK = "login_router"

# Registration customisation (if any) goes here
# REGISTRATION_CLASS = "mnd.custom_registration.CustomRegistration"

VERSION = env.get('app_version', '%s (mnd)' % mnd.VERSION)
