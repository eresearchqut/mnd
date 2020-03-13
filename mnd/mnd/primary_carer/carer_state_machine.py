import logging

from rdrf.events.events import EventType

from .registration_flags import RegistrationFlags
from .carer_operations import CarerOperations


logger = logging.getLogger(__name__)


class CarerState:
    TOKEN_ALREADY_GENERATED = 'token_already_generated'
    INVITED = 'carer_invite'
    DEACTIVATED = 'carer_deactivated'
    ACTIVATED = 'carer_activated'
    RE_INVITED = 'carer_reinvited'
    REGISTRATION_DISABLED = 'carer_registration_disabled'
    CARER_NOT_SET = 'carer_not_set_for_patient'


class State:

    def __init__(self, carer, patient):
        self.carer = carer
        self.patient = patient
        self.state = None

    def next_state(self):
        return self

    def template(self):
        raise NotImplementedError()

    def process_action(self, request, display_only=False):
        return CarerOperations(request, self).nop()


class CarerInvite(State):

    def __init__(self, carer, patient):
        super().__init__(carer, patient)
        self.state = CarerState.INVITED

    def next_state(self):
        rf = RegistrationFlags(self.carer, self.patient)
        if rf.has_pending_registration:
            return CarerTokenGenerated(self.carer, self.patient)
        else:
            return CarerDeactivate(self.carer, self.patient)

    def template(self):
        return "registration/carer_invite.html"

    def process_action(self, request, display_only=False):
        if display_only:
            return CarerOperations(request, self).nop()
        return CarerOperations(request, self).register_carer()


class CarerTokenGenerated(State):

    def __init__(self, carer, patient):
        super().__init__(carer, patient)
        self.state = CarerState.TOKEN_ALREADY_GENERATED

    def template(self):
        return "registration/carer_token_generated.html"

    def process_action(self, request, display_only=False):
        if display_only:
            return CarerOperations(request, self).nop()
        # resend invite is the same as registering
        return CarerOperations(request, self).register_carer()


class CarerRegistrationDisabled(State):

    def __init__(self, carer, patient):
        super().__init__(carer, patient)
        self.state = CarerState.REGISTRATION_DISABLED

    def template(self):
        return "registration/carer_registration_disabled.html"


class CarerNotSetForPatient(State):

    def __init__(self, carer, patient):
        super().__init__(carer, patient)
        self.state = CarerState.CARER_NOT_SET

    def template(self):
        return "registration/carer_not_set.html"


class CarerReInvite(State):

    def __init__(self, carer, patient):
        super().__init__(carer, patient)
        self.state = CarerState.RE_INVITED

    def template(self):
        return "registration/carer_reinvite.html"

    def next_state(self):
        return CarerTokenGenerated(self.carer, self.patient)

    def process_action(self, request, display_only=False):
        if display_only:
            return CarerOperations(request, self).nop()
        return CarerOperations(request, self).register_carer()


class CarerDeactivate(State):

    def __init__(self, carer, patient):
        super().__init__(carer, patient)
        self.state = CarerState.DEACTIVATED

    def next_state(self):
        return CarerActivate(self.carer, self.patient)

    def template(self):
        return "registration/carer_deactivate.html"

    def process_action(self, request, display_only=False):
        if display_only:
            return CarerOperations(request, self).nop(event_type=EventType.CARER_DEACTIVATED)
        return CarerOperations(request, self).deactivate_carer()


class CarerActivate(State):

    def __init__(self, carer, patient):
        super().__init__(carer, patient)
        self.state = CarerState.ACTIVATED

    def next_state(self):
        return CarerDeactivate(self.carer, self.patient)

    def template(self):
        return "registration/carer_activate.html"

    def process_action(self, request, display_only=False):
        if display_only:
            return CarerOperations(request, self).nop(event_type=EventType.CARER_ACTIVATED)
        return CarerOperations(request, self).activate_carer()


def get_current_state(primary_carer, patient):
    rf = RegistrationFlags(primary_carer, patient)
    registration_enabled = rf.registration_allowed
    if not registration_enabled:
        return CarerRegistrationDisabled(primary_carer, patient)
    if not primary_carer:
        return CarerNotSetForPatient(primary_carer, patient)
    if rf.has_pending_registration:
        return CarerTokenGenerated(primary_carer, patient)
    else:
        if rf.has_expired_registration:
            return CarerReInvite(primary_carer, patient)
        if rf.can_register:
            return CarerInvite(primary_carer, patient)
        if rf.can_deactivate:
            return CarerDeactivate(primary_carer, patient)
        if rf.can_activate:
            return CarerActivate(primary_carer, patient)


def get_carer_state(primary_carer, patient):
    rf = RegistrationFlags(primary_carer, patient)
    registration_enabled = rf.registration_allowed
    if not registration_enabled:
        return CarerRegistrationDisabled(primary_carer, patient)
    if rf.can_deactivate:
        return CarerDeactivate(primary_carer, patient)
