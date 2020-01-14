from django.utils.translation import ugettext as _
from django.utils.formats import date_format

from rdrf.views.patients_listing import (
    Column,
    ColumnCodeField,
    ColumnContextMenu,
    ColumnDateOfBirth,
    ColumnDiagnosisProgress,
    ColumnFullName,
    PatientsListingView
)


class MNDPatientsListingView(PatientsListingView):

    def get_columns(self):
        columns = [
            ColumnFullName(_("Patient"), "patients.can_see_full_name"),
            ColumnDateOfBirth(_("Date of Birth"), "patients.can_see_dob"),
            ColumnCodeField(_("Gender"), "patients.can_see_code_field"),
            ColumnDiagnosisProgress(_("Overall Form Progress"), "patients.can_see_diagnosis_progress"),
            ColumnDateLastUpdated(_("Date Last Updated"), "patients.can_see_last_updated_at"),
            ColumnContextMenu(_("Modules"), "patients.can_see_data_modules"),
        ]
        return columns


class ColumnDateLastUpdated(Column):
    field = "last_updated_overall_at"

    def fmt(self, val):
        return date_format(val) if val is not None else ""
