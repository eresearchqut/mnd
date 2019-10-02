from rest_framework import serializers
from rdrf.services.rest.serializers import PatientSerializer


class MNDPatientSerializer(PatientSerializer):
    first_visit = serializers.SerializerMethodField()

    def get_first_visit(self, obj):
        registries = obj.rdrf_registry.all()
        target_forms = [
            form_model
            for registry_model in registries
            for form_model in registry_model.forms
            if form_model.name.lower() == 'firstvisit'
        ]
        if not target_forms:
            return None
        form_model = target_forms[0]
        for section_model in form_model.section_models:
            for cde_model in section_model.cde_models:
                if cde_model.name.lower() == 'visit date':
                    try:
                        return obj.get_form_value(
                            form_model.registry.code,
                            form_model.name,
                            section_model.code,
                            cde_model.code,
                            section_model.allow_multiple
                        )
                    except KeyError:
                        return None
