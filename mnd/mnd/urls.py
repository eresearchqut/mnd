from django.conf.urls import include
from django.urls import re_path

from .views.mnd_landing_view import LandingView
from .views.pdf_export_view import pdf_export
from .views.mnd_patient_view import AddPatientView, PatientEditView
from .views.mnd_patients_listing import MNDPatientsListingView
from .views.carer_registration_view import CarerOperationsView, PatientCarerRegistrationView
from .views.mnd_registration_view import MNDRegistrationView
from mnd.integration.mims import mims_view
from rdrf.urls import urlpatterns as rdrf_urlpatterns

rdrf_urls = [p for p in rdrf_urlpatterns if not getattr(p, 'app_name', None) == 'api_urls']

urlpatterns = [
    # Any custom URLs go here before we include the TRRF urls
    re_path(r'^pdf/about_me/(?P<registry_code>\w+)/(?P<patient_id>\d+)/?$', pdf_export, name='about_me'),
    re_path(r'^(?P<registry_code>\w+)/patient/add/?$', AddPatientView.as_view(), name='patient_add'),
    re_path(r'^(?P<registry_code>\w+)/patient/(?P<patient_id>\d+)/edit$', PatientEditView.as_view(), name='patient_edit'),
    re_path(r'^patientslisting/?', MNDPatientsListingView.as_view(), name='patientslisting'),
    re_path(r'^patient_carer_registration/?$', PatientCarerRegistrationView.as_view(), name='patient_carer_registration'),
    re_path(r'^carer_operations/?$', CarerOperationsView.as_view(), name='carer_operations'),
    re_path(r'^(?P<registry_code>\w+)/carer_registration/?$', MNDRegistrationView.as_view(), name='carer_registration'),
    re_path(r'^api/v1/', include(('mnd.services.rest.urls.api_urls', 'api_urls'), namespace='v1')),
    re_path(r'^mims/product_search', mims_view.product_search, name='mims_product_search'),
    re_path(r'^mims/product_details', mims_view.product_details, name='mims_product_details'),
    re_path(r'^mims/cmi_details', mims_view.cmi_details, name='mims_cmi_details'),
    re_path(r'^$', LandingView.as_view(), name='landing'),
    re_path(r'', include(rdrf_urls)),
]
