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
from registry.patients.models import LivingStates


class MNDPatientsListingView(PatientsListingView):

    def get_template(self):
        if not self.registries:
            return super().get_template()
        return 'rdrf_cdes/mnd_patients_listing.html'

    def build_context(self):
        context = super().build_context()
        context['living_status_preselect_value'] = LivingStates.ALIVE
        return context

    def set_parameters(self, request):
        super().set_parameters(request)

        valid_living_states = {val for val, _ in LivingStates.CHOICES}
        living_status = request.POST.get("searchPanes[living_status][0]")
        self.living_status_filter = living_status if living_status in valid_living_states else None

    def get_columns(self):
        columns = [
            ColumnFullName(_("Patient"), "patients.can_see_full_name"),
            ColumnDateOfBirth(_("Date of Birth"), "patients.can_see_dob"),
            ColumnCodeField(_("Gender"), "patients.can_see_code_field"),
            ColumnDiagnosisProgress(_("Overall Form Progress"), "patients.can_see_diagnosis_progress"),
            ColumnDateLastUpdated(_("Date Last Updated"), "patients.can_see_last_updated_at"),
            ColumnLivingStatus(_("Living Status"), "patients.can_see_living_status"),
            ColumnContextMenu(_("Modules"), "patients.can_see_data_modules"),
        ]
        return columns

    def apply_filters(self):
        super().apply_filters()
        if self.living_status_filter:
            self.patients = self.patients.filter(living_status=self.living_status_filter)

        def choice_to_option(value, label):
            return dict(
                label=str(label),  # enforcing translation of gettext_lazy label
                value=value,
                total=self.patients_base.filter(living_status=value).count(),
                count=self.patients.filter(living_status=value).count())

        self.searchPanesOptions = {
            "living_status": [choice_to_option(*x) for x in LivingStates.CHOICES]
        }


class ColumnDateLastUpdated(Column):
    field = "last_updated_overall_at"

    def fmt(self, val):
        return date_format(val) if val is not None else ""


class ColumnLivingStatus(Column):
    field = "living_status"
    sort_fields = ["living_status"]
    visible = False
