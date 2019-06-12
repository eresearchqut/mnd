from pypdftk import fill_form
import os

from .pdf_exports.about_me import get_pdf_template, generate_pdf_form_fields

_CURRENT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TEMPLATE_PATH = f"{_CURRENT_PATH}/mnd/templates/pdf_export/"


def export_to_pdf(patient, patient_address):
    return fill_form(
        get_pdf_template(_TEMPLATE_PATH),
        generate_pdf_form_fields(patient, patient_address),
        flatten=False
    )
