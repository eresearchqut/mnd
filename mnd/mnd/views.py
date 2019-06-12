from io import BytesIO
import logging
import os

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from registry.patients.models import Patient
from rdrf.models.definition.models import Registry

from .pdf_exports.export import export_to_pdf

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

    result_pdf_path = export_to_pdf(registry, patient)
    with open(result_pdf_path, 'rb') as f:
        data = BytesIO(f.read())
    os.remove(result_pdf_path)
    return FileResponse(data, as_attachment=True, filename=filename)
