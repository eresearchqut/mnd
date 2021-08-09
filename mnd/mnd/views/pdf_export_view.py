import logging
import os

from django.core.exceptions import PermissionDenied
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_GET

from registry.patients.models import Patient
from rdrf.models.definition.models import Registry
from rdrf.security.security_checks import security_check_user_patient, get_object_or_permission_denied

from ..pdf_exports.export import export_to_pdf

logger = logging.getLogger("registry_log")


@require_GET
def pdf_export(request, registry_code, patient_id):
    registry = get_object_or_404(Registry, code=registry_code)
    patient = get_object_or_permission_denied(Patient, pk=patient_id)

    security_check_user_patient(request.user, patient)
    if request.user.is_clinician and request.user not in patient.registered_clinicians.all():
        raise PermissionDenied(_("You must be registered as the patients clinician to access the pdf"))

    filename = f'About Me MND - {patient.display_name}.pdf'

    local_pdf_filename = export_to_pdf(registry, patient)
    return AutoCleaningFileResponse(local_pdf_filename, as_attachment=True, filename=filename)


class AutoCleaningFileResponse(FileResponse):
    def __init__(self, local_filename, *args, **kwargs):
        self.local_filename = local_filename
        super().__init__(open(local_filename, 'rb'), *args, **kwargs)

    def close(self):
        super().close()
        os.remove(self.local_filename)
