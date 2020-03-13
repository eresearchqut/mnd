import logging
from ..models import CarerRegistration

from django.utils.functional import cached_property

logger = logging.getLogger(__name__)


class RegistrationFlags:

    def __init__(self, primary_carer, patient):
        self.primary_carer = primary_carer
        self.patient = patient

    @cached_property
    def can_activate(self):
        return CarerRegistration.objects.has_deactivated_carer(self.primary_carer, self.patient)

    @cached_property
    def can_deactivate(self):
        return CarerRegistration.objects.has_registered_carer(self.primary_carer, self.patient)

    @cached_property
    def has_expired_registration(self):
        return CarerRegistration.objects.has_expired_registration(self.primary_carer, self.patient)

    @cached_property
    def has_pending_registration(self):
        return CarerRegistration.objects.has_pending_registration(self.primary_carer, self.patient)

    @cached_property
    def is_carer_registered(self):
        return CarerRegistration.objects.is_carer_registered(self.primary_carer, self.patient)

    @cached_property
    def can_register(self):
        return not (
            self.has_pending_registration or self.can_deactivate or self.can_activate
        ) and self.primary_carer

    @cached_property
    def registration_allowed(self):
        registry = self.patient.rdrf_registry.first()
        if registry:
            return registry.carer_registration_allowed()
        return False
