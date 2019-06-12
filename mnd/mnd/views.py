from io import BytesIO
import logging

from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from registry.patients.models import Patient, PatientAddress

from .pdf_exports.export import export_to_pdf

logger = logging.getLogger("registry_log")


def user_is_patient_or_superuser(user):
    # TODO: what is the relation between patient and user ?
    return user.is_superuser


@login_required
@require_http_methods(['GET'])
@user_passes_test(user_is_patient_or_superuser)
def pdf_export(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    patient_address = PatientAddress.objects.filter(patient=patient).first()

    result_pdf_path = export_to_pdf(patient, patient_address)
    with open(result_pdf_path, 'rb') as f:
        file = BytesIO(f.read())
        return FileResponse(file, as_attachment=True, filename='pdf_export.pdf')
