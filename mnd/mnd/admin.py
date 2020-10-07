from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from mnd.models import DuplicatePatient, MIMSCmiCache, MIMSProductCache


class DuplicatePatientAdmin(admin.ModelAdmin):
    list_display = ("patient_link", "working_groups", "created_at", "created_by", "last_updated")
    list_filter = ("is_duplicate",)

    def patient_link(self, obj):
        patient_url = reverse("patient_edit", kwargs={
            "registry_code": obj.patient.rdrf_registry.first().code,
            "patient_id": obj.patient.id,
        })
        return mark_safe(f"<a href='{patient_url}'>{obj.patient.display_name}</a>")
    patient_link.short_description = "Patient"

    def working_groups(self, obj):
        return obj.patient.working_groups_display

    def created_at(self, obj):
        return obj.patient.created_at

    def created_by(self, obj):
        return obj.patient.created_by

    def last_updated(self, obj):
        return obj.patient.last_updated_overall_at


class MIMSProductCacheAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'created_at')
    list_filter = ('created_at', )
    actions = ['delete_selected']


class MIMSCmiCacheAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'product_name', 'cmi_id', 'has_link', 'cmi_link')
    list_filter = ('cmi_id', 'has_link')
    actions = ['delete_selected']


admin.site.register(DuplicatePatient, DuplicatePatientAdmin)
admin.site.register(MIMSProductCache, MIMSProductCacheAdmin)
admin.site.register(MIMSCmiCache, MIMSCmiCacheAdmin)
