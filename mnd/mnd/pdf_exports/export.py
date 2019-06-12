from pypdftk import fill_form

from .about_me import get_pdf_template, generate_pdf_form_fields


def export_to_pdf(patient, patient_address):
    return fill_form(
        get_pdf_template(),
        generate_pdf_form_fields(patient, patient_address),
        flatten=False
    )
