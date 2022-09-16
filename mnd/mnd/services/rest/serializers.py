import logging

from rest_framework import serializers
from rdrf.services.rest.serializers import PatientSerializer

from rdrf.models.definition.models import RegistryForm, RDRFContext, ContextFormGroup

logger = logging.getLogger(__name__)


class MNDPatientSerializer(PatientSerializer):
    first_visit = serializers.SerializerMethodField()

    def get_first_visit(self, obj):
        registries = obj.rdrf_registry.all()

        form_model = RegistryForm.objects.filter(registry__in=registries, name__iexact='firstvisit').first()  # Yuck

        if not form_model:
            return None

        registry = form_model.registry
        context_form_groups = ContextFormGroup.objects.filter(items__registry_form=form_model)  # Yuck

        cde_lookup_codes = ['mndVDate', 'mndOnset']
        cde_lookups = {cde.code: (form_model.name, section.code, cde.code)
                       for section in form_model.section_models
                       for cde in section.cde_models
                       if cde.code in cde_lookup_codes}

        contexts = RDRFContext.objects.get_for_patient(obj, registry).filter(context_form_group__in=context_form_groups)

        for context in contexts:
            lookup_values = {key: obj.get_form_value(registry.code,
                                                     form_name,
                                                     section_code,
                                                     cde_code,
                                                     context_id=context.id)
                             for key, (form_name, section_code, cde_code) in cde_lookups.items()}

            # If we found values for any of the lookups, then don't look any further
            # This assumes all lookup values are in the one context (this may be a bad assumption)
            if any(lookup_values.values()):
                return lookup_values
