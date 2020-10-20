import logging

from django.core.exceptions import PermissionDenied

from rdrf.models.definition.models import RegistryForm
from rdrf.security.security_checks import get_object_or_permission_denied
from rdrf.views.form_view import FormView

from registry.patients.models import Patient

logger = logging.getLogger(__name__)


class MNDFormView(FormView):
    def registry_permissions_check(self, request, registry_code, form_id, patient_id, context_id):
        if request.user.is_clinician:
            form = get_object_or_permission_denied(RegistryForm, pk=form_id)
            patient = get_object_or_permission_denied(Patient, pk=patient_id)

            # TODO: Use upcoming patient-clinician connection feature
            if "patient-reported" in form.tags and patient.clinician != request.user:
                raise PermissionDenied("You must be set as the patient's clinician to access this form")
