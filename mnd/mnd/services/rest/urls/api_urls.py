from django.urls import re_path
from rdrf.services.rest.urls import api_urls
from ..views import api_views as mnd_api_views


urlpatterns = [
    re_path(r'registries/(?P<registry_code>\w+)/patients/(?P<pk>\d+)/$',
            mnd_api_views.MNDPatientDetail.as_view(), name='patient-detail'),
] + api_urls.urlpatterns
