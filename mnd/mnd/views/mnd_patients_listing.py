import logging

from django.utils.translation import ugettext as _

from rdrf.views.patients_listing import (
    ColumnFullName, ColumnDateOfBirth,
    ColumnCodeField, ColumnDiagnosisProgress,
    ColumnGeneticDataMap, PatientsListingView
)

logger = logging.getLogger(__name__)


class MNDPatientsListingView(PatientsListingView):

    def get_columns(self):
        columns = [
            ColumnFullName(_("Patient"), "patients.can_see_full_name"),
            ColumnDateOfBirth(_("Date of Birth"), "patients.can_see_dob"),
            ColumnCodeField(_("Gender"), "patients.can_see_code_field"),
            ColumnDiagnosisProgress(_("Diagnosis Entry Progress"), "patients.can_see_diagnosis_progress"),
            ColumnGeneticDataMap(_("Genetic Data"), "patients.can_see_genetic_data_map"),
        ]
        return columns
