# flake8: noqa
import os

from rdrf.settings import *
import mnd
from mnd.security.url_whitelist import MND_WHITELISTED_URLS


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

PROJECT_LOGO = env.get("project_logo", "images/mnd/MiND_Logo_orange.png")

# Registration customisation (if any) goes here
# REGISTRATION_CLASS = "mnd.custom_registration.CustomRegistration"

VERSION = env.get('app_version', '%s (mnd)' % mnd.VERSION)

PDF_TEMPLATES_PATH = f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/mnd/templates/pdf_export"

# Content Security Policy
CSP_CHILD_SRC = ["'self'", "https://www.youtube.com"]

# Currently using registration from base TRRF as-is, but keeping these for future reference
#
# REGISTRATION_FORM = 'mnd.forms.mnd_registration_form.MNDRegistrationForm'
# REGISTRATION_CLASS = 'mnd.registry.groups.registration.mnd_registration.MNDRegistration'

STRONGHOLD_PUBLIC_URLS += (
    r'/(?P<registry_code>\w+)/carer_registration/?$',
)

SECURITY_WHITELISTED_URLS += MND_WHITELISTED_URLS

MIMS_API_KEY = env.get('mims_api_key', '')
MIMS_CLIENT_ID = env.get('mims_client_id', '')
MIMS_CLIENT_SECRET = env.get('mims_client_secret', '')
MIMS_ENDPOINT = env.get('mims_endpoint', '')
EXTRA_WIDGETS = 'mnd.forms.widgets.mnd_widgets'

REGISTRY_FORM_TAGS = (("patient-reported", "Patient-reported form"),)

ACCOUNT_ACTIVATION_DAYS = 90

# Reports settings
REPORT_PATIENT_CLASS = 'mnd.report.schema.MNDPatientType'
REPORT_CONFIGURATION = 'mnd.report.report_configuration.REPORT_CONFIGURATION'