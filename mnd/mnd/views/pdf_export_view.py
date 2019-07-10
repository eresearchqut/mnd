import logging
import os

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from registry.patients.models import Patient
from rdrf.models.definition.models import Registry

from ..pdf_exports.export import export_to_pdf

logger = logging.getLogger("registry_log")


@require_GET
@login_required
def pdf_export(request, registry_code, patient_id):
    registry = get_object_or_404(Registry, code=registry_code)
    patient = get_object_or_404(Patient, pk=patient_id)

    # TODO: might need further refinement, allow carer of patient, clinicians etc.
    if not (request.user.is_superuser or request.user == patient.user):
        return HttpResponseForbidden()

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
