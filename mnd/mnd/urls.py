from django.conf.urls import include
from django.urls import re_path

from .views.pdf_export_view import pdf_export
from .views.mnd_patient_view import AddPatientView, PatientEditView
from .views.mnd_patients_listing import MNDPatientsListingView

urlpatterns = [
    # Any custom URLs go here before we include the TRRF urls
    re_path(r"^pdf/about_me/(?P<registry_code>\w+)/(?P<patient_id>\d+)/?$", pdf_export, name='about_me'),
    re_path(r"^(?P<registry_code>\w+)/patient/add/?$", AddPatientView.as_view(), name='patient_add'),
    re_path(r"^(?P<registry_code>\w+)/patient/(?P<patient_id>\d+)/edit$", PatientEditView.as_view(), name='patient_edit'),
    re_path(r'^patientslisting/?', MNDPatientsListingView.as_view(), name="patientslisting"),
    re_path(r'', include('rdrf.urls')),
]
