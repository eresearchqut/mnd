from rdrf.services.rest.views.api_views import PatientDetail
from ..serializers import MNDPatientSerializer


class MNDPatientDetail(PatientDetail):
    serializer_class = MNDPatientSerializer
