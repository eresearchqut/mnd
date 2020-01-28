from collections import OrderedDict
import uuid

from django.forms import CharField
from django.forms import ValidationError
from django.utils.translation import gettext as _
from django.utils import timezone

from registration.forms import RegistrationForm
from rdrf.forms.registration_forms import PatientRegistrationForm

from mnd.registry.patients.mnd_admin_forms import (
    PatientInsuranceRegistrationForm,
    PreferredContactForm,
    PrimaryCarerRegistrationForm
)

from ..models import CarerRegistration


class MNDRegistrationForm(PatientRegistrationForm):
    phone_number = None



class MNDCarerRegistrationForm(RegistrationForm):
    placeholders = {
        'username': _("Username"),
        'password1': _("Password"),
        'password2': _("Repeat Password"),
        'token': _("Registration token")
    }

    password_fields = ['password1', 'password2']

    token = CharField(required=True, min_length=36, max_length=36)
    registry_code = CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_fields()

    def setup_fields(self):
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = self.placeholders.get(field, '')
            if field in self.password_fields:
                self.fields[field].widget.render_value = True

    def clean_token(self):
        token = self.cleaned_data['token']
        if not CarerRegistration.objects.filter(
            token=token, status=CarerRegistration.CREATED, expires_on__gte=timezone.now()
        ).exists():
            raise ValidationError(_("Invalid token !"))
        try:
            uid_token = uuid.UUID(token)
        except ValueError:
            raise ValidationError(_("Invalid token format !"))
        return uid_token
