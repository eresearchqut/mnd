from io import BytesIO
import logging

from django.http import FileResponse
from django.views.generic.base import View

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from registry.patients.models import Patient, PatientAddress

from .pdf_export import export_to_pdf

logger = logging.getLogger("registry_log")


class LoginRequiredMixin(object):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class PDFExportView(LoginRequiredMixin, View):

    def get(self, request, patient_id):
        if request.user.is_authenticated:
            patient = get_object_or_404(Patient, pk=patient_id)
            patient_address = PatientAddress.objects.filter(patient=patient).first()

            result_pdf_path = export_to_pdf(patient, patient_address)
            with open(result_pdf_path, 'rb') as f:
                file = BytesIO(f.read())
                return FileResponse(file, as_attachment=True, filename='pdf_export.pdf')
