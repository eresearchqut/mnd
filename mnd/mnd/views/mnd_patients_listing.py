from django.utils.translation import ugettext as _
from django.utils.formats import date_format, time_format

from rdrf.views.patients_listing import (
    Column,
    ColumnFullName, ColumnDateOfBirth,
    ColumnCodeField, ColumnDiagnosisProgress,
    ColumnGeneticDataMap, PatientsListingView
)


class MNDPatientsListingView(PatientsListingView):

    def get_columns(self):
        columns = [
            ColumnFullName(_("Patient"), "patients.can_see_full_name"),
            ColumnDateOfBirth(_("Date of Birth"), "patients.can_see_dob"),
            ColumnCodeField(_("Gender"), "patients.can_see_code_field"),
            ColumnDiagnosisProgress(_("Diagnosis Entry Progress"), "patients.can_see_diagnosis_progress"),
            ColumnGeneticDataMap(_("Genetic Data"), "patients.can_see_genetic_data_map"),
            ColumnLastUpdated(_("Last updated"), "patients.can_see_dob")
        ]
        return columns


class ColumnLastUpdated(Column):
    field = "last_updated_overall_at"

    def fmt(self, val):
        return "{} {}".format(date_format(val), time_format(val)) if val is not None else ""
